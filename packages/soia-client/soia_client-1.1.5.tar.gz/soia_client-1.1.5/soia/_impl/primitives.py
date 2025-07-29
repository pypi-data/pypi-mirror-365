import base64
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final, final

from soia import _spec, reflection
from soia._impl.function_maker import Expr, ExprLike
from soia._impl.timestamp import Timestamp
from soia._impl.type_adapter import TypeAdapter


class AbstractPrimitiveAdapter(TypeAdapter):
    @final
    def finalize(
        self,
        resolve_type_fn: Callable[[_spec.Type], "TypeAdapter"],
    ) -> None:
        pass

    @final
    def register_records(
        self,
        registry: dict[str, reflection.Record],
    ) -> None:
        pass

    @final
    def frozen_class_of_struct(self) -> type | None:
        return None


class _BoolAdapter(AbstractPrimitiveAdapter):
    def default_expr(self) -> ExprLike:
        return "False"

    def to_frozen_expr(self, arg_expr: ExprLike) -> Expr:
        return Expr.join("(True if ", arg_expr, " else False)")

    def is_not_default_expr(self, arg_expr: ExprLike, attr_expr: ExprLike) -> ExprLike:
        return arg_expr

    def to_json_expr(
        self,
        in_expr: ExprLike,
        readable: bool,
    ) -> ExprLike:
        if readable:
            return Expr.join("(True if ", in_expr, " else False)")
        else:
            return Expr.join("(1 if ", in_expr, " else 0)")

    def from_json_expr(self, json_expr: ExprLike) -> Expr:
        return Expr.join("(True if ", json_expr, " else False)")

    def get_type(self) -> reflection.Type:
        return reflection.PrimitiveType(
            kind="primitive",
            value="bool",
        )


BOOL_ADAPTER: Final[TypeAdapter] = _BoolAdapter()


@dataclass(frozen=True)
class _AbstractIntAdapter(AbstractPrimitiveAdapter):
    """Type adapter implementation for int32, int64 and uint64."""

    def default_expr(self) -> ExprLike:
        return "0"

    def to_frozen_expr(self, arg_expr: ExprLike) -> Expr:
        # Must accept float inputs and turn them into ints.
        return Expr.join("(0).__class__(", arg_expr, ")")

    def is_not_default_expr(self, arg_expr: ExprLike, attr_expr: ExprLike) -> ExprLike:
        return arg_expr

    def from_json_expr(self, json_expr: ExprLike) -> Expr:
        # Must accept float inputs and string inputs and turn them into ints.
        return Expr.join(
            "(0).__class__(",
            json_expr,
            ")",
        )


@dataclass(frozen=True)
class _Int32Adapter(_AbstractIntAdapter):
    def to_json_expr(self, in_expr: ExprLike, readable: bool) -> Expr:
        return Expr.join(
            "(-2147483648 if ",
            in_expr,
            " <= -2147483648 else ",
            in_expr,
            " if ",
            in_expr,
            " < 2147483647 else 2147483647)",
        )

    def get_type(self) -> reflection.Type:
        return reflection.PrimitiveType(
            kind="primitive",
            value="int32",
        )


def _int64_to_json(i: int) -> int | str:
    if i < -9007199254740991:  # min safe integer in JavaScript
        if i <= -9223372036854775808:
            return "-9223372036854775808"
        else:
            return str(i)
    elif i <= 9007199254740991:  # max safe integer in JavaScript
        return i
    elif i < 9223372036854775807:
        return str(i)
    else:
        return "9223372036854775807"


@dataclass(frozen=True)
class _Int64Adapter(_AbstractIntAdapter):
    def to_json_expr(self, in_expr: ExprLike, readable: bool) -> Expr:
        return Expr.join(Expr.local("int64_to_json", _int64_to_json), "(", in_expr, ")")

    def get_type(self) -> reflection.Type:
        return reflection.PrimitiveType(
            kind="primitive",
            value="int64",
        )


def _uint64_to_json(i: int) -> int | str:
    if i <= 0:
        return 0
    elif i <= 9007199254740991:  # max safe integer in JavaScript
        return i
    elif i < 18446744073709551615:
        return f"{i}"
    else:
        return "18446744073709551615"


@dataclass(frozen=True)
class _Uint64Adapter(_AbstractIntAdapter):
    def to_json_expr(self, in_expr: ExprLike, readable: bool) -> Expr:
        return Expr.join(
            Expr.local("uint64_to_json", _uint64_to_json), "(", in_expr, ")"
        )

    def get_type(self) -> reflection.Type:
        return reflection.PrimitiveType(
            kind="primitive",
            value="uint64",
        )


INT32_ADAPTER: Final[TypeAdapter] = _Int32Adapter()
INT64_ADAPTER: Final[TypeAdapter] = _Int64Adapter()
UINT64_ADAPTER: Final[TypeAdapter] = _Uint64Adapter()


