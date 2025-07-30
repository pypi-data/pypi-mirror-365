import logging
import textwrap
from inspect import cleandoc
from typing import (
    Callable,
    Generic,
    List,
    Tuple,
    TypeVar,
    Union,
)

from exasol.analytics.query_handler.context.scope import ScopeQueryHandlerContext
from exasol.analytics.query_handler.context.top_level_query_handler_context import (
    ConnectionLookup,
    TopLevelQueryHandlerContext,
)
from exasol.analytics.query_handler.query.interface import Query
from exasol.analytics.query_handler.query.result.python_query_result import (
    PythonQueryResult,
)
from exasol.analytics.query_handler.query.select import SelectQueryWithColumnDefinition
from exasol.analytics.query_handler.query_handler import QueryHandler
from exasol.analytics.query_handler.result import (
    Continue,
    Finish,
)
from exasol.analytics.query_handler.udf.runner.state import QueryHandlerRunnerState
from exasol.analytics.sql_executor.interface import SQLExecutor
from exasol.analytics.utils.errors import UninitializedAttributeError

LOGGER = logging.getLogger(__file__)

ResultType = TypeVar("ResultType")
ParameterType = TypeVar("ParameterType")


class PythonQueryHandlerRunner(Generic[ParameterType, ResultType]):

    def __init__(
        self,
        sql_executor: SQLExecutor,
        top_level_query_handler_context: TopLevelQueryHandlerContext,
        parameter: ParameterType,
        query_handler_factory: Callable[
            [ParameterType, ScopeQueryHandlerContext],
            QueryHandler[ParameterType, ResultType],
        ],
    ):
        self._sql_executor = sql_executor
        query_handler = query_handler_factory(
            parameter, top_level_query_handler_context
        )
        self._state = QueryHandlerRunnerState(
            top_level_query_handler_context=top_level_query_handler_context,
            query_handler=query_handler,
            connection_lookup=None,
        )

    def run(self) -> ResultType:
        try:
            result = self._state.query_handler.start()
            while isinstance(result, Continue):
                result = self._handle_continue(result)
            if isinstance(result, Finish):
                self._handle_finish()
                return result.result
            else:
                raise RuntimeError(f"Unsupported result type {type(result)}")
        except Exception as e:
            try:
                self._handle_finish()
            except Exception as e1:
                LOGGER.exception("Caught exception during cleanup after an exception.")
            raise RuntimeError(
                f"Execution of query handler {self._state.query_handler} failed."
            ) from e

    def _handle_continue(self, result: Continue) -> Union[Continue, Finish[ResultType]]:
        self._release_and_create_query_handler_context_of_input_query()
        self._cleanup_query_handler_context()
        self._execute_queries(result.query_list)
        input_query_result = self._run_input_query(result)
        _result = self._state.query_handler.handle_query_result(input_query_result)
        return _result

    def _run_input_query(self, result: Continue) -> PythonQueryResult:
        input_query_view, input_query = self._wrap_return_query(result.input_query)
        self._sql_executor.execute(input_query_view)
        input_query_result_set = self._sql_executor.execute(input_query)
        if input_query_result_set.columns() != result.input_query.output_columns:
            raise RuntimeError(
                f"Specified columns {result.input_query.output_columns} of the input query "
                f"are not equal to the actual received columns {input_query_result_set.columns()}"
            )
        input_query_result_table = input_query_result_set.fetchall()
        input_query_result = PythonQueryResult(
            data=input_query_result_table, columns=result.input_query.output_columns
        )
        return input_query_result

    def _handle_finish(self):
        if self._state.input_query_query_handler_context is not None:
            self._state.input_query_query_handler_context.release()
        self._state.top_level_query_handler_context.release()
        self._cleanup_query_handler_context()

    def _cleanup_query_handler_context(self):
        cleanup_query_list = (
            self._state.top_level_query_handler_context.cleanup_released_object_proxies()
        )
        self._execute_queries(cleanup_query_list)

    def _execute_queries(self, queries: List[Query]):
        for query in queries:
            self._sql_executor.execute(query.query_string)

    def _release_and_create_query_handler_context_of_input_query(self):
        if self._state.input_query_query_handler_context is not None:
            self._state.input_query_query_handler_context.release()
        self._state.input_query_query_handler_context = (
            self._state.top_level_query_handler_context.get_child_query_handler_context()
        )

    def _wrap_return_query(
        self, input_query: SelectQueryWithColumnDefinition
    ) -> Tuple[str, str]:
        if self._state.input_query_query_handler_context is None:
            raise UninitializedAttributeError(
                "Current state's input query query handler context is not set."
            )
        temporary_view_name = (
            self._state.input_query_query_handler_context.get_temporary_view_name()
        )
        input_query_create_view_string = cleandoc(
            f"""
            CREATE OR REPLACE VIEW {temporary_view_name.fully_qualified} AS
            {input_query.query_string};
            """
        )
        full_qualified_columns = [
            col.name.fully_qualified for col in input_query.output_columns
        ]
        columns_str = ",\n".join(full_qualified_columns)
        input_query_string = cleandoc(
            f"""
            SELECT
            {textwrap.indent(columns_str, " " * 4)}
            FROM {temporary_view_name.fully_qualified};
            """
        )
        return input_query_create_view_string, input_query_string
