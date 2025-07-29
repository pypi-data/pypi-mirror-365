import json
import typing
from collections.abc import Iterable
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Final,
    Generic,
    Literal,
    Mapping,
    Optional,
    TypeAlias,
    TypeVar,
    Union,
    cast,
)


@dataclass(frozen=True)
class TypeDescriptor:
    type: "Type"
    records: tuple["Record", ...]

    def as_json(self) -> Any:
        return _TYPE_DESCRIPTOR_SERIALIZER.to_json(self)

    def as_json_code(self) -> str:
        return json.dumps(self.as_json(), indent=2)

    @staticmethod
    def from_json(json: Any) -> "TypeDescriptor":
        return _TYPE_DESCRIPTOR_SERIALIZER.from_json(json)

    @staticmethod
    def from_json_code(json_code: str) -> "TypeDescriptor":
        return _TYPE_DESCRIPTOR_SERIALIZER.from_json(json.loads(json_code))


@dataclass(frozen=True)
class PrimitiveType:
    kind: Literal["primitive"]
    value: Literal[
        "bool",
        "int32",
        "int64",
        "uint64",
        "float32",
        "float64",
        "timestamp",
        "string",
        "bytes",
    ]


@dataclass(frozen=True)
class OptionalType:
    kind: Literal["optional"]
    value: "Type"


@dataclass(frozen=True)
class ArrayType:
    kind: Literal["array"]

    @dataclass(frozen=True)
    class Array:
        item: "Type"
        key_chain: tuple[str, ...]

    value: Array


@dataclass(frozen=True)
class RecordType:
    kind: Literal["record"]
    value: str


Type: TypeAlias = Union[PrimitiveType, OptionalType, ArrayType, RecordType]


@dataclass(frozen=True)
class Field:
    name: str
    type: Optional[Type]
    number: int


@dataclass(frozen=True)
class Record:
    kind: Literal["struct", "enum"]
    id: str
    fields: tuple[Field, ...]
    removed_fields: tuple[int, ...]


# ==============================================================================
# INTERNAL: JSON serialization framework
# ==============================================================================


_T = TypeVar("_T")


@dataclass(frozen=True)
class _Serializer(Generic[_T]):
    to_json: Callable[[_T], Any]
    from_json: Callable[[Any], _T]


@dataclass(frozen=True, eq=True)
class _NoDefault:
    pass


_NO_DEFAULT: Final = _NoDefault()


@dataclass(frozen=True)
class _FieldSerializer(Generic[_T]):
    name: str
    serializer: _Serializer[_T]
    default: _T | _NoDefault = _NO_DEFAULT


def _primitive_serializer(check_type_fn: Callable[[Any], _T]) -> _Serializer[_T]:
    return _Serializer(check_type_fn, check_type_fn)


def _literal_union_serializer(s: set[_T]) -> _Serializer[_T]:
    def check_in(input: _T) -> _T:
        if input not in s:
            raise ValueError(f"{input} is not in {s}")
        return input

    return _Serializer(check_in, check_in)


def _dataclass_serializer(
    type: typing.Type[_T], fields: Iterable[_FieldSerializer]
) -> _Serializer[_T]:
    def to_json(obj: _T) -> dict[str, Any]:
        json = {}
        for field in fields:
            value = getattr(obj, field.name)
            if value != field.default:
                json[field.name] = field.serializer.to_json(value)
        return json

    def from_json(json: dict[str, Any]) -> _T:
        def field_from_json(field: _FieldSerializer) -> Any:
            value_json = json.get(field.name)
            if value_json is None:
                if field.default != _NO_DEFAULT:
                    return field.default
                else:
                    # Will raise an exception.
                    json[field.name]
            return field.serializer.from_json(value_json)

        return type(**{f.name: field_from_json(f) for f in fields})

    return _Serializer(to_json, from_json)


def _union_serializer(
    kind_to_serializer: Mapping[str, _Serializer],
) -> _Serializer:
    def to_json(input: Any) -> dict[str, Any]:
        kind = cast(Any, input).kind
        serializer = kind_to_serializer[kind]
        return serializer.to_json(input)

    def from_json(json: dict[str, Any]) -> Any:
        kind = json["kind"]
        serializer = kind_to_serializer[kind]
        return serializer.from_json(json)

    return _Serializer(to_json, from_json)


