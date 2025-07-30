from plm.v1 import process_pb2 as _process_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NewProcessMessage(_message.Message):
    __slots__ = ("name", "description", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    type: _process_pb2.ProcessType
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[_process_pb2.ProcessType, str]] = ...) -> None: ...

class UpdateProcessMessage(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteProcessMessage(_message.Message):
    __slots__ = ("process_id",)
    PROCESS_ID_FIELD_NUMBER: _ClassVar[int]
    process_id: str
    def __init__(self, process_id: _Optional[str] = ...) -> None: ...
