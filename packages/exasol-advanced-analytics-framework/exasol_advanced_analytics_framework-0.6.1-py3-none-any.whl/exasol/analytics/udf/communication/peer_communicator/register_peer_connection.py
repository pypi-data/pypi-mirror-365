from typing import Optional

import structlog
from structlog.typing import FilteringBoundLogger

from exasol.analytics.udf.communication import messages
from exasol.analytics.udf.communication.connection_info import ConnectionInfo
from exasol.analytics.udf.communication.peer import Peer
from exasol.analytics.udf.communication.peer_communicator.send_socket_factory import (
    SendSocketFactory,
)
from exasol.analytics.udf.communication.serialization import serialize_message
from exasol.analytics.udf.communication.socket_factory.abstract import Socket

LOGGER: FilteringBoundLogger = structlog.get_logger()


class RegisterPeerConnection:

    def __init__(
        self,
        predecessor: Optional[Peer],
        predecessor_send_socket_factory: Optional[SendSocketFactory],
        successor: Peer,
        successor_send_socket_factory: SendSocketFactory,
        my_connection_info: ConnectionInfo,
    ):
        self._logger = LOGGER.bind(
            successor=successor.model_dump(),
            predecessor=None if predecessor is None else predecessor.model_dump(),
            my_connection_info=my_connection_info.model_dump(),
        )
        self._successor = successor
        self._predecessor = predecessor
        self._my_connection_info = my_connection_info
        self._successor_socket = successor_send_socket_factory.create_send_socket()
        self._predecessor_socket: Optional[Socket] = None
        if predecessor_send_socket_factory is not None:
            self._predecessor_socket = (
                predecessor_send_socket_factory.create_send_socket()
            )

    @property
    def successor(self) -> Peer:
        return self._successor

    @property
    def predecessor(self) -> Optional[Peer]:
        return self._predecessor

    def forward(self, peer: Peer):
        self._logger.debug("forward", peer=peer.model_dump())
        message = messages.RegisterPeer(
            peer=peer, source=Peer(connection_info=self._my_connection_info)
        )
        serialized_message = serialize_message(message)
        self._successor_socket.send(serialized_message)

    def ack(self, peer: Peer):
        self._logger.debug("ack", peer=peer.model_dump())
        if self._predecessor_socket is not None:
            message = messages.AcknowledgeRegisterPeer(
                peer=peer, source=Peer(connection_info=self._my_connection_info)
            )
            serialized_message = serialize_message(message)
            self._predecessor_socket.send(serialized_message)

    def complete(self, peer: Peer):
        self._logger.debug("complete", peer=peer.model_dump())
        message = messages.RegisterPeerComplete(
            peer=peer, source=Peer(connection_info=self._my_connection_info)
        )
        serialized_message = serialize_message(message)
        self._successor_socket.send(serialized_message)

    def close(self):
        self._successor_socket.close(linger=10)
        if self._predecessor_socket is not None:
            self._predecessor_socket.close(linger=10)

    def __del__(self):
        self.close()