def _listuple_serializer(
    item_serializer: _Serializer[_T],
) -> _Serializer[tuple[_T, ...]]:
    def to_json(input: tuple[_T, ...]) -> list[Any]:
        return [item_serializer.to_json(e) for e in input]

    def from_json(json: list[Any]) -> tuple[_T, ...]:
        return tuple(item_serializer.from_json(e) for e in json)

    return _Serializer(to_json, from_json)


def _forwarding_serializer(
    get_serializer_fn: Callable[[], _Serializer[_T]],
) -> _Serializer[_T]:
    def to_json(input: _T) -> Any:
        return get_serializer_fn().to_json(input)

    def from_json(json: Any) -> _T:
        return get_serializer_fn().from_json(json)

    return _Serializer(to_json, from_json)


def _optional_serializer(
    other_serializer: _Serializer[_T],
) -> _Serializer[Optional[_T]]:
    def to_json(input: Optional[_T]) -> Any:
        if input is None:
            return None
        return other_serializer.to_json(input)

    def from_json(json: Any) -> Optional[_T]:
        if json is None:
            return None
        return other_serializer.from_json(json)

    return _Serializer(to_json, from_json)


# ==============================================================================
# INTERNAL: JSON serialization of TypeDescriptor
# ==============================================================================


def _type_serializer() -> _Serializer[Type]:
    return _TYPE_SERIALIZER


_TYPE_SERIALIZER: Final = _union_serializer(
    {
        "primitive": _dataclass_serializer(
            PrimitiveType,
            [
                _FieldSerializer("kind", _literal_union_serializer({"primitive"})),
                _FieldSerializer(
                    "value",
                    _literal_union_serializer(
                        {
                            "bool",
                            "int32",
                            "int64",
                            "uint64",
                            "float32",
                            "float64",
                            "timestamp",
                            "string",
                            "bytes",
                        }
                    ),
                ),
            ],
        ),
        "optional": _dataclass_serializer(
            OptionalType,
            [
                _FieldSerializer(
                    "kind",
                    _literal_union_serializer({"optional"}),
                ),
                _FieldSerializer(
                    "value",
                    _forwarding_serializer(_type_serializer),
                ),
            ],
        ),
        "array": _dataclass_serializer(
            ArrayType,
            [
                _FieldSerializer(
                    "kind",
                    _literal_union_serializer({"array"}),
                ),
                _FieldSerializer(
                    "value",
                    _dataclass_serializer(
                        ArrayType.Array,
                        [
                            _FieldSerializer(
                                "item",
                                _forwarding_serializer(_type_serializer),
                            ),
                            _FieldSerializer(
                                "key_chain",
                                _listuple_serializer(_primitive_serializer(str)),
                                default=(),
                            ),
                        ],
                    ),
                ),
            ],
        ),
        "record": _dataclass_serializer(
            RecordType,
            [
                _FieldSerializer(
                    "kind",
                    _literal_union_serializer({"record"}),
                ),
                _FieldSerializer(
                    "value",
                    _primitive_serializer(str),
                ),
            ],
        ),
    }
)


_FIELD_SERIALIZER: Final = _dataclass_serializer(
    Field,
    [
        _FieldSerializer(
            "name",
            _primitive_serializer(str),
        ),
        _FieldSerializer[Optional[Type]](
            "type",
            _optional_serializer(_forwarding_serializer(_type_serializer)),
            default=None,
        ),
        _FieldSerializer(
            "number",
            _primitive_serializer(int),
        ),
    ],
)


_RECORD_SERIALIZER: Final = _dataclass_serializer(
    Record,
    [
        _FieldSerializer(
            "kind",
            _literal_union_serializer({"struct", "enum"}),
        ),
        _FieldSerializer(
            "id",
            _primitive_serializer(str),
        ),
        _FieldSerializer(
            "fields",
            _listuple_serializer(_FIELD_SERIALIZER),
        ),
        _FieldSerializer(
            "removed_fields",
            _listuple_serializer(_primitive_serializer(int)),
            default=(),
        ),
    ],
)


_TYPE_DESCRIPTOR_SERIALIZER = _dataclass_serializer(
    TypeDescriptor,
    [
        _FieldSerializer(
            "type",
            _TYPE_SERIALIZER,
        ),
        _FieldSerializer(
            "records",
            _listuple_serializer(_RECORD_SERIALIZER),
        ),
    ],
)
