from typing import Optional

import structlog
from structlog.typing import FilteringBoundLogger

from exasol.analytics.udf.communication.connection_info import ConnectionInfo
from exasol.analytics.udf.communication.peer import Peer
from exasol.analytics.udf.communication.peer_communicator.register_peer_connection import (
    RegisterPeerConnection,
)
from exasol.analytics.udf.communication.peer_communicator.timer import Timer

LOGGER: FilteringBoundLogger = structlog.get_logger()


class RegisterPeerSender:
    def __init__(
        self,
        register_peer_connection: Optional[RegisterPeerConnection],
        needs_to_send_for_peer: bool,
        my_connection_info: ConnectionInfo,
        peer: Peer,
        timer: Timer,
    ):
        self._needs_to_send_for_peer = needs_to_send_for_peer
        self._register_peer_connection = register_peer_connection
        if needs_to_send_for_peer and self._register_peer_connection is None:
            raise ValueError(
                "_register_peer_connection is None while needs_to_send_for_peer is true"
            )
        self._my_connection_info = my_connection_info
        self._timer = timer
        self._finished = False
        self._peer = peer
        self._send_attempt_count = 0
        self._logger = LOGGER.bind(
            peer=peer.model_dump(),
            my_connection_info=my_connection_info.model_dump(),
            needs_to_send_for_peer=self._needs_to_send_for_peer,
        )
        self._logger.debug("init")

    def stop(self):
        self._logger.debug("stop")
        self._finished = True

    def try_send(self, force=False):
        self._logger.debug("try_send")
        should_we_send = self._should_we_send()
        if (should_we_send or force) and self._needs_to_send_for_peer:
            self._send()
            self._timer.reset_timer()

    def _send(self):
        self._send_attempt_count += 1
        self._logger.debug("send", send_attempt_count=self._send_attempt_count)
        self._register_peer_connection.forward(self._peer)

    def _should_we_send(self) -> bool:
        is_time = self._timer.is_time()
        result = is_time and not self._finished
        return result

    def is_ready_to_stop(self) -> bool:
        return self._finished or not self._needs_to_send_for_peer


class RegisterPeerSenderFactory:
    def create(
        self,
        register_peer_connection: Optional[RegisterPeerConnection],
        needs_to_send_for_peer: bool,
        my_connection_info: ConnectionInfo,
        peer: Peer,
        timer: Timer,
    ) -> RegisterPeerSender:
        register_peer_sender = RegisterPeerSender(
            register_peer_connection=register_peer_connection,
            needs_to_send_for_peer=needs_to_send_for_peer,
            my_connection_info=my_connection_info,
            peer=peer,
            timer=timer,
        )
        return register_peer_sender
