from collections import deque
from typing import (
    Deque,
    List,
)

import structlog
from structlog.typing import FilteringBoundLogger

from exasol.analytics.udf.communication import messages
from exasol.analytics.udf.communication.connection_info import ConnectionInfo
from exasol.analytics.udf.communication.peer import Peer
from exasol.analytics.udf.communication.peer_communicator.background_listener_interface import (
    BackgroundListenerInterface,
)
from exasol.analytics.udf.communication.socket_factory.abstract import (
    Frame,
    SocketFactory,
)

LOGGER: FilteringBoundLogger = structlog.getLogger()


class FrontendPeerState:

    def __init__(
        self,
        my_connection_info: ConnectionInfo,
        socket_factory: SocketFactory,
        background_listener: BackgroundListenerInterface,
        peer: Peer,
    ):
        self._connection_is_closed = False
        self._received_messages: Deque[List[Frame]] = deque()
        self._background_listener = background_listener
        self._my_connection_info = my_connection_info
        self._peer = peer
        self._socket_factory = socket_factory
        self._connection_is_ready = False
        self._peer_register_forwarder_is_ready = False
        self._sequence_number = 0
        self._logger = LOGGER.bind(
            peer=peer.model_dump(), my_connection_info=my_connection_info.model_dump()
        )

    def _next_sequence_number(self):
        result = self._sequence_number
        self._sequence_number += 1
        return result

    def received_connection_is_ready(self):
        self._connection_is_ready = True

    def received_peer_register_forwarder_is_ready(self):
        self._peer_register_forwarder_is_ready = True

    def received_payload_message(
        self, message_obj: messages.Payload, frames: List[Frame]
    ):
        if message_obj.source != self._peer:
            raise RuntimeError(
                f"Received message from wrong peer. "
                f"Expected peer is {self._peer}, but got {message_obj.source}."
                f"Message was: {message_obj}"
            )
        self._received_messages.append(frames[1:])

    @property
    def peer_is_ready(self) -> bool:
        return self._connection_is_ready and self._peer_register_forwarder_is_ready

    def send(self, payload: List[Frame]):
        message = messages.Payload(
            source=Peer(connection_info=self._my_connection_info),
            destination=self._peer,
            sequence_number=self._next_sequence_number(),
        )
        self._logger.debug("send", message=message.model_dump())
        self._background_listener.send_payload(message=message, payload=payload)
        return message.sequence_number

    def has_received_messages(self) -> bool:
        return len(self._received_messages) > 0

    def recv(self) -> List[Frame]:
        if len(self._received_messages) > 0:
            return self._received_messages.pop()
        else:
            raise RuntimeError("No messages to receive.")

    def received_connection_is_closed(self):
        self._connection_is_closed = True

    @property
    def connection_is_closed(self) -> bool:
        return self._connection_is_closed

    def received_acknowledge_payload_message(
        self, acknowledge_payload: messages.AcknowledgePayload
    ):
        """Not yet implemented and for that reason we ignore the input"""
