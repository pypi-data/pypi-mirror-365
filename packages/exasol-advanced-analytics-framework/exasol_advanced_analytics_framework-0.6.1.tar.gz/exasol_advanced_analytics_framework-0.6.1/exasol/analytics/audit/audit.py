import logging
import uuid
from typing import (
    Any,
    Iterator,
    cast,
)

from exasol.analytics.audit.columns import BaseAuditColumns
from exasol.analytics.query_handler.query.select import (
    AuditQuery,
    LogSpan,
    ModifyQuery,
    Query,
    SelectQueryWithColumnDefinition,
)
from exasol.analytics.schema import (
    Column,
    ColumnName,
    DBObjectName,
    DBObjectNameWithSchema,
    DbObjectType,
    DbOperationType,
    InsertStatement,
    SchemaName,
    Table,
    TableNameImpl,
)

LOG = logging.getLogger(__name__)


def base_column_values(
    attributes: dict[Column, Any],
    parent: LogSpan | None = None,
) -> dict[str, Any]:
    """
    Given a dict of columns and values and the optional parent LogSpan
    this function returns a dict with keys being only the names of the
    columns, optionally incuding the PARENT_LOG_SPAN_ID.
    """
    columns = dict(attributes)
    if parent:
        columns[BaseAuditColumns.PARENT_LOG_SPAN_ID] = str(parent.id)
    return {c.name.name: v for c, v in columns.items()}


def _generate_run_id():
    return uuid.uuid4()


