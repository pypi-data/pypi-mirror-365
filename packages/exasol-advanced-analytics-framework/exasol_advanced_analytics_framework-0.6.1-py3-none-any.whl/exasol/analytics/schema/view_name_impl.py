from typing import Optional

from typeguard import typechecked

from exasol.analytics.schema.schema_name import SchemaName
from exasol.analytics.schema.table_like_name_impl import TableLikeNameImpl
from exasol.analytics.schema.view_name import ViewName


class ViewNameImpl(TableLikeNameImpl, ViewName):

    @typechecked
    def __init__(self, view_name: str, schema: Optional[SchemaName] = None):
        super().__init__(view_name, schema)
