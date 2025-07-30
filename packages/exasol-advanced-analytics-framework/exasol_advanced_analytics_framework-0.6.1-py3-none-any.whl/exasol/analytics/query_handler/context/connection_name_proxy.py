from exasol.analytics.query_handler.context.connection_name import (
    ConnectionName,
    ConnectionNameImpl,
)
from exasol.analytics.query_handler.context.proxy.db_object_name_proxy import (
    DBObjectNameProxy,
)
from exasol.analytics.query_handler.query.drop.connection import DropConnectionQuery
from exasol.analytics.query_handler.query.interface import Query


class ConnectionNameProxy(DBObjectNameProxy[ConnectionName], ConnectionName):

    @property
    def fully_qualified(self) -> str:
        return self.quoted_name

    def get_cleanup_query(self) -> Query:
        return DropConnectionQuery(self._db_object_name)

    def __init__(self, connection_name: ConnectionName, global_counter_value: int):
        super().__init__(connection_name, global_counter_value)
