from geometry.v1 import pose_pb2 as _pose_pb2
from plm.v1 import sequence_pb2 as _sequence_pb2
from plm.v1 import task_pb2 as _task_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROCESS_TYPE_UNSPECIFIED: _ClassVar[ProcessType]
    PROCESS_TYPE_ASSEMBLY: _ClassVar[ProcessType]
    PROCESS_TYPE_DISASSEMBLY: _ClassVar[ProcessType]
    PROCESS_TYPE_INSPECTION: _ClassVar[ProcessType]
PROCESS_TYPE_UNSPECIFIED: ProcessType
PROCESS_TYPE_ASSEMBLY: ProcessType
PROCESS_TYPE_DISASSEMBLY: ProcessType
PROCESS_TYPE_INSPECTION: ProcessType

class ProcessMessage(_message.Message):
    __slots__ = ("instance_id", "id", "name", "description", "type", "frame", "root_sequence_id", "sequences", "tasks")
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    ROOT_SEQUENCE_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCES_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    instance_id: str
    id: str
    name: str
    description: str
    type: ProcessType
    frame: _pose_pb2.LocalizedPose
    root_sequence_id: str
    sequences: _containers.RepeatedCompositeFieldContainer[_sequence_pb2.SequenceMessage]
    tasks: _containers.RepeatedCompositeFieldContainer[_task_pb2.TaskMessage]
    def __init__(self, instance_id: _Optional[str] = ..., id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[ProcessType, str]] = ..., frame: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ..., root_sequence_id: _Optional[str] = ..., sequences: _Optional[_Iterable[_Union[_sequence_pb2.SequenceMessage, _Mapping]]] = ..., tasks: _Optional[_Iterable[_Union[_task_pb2.TaskMessage, _Mapping]]] = ...) -> None: ...
