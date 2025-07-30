from typing import (
    Literal,
    Optional,
    Union,
)

from pydantic import (
    BaseModel,
    Field,
    RootModel,
)

from exasol.analytics.udf.communication.connection_info import ConnectionInfo
from exasol.analytics.udf.communication.peer import Peer


class BaseMessage(BaseModel, frozen=True):
    pass


class RegisterPeer(BaseMessage, frozen=True):
    message_type: Literal["RegisterPeer"] = "RegisterPeer"
    peer: Peer
    source: Optional[Peer] = None


class AcknowledgeRegisterPeer(BaseMessage, frozen=True):
    message_type: Literal["AcknowledgeRegisterPeer"] = "AcknowledgeRegisterPeer"
    peer: Peer
    source: Peer


class RegisterPeerComplete(BaseMessage, frozen=True):
    message_type: Literal["RegisterPeerComplete"] = "RegisterPeerComplete"
    peer: Peer
    source: Peer


class PeerRegisterForwarderIsReady(BaseMessage, frozen=True):
    message_type: Literal["PeerRegisterForwarderIsReady"] = (
        "PeerRegisterForwarderIsReady"
    )
    peer: Peer


class Ping(BaseMessage, frozen=True):
    message_type: Literal["Ping"] = "Ping"
    source: ConnectionInfo


class Stop(BaseMessage, frozen=True):
    message_type: Literal["Stop"] = "Stop"


class PrepareToStop(BaseMessage, frozen=True):
    message_type: Literal["PrepareToStop"] = "PrepareToStop"


class IsReadyToStop(BaseMessage, frozen=True):
    message_type: Literal["IsReadyToStop"] = "IsReadyToStop"


class Payload(BaseMessage, frozen=True):
    message_type: Literal["Payload"] = "Payload"
    source: Peer
    destination: Peer
    sequence_number: int


class AcknowledgePayload(BaseMessage, frozen=True):
    message_type: Literal["AcknowledgePayload"] = "AcknowledgePayload"
    source: Peer
    destination: Peer
    sequence_number: int


class AbortPayload(BaseMessage, frozen=True):
    message_type: Literal["AbortPayload"] = "AbortPayload"
    payload: Payload
    reason: str


class MyConnectionInfo(BaseMessage, frozen=True):
    message_type: Literal["MyConnectionInfo"] = "MyConnectionInfo"
    my_connection_info: ConnectionInfo


class SynchronizeConnection(BaseMessage, frozen=True):
    message_type: Literal["SynchronizeConnection"] = "SynchronizeConnection"
    source: ConnectionInfo
    destination: Peer
    attempt: int


class AcknowledgeConnection(BaseMessage, frozen=True):
    message_type: Literal["AcknowledgeConnection"] = "AcknowledgeConnection"
    source: ConnectionInfo
    destination: Peer


class ConnectionIsReady(BaseMessage, frozen=True):
    message_type: Literal["ConnectionIsReady"] = "ConnectionIsReady"
    peer: Peer


class CloseConnection(BaseMessage, frozen=True):
    message_type: Literal["CloseConnection"] = "CloseConnection"
    source: ConnectionInfo
    destination: Peer
    attempt: int


class AcknowledgeCloseConnection(BaseMessage, frozen=True):
    message_type: Literal["AcknowledgeCloseConnection"] = "AcknowledgeCloseConnection"
    source: ConnectionInfo
    destination: Peer


class ConnectionIsClosed(BaseMessage, frozen=True):
    message_type: Literal["ConnectionIsClosed"] = "ConnectionIsClosed"
    peer: Peer


class Timeout(BaseMessage, frozen=True):
    message_type: Literal["Timeout"] = "Timeout"
    reason: str


class Gather(BaseMessage, frozen=True):
    message_type: Literal["Gather"] = "Gather"
    source: Peer
    destination: Peer
    sequence_number: int
    position: int


class Broadcast(BaseMessage, frozen=True):
    message_type: Literal["Broadcast"] = "Broadcast"
    source: Peer
    destination: Peer
    sequence_number: int


class Message(RootModel, frozen=True):
    root: Union[
        Ping,
        RegisterPeer,
        AcknowledgeRegisterPeer,
        RegisterPeerComplete,
        PeerRegisterForwarderIsReady,
        Stop,
        PrepareToStop,
        IsReadyToStop,
        Payload,
        AcknowledgePayload,
        AbortPayload,
        MyConnectionInfo,
        ConnectionIsReady,
        SynchronizeConnection,
        AcknowledgeConnection,
        CloseConnection,
        AcknowledgeCloseConnection,
        ConnectionIsClosed,
        Timeout,
        Gather,
        Broadcast,
    ] = Field(discriminator="message_type")