@dataclass(frozen=True)
class _AbstractFloatAdapter(AbstractPrimitiveAdapter):
    """Type adapter implementation for float32 and float64."""

    def default_expr(self) -> ExprLike:
        return "0.0"

    def to_frozen_expr(self, arg_expr: ExprLike) -> Expr:
        return Expr.join("(", arg_expr, " + 0.0)")

    def is_not_default_expr(self, arg_expr: ExprLike, attr_expr: ExprLike) -> ExprLike:
        return arg_expr

    def to_json_expr(self, in_expr: ExprLike, readable: bool) -> ExprLike:
        return in_expr

    def from_json_expr(self, json_expr: ExprLike) -> Expr:
        return Expr.join("(", json_expr, " + 0.0)")


@dataclass(frozen=True)
class _Float32Adapter(_AbstractFloatAdapter):
    """Type adapter implementation for float32."""

    def get_type(self) -> reflection.Type:
        return reflection.PrimitiveType(
            kind="primitive",
            value="float32",
        )


@dataclass(frozen=True)
class _Float64Adapter(_AbstractFloatAdapter):
    """Type adapter implementation for float32."""

    def get_type(self) -> reflection.Type:
        return reflection.PrimitiveType(
            kind="primitive",
            value="float64",
        )


FLOAT32_ADAPTER: Final[TypeAdapter] = _Float32Adapter()
FLOAT64_ADAPTER: Final[TypeAdapter] = _Float64Adapter()


class _TimestampAdapter(AbstractPrimitiveAdapter):
    def default_expr(self) -> Expr:
        return Expr.local("_EPOCH", Timestamp.EPOCH)

    def to_frozen_expr(self, arg_expr: ExprLike) -> Expr:
        timestamp_local = Expr.local("Timestamp", Timestamp)
        return Expr.join(
            "(",
            arg_expr,
            " if ",
            arg_expr,
            ".__class__ is ",
            timestamp_local,
            " else ",
            timestamp_local,
            "(unix_millis=",
            arg_expr,
            ".unix_millis))",
        )

    def is_not_default_expr(self, arg_expr: ExprLike, attr_expr: ExprLike) -> Expr:
        return Expr.join(arg_expr, ".unix_millis")

    def to_json_expr(self, in_expr: ExprLike, readable: bool) -> Expr:
        if readable:
            return Expr.join(in_expr, "._trj()")
        else:
            return Expr.join(in_expr, ".unix_millis")

    def from_json_expr(self, json_expr: ExprLike) -> Expr:
        fn = Expr.local("_timestamp_from_json", _timestamp_from_json)
        return Expr.join(fn, "(", json_expr, ")")

    def get_type(self) -> reflection.Type:
        return reflection.PrimitiveType(
            kind="primitive",
            value="timestamp",
        )


def _timestamp_from_json(json: Any) -> Timestamp:
    if json.__class__ is int or isinstance(json, int):
        return Timestamp(unix_millis=json)
    else:
        return Timestamp(unix_millis=json["unix_millis"])


TIMESTAMP_ADAPTER: Final[TypeAdapter] = _TimestampAdapter()


class _StringAdapter(AbstractPrimitiveAdapter):
    def default_expr(self) -> ExprLike:
        return '""'

    def to_frozen_expr(self, arg_expr: ExprLike) -> Expr:
        return Expr.join("('' + ", arg_expr, ")")

    def is_not_default_expr(self, arg_expr: ExprLike, attr_expr: ExprLike) -> ExprLike:
        return arg_expr

    def to_json_expr(self, in_expr: ExprLike, readable: bool) -> ExprLike:
        return in_expr

    def from_json_expr(self, json_expr: ExprLike) -> Expr:
        return Expr.join("('' + (", json_expr, " or ''))")

    def get_type(self) -> reflection.Type:
        return reflection.PrimitiveType(
            kind="primitive",
            value="string",
        )


STRING_ADAPTER: Final[TypeAdapter] = _StringAdapter()


class _BytesAdapter(AbstractPrimitiveAdapter):
    def default_expr(self) -> ExprLike:
        return 'b""'

    def to_frozen_expr(self, arg_expr: ExprLike) -> Expr:
        return Expr.join("(b'' + ", arg_expr, ")")

    def is_not_default_expr(self, arg_expr: ExprLike, attr_expr: ExprLike) -> ExprLike:
        return arg_expr

    def to_json_expr(
        self,
        in_expr: ExprLike,
        readable: bool,
    ) -> Expr:
        return Expr.join(
            Expr.local("b64encode", base64.b64encode),
            "(",
            in_expr,
            ").decode('utf-8')",
        )

    def from_json_expr(self, json_expr: ExprLike) -> Expr:
        return Expr.join(
            Expr.local("b64decode", base64.b64decode), "(", json_expr, ' or "")'
        )

    def get_type(self) -> reflection.Type:
        return reflection.PrimitiveType(
            kind="primitive",
            value="bytes",
        )


BYTES_ADAPTER: Final[TypeAdapter] = _BytesAdapter()
