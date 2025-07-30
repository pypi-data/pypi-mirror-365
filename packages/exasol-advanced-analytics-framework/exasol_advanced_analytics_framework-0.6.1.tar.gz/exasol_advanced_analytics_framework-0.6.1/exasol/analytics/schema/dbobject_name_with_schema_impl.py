from typing import Optional

from typeguard import typechecked

from exasol.analytics.schema.dbobject_name_impl import DBObjectNameImpl
from exasol.analytics.schema.dbobject_name_with_schema import DBObjectNameWithSchema
from exasol.analytics.schema.exasol_identifier import qualified_name
from exasol.analytics.schema.schema_name import SchemaName
from exasol.analytics.utils.hash_generation_for_object import generate_hash_for_object
from exasol.analytics.utils.repr_generation_for_object import generate_repr_for_object


class DBObjectNameWithSchemaImpl(DBObjectNameImpl, DBObjectNameWithSchema):

    @typechecked
    def __init__(self, db_object_name: str, schema: Optional[SchemaName] = None):
        super().__init__(db_object_name)
        self._schema_name = schema

    @property
    def schema_name(self) -> Optional[SchemaName]:
        return self._schema_name

    @property
    def fully_qualified(self) -> str:
        return qualified_name(self._schema_name, self.quoted_name)

    def __repr__(self) -> str:
        return generate_repr_for_object(self)

    def __eq__(self, other) -> bool:
        return (
            type(other) == type(self)
            and self._name == other.name
            and self._schema_name == other.schema_name
        )

    def __hash__(self):
        return generate_hash_for_object(self)