class AuditTable(Table):
    def __init__(
        self,
        db_schema: str,
        table_name_prefix: str,
        additional_columns: list[Column] = [],
        run_id: uuid.UUID | None = None,
    ):
        run_id = run_id or _generate_run_id()
        LOG.debug(f"AuditTable: run_id = {run_id}")
        if not table_name_prefix:
            raise ValueError("table_name_prefix must not be empty")
        table_name = f"{table_name_prefix}_AUDIT_LOG"
        super().__init__(
            name=TableNameImpl(table_name, SchemaName(db_schema)),
            columns=(BaseAuditColumns.all + additional_columns),
        )
        self._column_names = [c.name for c in self.columns]
        self._run_id = run_id

    def augment(self, queries: Iterator[Query]) -> Iterator[Query]:
        """
        Process the specified queries and intermerge insert statements
        into the Audit Log if requested:

        * Queries not requesting any entry into the Audit Log are simply returned.

        * Instances of :class:`AuditQuery` are converted into insert
          statements into the Audit Log, optionally including custom
          audit_fields and a subquery (SelectQueryWithColumnDefinition)

        * Instances of :class:`ModifyQuery` requesting an entry into the Audit
          Log are wrapped into one insert statement before and one after. The
          actual modifying query in between remains unchanged.  The insert
          statements before and after record the timestamp and, if the
          ModifyQuery represents an INSERT operation, the number of rows in
          the modified table.
        """
        for query in queries:
            if not query.audit:
                yield query
            elif isinstance(query, AuditQuery):
                yield self._insert(query)
            elif isinstance(query, ModifyQuery):
                yield from self._wrap(query)
            else:
                raise TypeError(
                    f"Unexpected type {type(query).__name__}"
                    f' of query "{query.query_string}"'
                )

    def _insert(self, query: AuditQuery) -> Query:
        def log_span_fields(log_span: LogSpan | None):
            run_id = {BaseAuditColumns.RUN_ID: str(self._run_id)}
            if not log_span:
                return base_column_values(run_id)
            return base_column_values(
                run_id
                | {
                    BaseAuditColumns.LOG_SPAN_NAME: log_span.name,
                    BaseAuditColumns.LOG_SPAN_ID: str(log_span.id),
                },
                log_span.parent,
            )

        constants = query.audit_fields | log_span_fields(query.log_span)
        if not query.select_with_columns:
            return self._insert_statement(constants)

        alias = TableNameImpl("SUB_QUERY")
        subquery_columns = {
            c.name.name: ColumnName(c.name.name, alias)
            for c in query.select_with_columns.output_columns
        }
        return self._insert_statement(
            constants=constants,
            references=subquery_columns,
            suffix=f"FROM ({query.query_string}) as {alias.fully_qualified}",
        )

    def _wrap(self, query: ModifyQuery) -> Iterator[Query]:
        """
        Wrap the specified ModifyQuery it into 2 queries recording the
        state before and after the actual ModifyQuery.

        The state includes timestamps and optionally the number of rows of the
        modified table, in case the ModifyQuery indicates potential changes to the
        number of rows.
        """
        if query.db_operation_type != DbOperationType.INSERT:
            yield query
        else:
            yield from [
                self._count_rows(query, "Begin"),
                query,
                self._count_rows(query, "End"),
            ]

    def _count_rows(self, query: ModifyQuery, event_name: str) -> Query:
        """
        Create an SQL INSERT statement counting the rows of the table
        modified by ModifyQuery `query` and populate columns in the Audit
        Table marked with "+":

        + LOG_TIMESTAMP: BaseAuditColumns.values
        + SESSION_ID: BaseAuditColumns.values
        - RUN_ID
        + ROW_COUNT: subquery
        + LOG_SPAN_NAME: query.log_span
        + LOG_SPAN_ID: query.log_span
        + PARENT_LOG_SPAN_ID: query.log_span
        + EVENT_NAME: parameter event_name
        - EVENT_ATTRIBUTES
        + DB_OBJECT_TYPE: query.db_object_type: DbObjectType
        + DB_OBJECT_SCHEMA: query.db_object_name: DBObjectName
        + DB_OBJECT_NAME: query.db_object_name: DBObjectName
        - ERROR_MESSAGE
        """

        db_obj = query.db_object_name
        modify_query_fields = self._modify_query_fields(query, event_name)
        other_table = query.db_object_name.fully_qualified
        count_rows = base_column_values(
            {BaseAuditColumns.ROW_COUNT: f"(SELECT count(1) FROM {other_table})"}
        )
        return self._insert_statement(
            constants=(modify_query_fields | query.audit_fields),
            scalar_functions=count_rows,
        )

    def _modify_query_fields(
        self, query: ModifyQuery, event_name: str
    ) -> dict[str, Any]:
        def schema(db_obj: DBObjectName) -> str | None:
            if not isinstance(db_obj, DBObjectNameWithSchema):
                return None
            schema = cast(DBObjectNameWithSchema, db_obj).schema_name
            return schema.name if schema else None

        db_obj = query.db_object_name
        return base_column_values(
            {
                BaseAuditColumns.RUN_ID: str(self._run_id),
                BaseAuditColumns.LOG_SPAN_NAME: query.log_span.name,
                BaseAuditColumns.LOG_SPAN_ID: str(query.log_span.id),
                BaseAuditColumns.EVENT_NAME: event_name,
                BaseAuditColumns.DB_OBJECT_TYPE: query.db_object_type.name,
                BaseAuditColumns.DB_OBJECT_SCHEMA: schema(db_obj),
                BaseAuditColumns.DB_OBJECT_NAME: db_obj.name,
            },
            query.log_span.parent,
        )

    def _insert_statement(
        self,
        constants: dict[str, Any],
        scalar_functions: dict[str, Any] = {},
        references: dict[str, ColumnName] = {},
        suffix: str = "",
    ) -> Query:
        insert_statement = (
            InsertStatement(self._column_names, separator=",\n  ")
            .add_scalar_functions(BaseAuditColumns.values | scalar_functions)
            .add_constants(constants)
            .add_references(references)
        )
        space_suffix = f"\n{suffix}" if suffix else ""
        return ModifyQuery(
            query_string=(
                f"INSERT INTO {self.name.fully_qualified} (\n"
                f"  {insert_statement.columns}\n"
                ") SELECT\n"
                f"  {insert_statement.values}{space_suffix}"
            ),
            db_object_type=DbObjectType.TABLE,
            db_object_name=self.name,
            db_operation_type=DbOperationType.INSERT,
        )

    @property
    def create_query(self) -> ModifyQuery:
        return ModifyQuery(
            query_string=self.create_statement,
            db_object_type=DbObjectType.TABLE,
            db_object_name=self.name,
            db_operation_type=DbOperationType.CREATE_IF_NOT_EXISTS,
            audit=False,
        )
