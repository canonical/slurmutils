# Copyright 2024-2025 Canonical Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Base classes and functions for composing Slurm data models."""

# pyright: reportIncompatibleMethodOverride=false
#   This override is required because `pyright` dislikes in `ModelMapping` how
#   `_MapModel` and `MutableSequence` have conflicting signatures for the
#   `update` method. Potentially a candidate for a later refactor.

__all__ = [
    "classproperty",
    "Metadata",
    "Mode",
    "Model",
    "ModelList",
    "ModelMapping",
    "make_model_builder",
]

import json
import sys
from abc import ABC, ABCMeta, abstractmethod
from collections import Counter, deque
from collections.abc import (
    Callable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from dataclasses import dataclass
from enum import Enum, auto
from functools import singledispatchmethod
from inspect import getmro
from itertools import filterfalse, takewhile
from types import MethodType, NoneType, UnionType
from typing import (
    Annotated,
    Any,
    TypeVar,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from jsonschema import ValidationError, validate
from typing_extensions import Self, get_original_bases

from ..exceptions import ModelError
from .callback import Callback, DefaultCallback

if sys.version_info >= (3, 14):
    from annotationlib import Format, get_annotations
else:
    # The `__annotations__` attribute was removed from the `namespace` argument
    # of ABCMeta classes in Python 3.14, and replaced by the new
    # `annotationlib.get_annotations` function. Thus, we patch up a shim for 3.12
    # to make the code consistent between versions.
    class Format:
        VALUE = 1

    def get_annotations(obj, *, format=Format.VALUE):  # noqa: ARG001
        return dict(getattr(obj, "__annotations__", {}) or {})


class classproperty(property):  # noqa N801
    """Class property attribute.

    Create a class-level, read-only property.
    """

    def __get__(self, __instance, __owner: Any | None = None) -> Any:  # noqa D105
        return super().__get__(__owner)


class subclassdispatch:  # noqa N801
    """Like `singledispatch`, but dispatch based on subclass instead.

    Dispatches functions based on what the passed argument is a subclass of.
    """

    def __init__(self, func: Callable[..., Any]) -> None:
        self._registry = {}
        self._default_func = func
        self.__name__ = func.__name__

    def register(self, func: Callable[..., Any]) -> None:
        _, cls = next(iter(get_type_hints(func).items()))
        self._registry[cls] = func

    def dispatch(self, sub_cls: Any) -> Callable[..., Any]:
        if not isinstance(sub_cls, type):
            sub_cls = type(sub_cls)

        for cls, func in self._registry.items():
            if issubclass(sub_cls, cls):
                return func

        return self._default_func

    def __call__(self, *args, **kwargs) -> Any:
        return self.dispatch(args[0])(*args, **kwargs)

    def __get__(self, instance, owner) -> Self | MethodType:
        if instance is not None:
            return MethodType(self, instance)
        else:
            return self


class Mode(Enum):
    r"""Mode to parse/marshal Slurm configuration data.

    Attributes:
        ONELINE: Parse/marshal Slurm configuration from/to one line.
        STANZA: Parse/marshal Slurm configuration from/to a stanza.

    Examples:
        If mode is set to `ONELINE`, parse/marshal using " " as the separator:
            parse:
                "key1=value key2=value" -> {"key1": "value", "key2": "value"}
            marshal:
                 {"key1": "value", "key2": "value"} -> "key1=value key2=value"

        If mode is set to `STANZA`, parse\\marshal using "\n" as the separator:
            parse:
                "key1=value\nkey2=value" -> {"key1": "value", "key2": "value"}
            marshal:
                {"key1": "value", "key2": "value"} -> "key1=value\nkey2=value"
    """

    ONELINE = auto()
    STANZA = auto()


@dataclass(frozen=True)
class Metadata:
    r"""Metadata for Slurm configuration field.

    Attributes:
        origin: Name of field in configuration model.
        alias: Alias(es) used to identify field in a configuration file.
        sep: Separator used to split a field's key and value.
        unique: Flag for if field can occur only once or multiple times in a configuration file.
        primary: Flag for if a field should be at the front of a line in marshalled output.
        callback: Callbacks for handling field during parsing and marshalling.
        default_factory:
            A zero argument callable that will provide a default value if either
            `del` is called on the field, or the field is not present in the configuration file.

    Methods:
        parse: Alias for accessing `callback.parser` method.
        marshal: Alias for accessing `callback.marshaller` method.
    """

    origin: str = ""
    alias: str = ""
    sep: str = "="
    unique: bool = True
    primary: bool = False
    callback: Callback = DefaultCallback
    default_factory: Callable[[], Any] | None = None

    def parse(self, expr: str) -> Any:
        """Alias for accessing `callback.parser` method."""
        return self.callback.parser(expr, self.sep)

    def marshal(self, key: str, value: str) -> str:
        """Alias for accessing `callback.marshaller` method."""
        return self.callback.marshaller(key, value, self.sep)


class _ModelMeta(ABCMeta):
    """Metaclass for defining configuration models."""

    def __new__(
        mcls,  # noqa N804
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        /,
        **kwargs: dict[str, Any],
    ) -> "_ModelMeta":
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)

        for field, annotation in get_annotations(cls, format=Format.VALUE).items():
            metadata = _get_metadata(annotation)
            setattr(cls, field, _make_property(_format_field(field), metadata.default_factory))

        return cls


class _ModelBase(metaclass=_ModelMeta):
    """Helper class for providing base methods to models through inheritance."""

    def __init__(self, instance: Any, /) -> None:
        instance = self.validate_model(instance)
        if self.__model_builder__:
            object.__setattr__(self, "_model_data", self.__model_builder__(instance))
        else:
            object.__setattr__(self, "_model_data", instance)

    @classproperty
    @abstractmethod
    def __model_schema__(self) -> dict[str, Any]:  # noqa N805
        """Model json schema."""

    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any] | None:  # noqa N805
        """Model builder."""
        return None

    @classproperty
    def __model_mode__(cls) -> Mode:  # noqa N805
        """Model parse/marshal mode."""
        return Mode.STANZA

    @classmethod
    def from_str(cls, s: str, /) -> Self:
        """Create model from Slurm configuration string(s)."""
        return cls(_parse(cls, s))

    @classmethod
    def from_json(cls, obj: str | bytes | bytearray, /) -> Self:
        """Create model from a json object."""
        return cls(json.loads(obj))

    def json(self) -> str:
        """Get model as a json object."""
        return json.dumps(self.validate_model())

    def validate_model(self, instance: Iterable[Any] | None = None, /) -> Any:
        """Validate a model against its defined json schema.

        Args:
            instance:
                Optional dictionary object to validate against model json schema.
                If left set to `None`, this method will validate the attribute `_model_data`
                against the model json schema instead.

        Raises:
            ModelError:
                Raised if `instance` or the `_model_data` attribute fails to validate
                against the model's json schema.

        Returns:
            Expanded dictionary or list object. Sub-models must be rebuilt if validated output
            will be used for marshalling or overwriting the contents of the `_model_data`
            attribute. Output can be ignored if just performing a validation.
        """
        instance = (
            _get_as_builtin_object(instance)
            if instance is not None
            else _get_as_builtin_object(self._model_data)
        )
        try:
            validate(instance, schema=self.__model_schema__)
        except ValidationError as e:
            raise ModelError(e.message)

        return instance

    def __getattr__(self, item: str) -> Any:  # noqa D105
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __setattr__(self, key: str, value: Any) -> Any:  # noqa D105
        if not hasattr(self, key):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

        super().__setattr__(key, value)

    def __str__(self) -> str:  # noqa D105
        self.validate_model()
        return _marshal(self)


_TModelBase = TypeVar("_TModelBase", bound=_ModelBase)
_KT = TypeVar("_KT", bound=str)


class _MapModel(_ModelBase, ABC):
    """Helper class for providing mapping-related methods to models through inheritance."""

    def __init__(self, m: dict[str, Any] | None = None, /, **kwargs) -> None:
        super().__init__((m if m else {}) | kwargs)

    @classmethod
    def from_dict(cls, m: dict[str, Any], /) -> Self:
        """Create model from dictionary object."""
        return cls(m)

    def dict(self) -> dict[str, Any]:
        """Get model as dictionary object."""
        return self.validate_model()

    def update(self, other: Self) -> None:
        """Update model content with content of another model."""
        self._model_data.update(other._model_data)


class Model(_MapModel, ABC):
    """Base class for build configuration models."""


class ModelList(_ModelBase, ABC, MutableSequence[_TModelBase]):
    """Base class for lists containing models."""

    def __init__(self, i: Model | Iterable[Model] | None = None, /, *models: Model) -> None:
        super().__init__(
            [i] + list(models) if isinstance(i, Model) else list(i or []) + list(models)
        )

    @classmethod
    def from_list(cls, i: Sequence[Any], /) -> Self:
        """Create model from list object."""
        return cls(i)

    def insert(self, index: int, value: Model) -> None:
        """Insert model before index."""
        self._model_data.insert(index, value)

    def list(self) -> list[Any]:
        """Get model as list object."""
        return self.validate_model()

    @singledispatchmethod
    def __getitem__(self, index) -> Model | Self:  # noqa D105
        raise TypeError(f"list indices must be integers or slices, not {type(index)}")

    @__getitem__.register
    def _(self, index: int) -> Model:
        return self._model_data[index]

    @__getitem__.register
    def _(self, index: slice) -> Self:
        return self.__class__(self._model_data[index])

    def __setitem__(self, index: int | slice, value: Model | Iterable[Model]) -> None:  # noqa D105
        self._model_data[index] = value

    def __delitem__(self, index: int | slice) -> None:  # noqa D105
        del self._model_data[index]

    def __len__(self) -> int:  # noqa D105
        return len(self._model_data)


def _sort_model_list(model_list: ModelList) -> dict[str, ModelList]:
    """Sort a model list by the wrapped model's primary key value."""
    result: dict[str, ModelList] = {}

    primary_key = _glom_primary_key(model_list)
    for model in model_list:
        primary_key_value = getattr(model, primary_key)
        if primary_key_value in result:
            result[primary_key_value].append(model)
        else:
            result[primary_key_value] = model_list.__class__(model)

    return result


class ModelMapping(_MapModel, ABC, MutableMapping[_KT, _TModelBase]):
    """Base class for mappings containing models."""

    def __getitem__(self, key: str, /) -> Any:  # noqa D105
        return self._model_data[key]

    def __setitem__(self, key: str, value: Any, /) -> None:  # noqa D105
        self._model_data[key] = value

    def __delitem__(self, key: str, /) -> None:  # noqa D105
        del self._model_data[key]

    def __iter__(self) -> Iterator[str]:  # noqa D105
        return iter(self._model_data)

    def __len__(self) -> int:  # noqa D105
        return len(self._model_data)


def make_model_builder(
    *models: type[Model] | type[ModelList] | type[ModelMapping],
) -> Callable[[Any], Any]:
    """Make a custom model builder from a provided list of models.

    Args:
        *models: Configuration model to create if json schema successfully matches.

    Returns:
        Callable for building a model from a base Python object.
    """

    def match(obj: Any) -> Model | ModelList | ModelMapping | None:
        for model in models:
            try:
                validate(obj, schema=cast(dict[str, Any], model.__model_schema__))
                return model(obj)
            except ValidationError:
                pass

        return None

    @subclassdispatch
    def build(obj: Any) -> Any:
        raise TypeError(f"expected list or Mapping, not {type(obj)}")

    @build.register
    def _(obj: Mapping) -> dict[str, Any]:
        result: dict[str, Any] = {}

        for k, v in obj.items():
            if model := match(v):
                built = model
            elif isinstance(v, Mapping | list):
                built = build(v)
            else:
                built = v

            result[k] = built

        return result

    @build.register
    def _(obj: list) -> list[Any]:
        result: list[Any] = []

        for v in obj:
            if model := match(v):
                built = model
            elif isinstance(v, Mapping | list):
                built = build(v)
            else:
                built = v

            result.append(built)

        return result

    return build


def _make_property(name: str, default_factory: Callable[[], Any] | None = None) -> property:
    """Make new property for a data model field.

    Args:
        name: Name of configuration option that a model field maps to.
        default_factory:
            Zero argument callable to invoke when `del` is either called on the model field
            or the model field is accessed but the configuration option is not present in the
            model's internal data map.
    """

    def getter(self: Model) -> Any | None:
        if default_factory and name not in self._model_data:
            self._model_data[name] = default_factory()

        return self._model_data.get(name, None)

    def setter(self: Model, v: Any) -> None:
        self._model_data[name] = v

    def deleter(self: Model) -> None:
        try:
            del self._model_data[name]
            if default_factory:
                self._model_data[name] = default_factory()
        except KeyError:
            pass

    return property(getter, setter, deleter)


def _make_annotation_map(
    model_t: type[_ModelBase], include_origin: bool = False
) -> dict[str, Annotated]:
    """Make a metadata mapping from a model class.

    Args:
        model_t: Model class to make metadata mapping from.
        include_origin: Include the metadata `origin` field in the annotation mapping.
    """
    annotation_map: dict[str, Annotated] = {}

    for field, annotation in get_type_hints(model_t, include_extras=True).items():
        metadata = _get_metadata(annotation)
        annotation_map[metadata.alias or _format_field(field)] = annotation
        if include_origin and metadata.origin:
            annotation_map[metadata.origin] = annotation

    return annotation_map


def _get_metadata(annotation: type) -> Metadata:
    """Get metadata for a Slurm configuration field.

    Args:
        annotation: Annotation to get metadata of.

    Notes:
        If the field is not annotated with `typing.Annotated`, a
        default `Metadata` object will be returned instead.
    """
    if hasattr(annotation, "__metadata__"):
        return annotation.__metadata__[0]

    return Metadata()


def _get_type(annotation: type) -> tuple[Any, ...]:
    """Get the expected type(s) of a Slurm configuration field.

    Args:
        annotation: Annotation to get the Slurm configuration field type from.

    Notes:
        Some Slurm configuration fields can be multiple types, so a tuple of types is
        returned rather than a single type. For example, the `slurm.conf` configuration
        options `MaxNodes` can be both an integer or the string "unlimited".
    """
    # Check if type annotation is wrapped with `typing.Annotated`.
    if hasattr(annotation, "__origin__"):
        annotation = annotation.__origin__

    # Check if origin is an "Optional". For example, is the annotation `str | None`?
    # Almost all annotations will be `<type> | None` since Slurm configuration
    # fields are nullable.
    if get_origin(annotation) is UnionType:
        return tuple(filterfalse(lambda t: t is NoneType, get_args(annotation)))
    else:
        return (annotation,)


def _get_primary_key(model_t: type[_ModelBase]) -> str | None:
    r"""Get primary key of model.

    Args:
        model_t: Model class to get primary key of.

    Returns:
        Model's primary key or `None` if the model has no declared primary key.
    """
    for field, annotation in get_type_hints(model_t, include_extras=True).items():
        metadata = _get_metadata(annotation)
        if metadata.primary:
            return field

    return None


def _glom_primary_key(model_list: ModelList) -> str:
    """Get the primary key of a list of models.

    Args:
        model_list: List of models to get the primary key of.

    Raises:
        ModelError: Raised if not all models in the list have the same primary key.
    """
    primary_keys = Counter([_get_primary_key(type(model)) for model in model_list])
    if len(primary_keys) > 1 or None in primary_keys:
        raise ModelError(
            (
                f"models in {model_list} either have inconsistent primary keys"
                f"or do not have a primary key defined: {primary_keys}"
            )
        )

    return cast(str, list(primary_keys)[0])


def _format_field(field: str) -> str:
    """Format configuration field to be case-insensitive and remove underscores.

    Args:
        field: Configuration field to format.

    Examples:
        `_format_field("slurmctld_host")` -> "slurmctldhost"
    """
    return field.replace("_", "").lower()


@subclassdispatch
def _get_as_builtin_object(obj: Iterable[Any]) -> Iterable[Any]:
    """Recursively expand a complex iterable with nested models.

    Args:
        obj: Complex iterable to expand.
    """
    raise TypeError(f"expected list or Mapping, not {type(obj)}")


@_get_as_builtin_object.register
def _(obj: Mapping) -> dict[str, Any]:
    return {k: _expand_by_type(v) for k, v in obj.items()}


@_get_as_builtin_object.register
def _(obj: list) -> list[Any]:
    return [_expand_by_type(v) for v in obj]


def _expand_by_type(v: Any) -> Any:
    """Expand an object based on its type.

    Args:
        v: Object to expand based on its type.

    Returns:
        An "expanded" builtin object with no nested custom objects.
    """
    match v:
        case Model():
            return _get_as_builtin_object(v.dict())
        case ModelList():
            return _get_as_builtin_object(v.list())
        case Mapping() | list():
            return _get_as_builtin_object(v)
        case _:
            return v


@subclassdispatch
def _parse(model_t, s: str) -> Iterable[Any]:
    """Parse data in Slurm configuration format into models.

    Args:
        model_t: Model to create from parsed Slurm configuration data.
        s: Data in Slurm configuration format.

    Raises:
        TypeError: Raised if the type of `model_t` is not `Model`, `ModelList`, or `ModelMapping`.
        ModelError: Raised if an error occurs when parsing the value of `s`.
    """
    raise TypeError(
        f"expected subclass of type Model, ModelList, or ModelMapping, not {type(model_t)}"
    )


@_parse.register
def _(model_t: Model, s: str) -> dict[str, Any]:
    annotation_map = _make_annotation_map(cast(type, model_t))

    classification_map: dict[str, list[str]] = {}
    for token, expr in _scan(s, mode=model_t.__model_mode__):
        if token not in annotation_map:
            raise ModelError(
                (
                    f"unrecognized configuration field `{token}`. "
                    f"valid configuration fields are: {list(annotation_map.keys())}"
                )
            )

        classification_map[token] = classification_map.get(token, []) + [expr]

    result: dict[str, Any] = {}
    for token, expr in classification_map.items():
        annotation = annotation_map[token]
        metadata = _get_metadata(annotation)
        tp = _get_type(annotation)

        if metadata.unique and len(expr) > 1:
            raise ModelError(
                (
                    f"expected configuration field `{token}` to be unique, "
                    f"but multiple entries found: {classification_map}"
                )
            )

        if _ModelBase in getmro(tp[0]):
            result[metadata.origin or token] = tp[0].from_str("\n".join(expr))
            continue

        if metadata.unique:
            result[metadata.origin or token] = metadata.parse(expr[0])
        else:
            result[metadata.origin or token] = [metadata.parse(e) for e in expr]

    return result


@_parse.register
def _(model_t: ModelList, s: str) -> list[Any]:
    result: list[Any] = []
    origin = get_original_bases(cast(type, model_t))[0]
    wrapped_model_t = get_args(origin)[0]
    for _, expr in _scan(s, model_t.__model_mode__):
        result.append(wrapped_model_t.from_str(expr))

    return result


@_parse.register
def _(model_t: ModelMapping, s: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    origin = get_original_bases(cast(type, model_t))[0]
    wrapped_model_t = get_args(origin)[1]
    primary_key = _get_primary_key(wrapped_model_t)

    if primary_key:
        for _, expr in _scan(s, model_t.__model_mode__):
            model = wrapped_model_t.from_str(expr)
            result.update({getattr(model, primary_key): model})
    elif primary_key is None and issubclass(wrapped_model_t, ModelList):
        model = wrapped_model_t.from_str(s)
        result.update(_sort_model_list(model))
    else:
        raise ModelError(
            (
                f"model {wrapped_model_t} has no primary key. "
                f"{wrapped_model_t} cannot be used with a model mapping"
            )
        )

    return result


def _clean(s: str) -> list[str]:
    """Clean configuration line(s) before further processing.

    Args:
        s: Configuration line(s) to clean.

    Warnings:
        This function will strip all comments from the configuration line(s),
        but will not preserve them. Original comments will not be present in
        the marshalled configuration data output.
    """
    result: list[str] = []

    for line in s.splitlines():
        cleaned = line.split("#", maxsplit=1)[0].strip()
        if cleaned == "":  # Line was a comment line or is empty.
            continue

        result.append(cleaned)

    return result


def _scan(s: str, /, mode: Mode) -> Iterable[tuple[str, str]]:
    """Scan Slurm configuration data to identify key-value pairs.

    Args:
        s: Configuration data to scan for key-value pairs.
        mode: Mode to scan file in.
    """
    match mode:
        case mode.ONELINE:
            expr = _scan_line(c[0]) if (c := _clean(s)) else []

        case mode.STANZA:
            expr = _clean(s)

        case _:
            raise TypeError(f"mode must be either ONELINE or STANZA, not {type(mode)}")

    for e in expr:
        token = "".join(map(str, takewhile(lambda c: c != "=" and c != " ", e))).lower()
        yield token, e


def _scan_line(s: str) -> list[str]:
    """Scan a Slurm configuration line to identify key-value pairs.

    Args:
        s: Configuration line to scan for key-value pairs.

    Notes:
        This method is used rather than `shlex.split(...)` or a regular expression
        because this method offers a ~429% performance increase over `shlex.split(...)`
        for identifying key-value pairs in a Slurm configuration line.
    """
    pairs: list[str] = []
    quote = None
    current_pair = ""

    for c in s:
        if c in ['"', "'"]:
            if c == quote:
                quote = None
                current_pair += c
            elif quote is None:
                quote = c
                current_pair += c
            else:
                current_pair += c
        elif c.isspace() and quote is None:
            if current_pair:
                pairs.append(current_pair)
                current_pair = ""
        else:
            current_pair += c

    if current_pair:
        pairs.append(current_pair)

    return pairs


@subclassdispatch
def _marshal(model) -> str:
    """Marshal a model into Slurm configuration format.

    Args:
        model: Configuration model to marshal into Slurm configuration format.
    """
    raise TypeError(
        f"expected subclass of type Model, ModelList, or ModelMapping, not {type(model)}"
    )


@_marshal.register
def _(model: Model) -> str:
    annotation_map = _make_annotation_map(type(model), include_origin=True)
    result: deque[str] = deque()

    # Directly access `_model_data` here because `_expand(...)` does not
    # preserve the type information required for subclass dispatching.
    for k, v in model._model_data.items():  # noqa SLF001
        if isinstance(v, Model | ModelList | ModelMapping):
            result.append(str(v))
            continue

        metadata = _get_metadata(annotation_map[k])
        expr = metadata.marshal(metadata.alias or k, v)
        if metadata.primary:
            result.appendleft(expr)
        else:
            result.append(expr)

    return _format_output(result, mode=model.__model_mode__)


@_marshal.register
def _(model: ModelList) -> str:
    result: list[str] = []
    for wrapped_model in model:
        result.append(str(wrapped_model))

    return _format_output(result, mode=model.__model_mode__)


@_marshal.register
def _(model: ModelMapping) -> str:
    result: list[str] = []
    for wrapped_model in model.values():
        result.append(str(wrapped_model))

    return _format_output(result, mode=model.__model_mode__)


def _format_output(i: Iterable[str], mode: Mode) -> str:
    """Format `_marshal` output based on model mode.

    Args:
        i: Iterable to format based on given mode.
        mode: Mode to format output in.

    Raises:
        TypeError:
            Raised if invalid marshaling mode is provided.
            Valid modes are `ONELINE` and `STANZA`.
    """
    match mode:
        case Mode.ONELINE:
            return " ".join(i)
        case Mode.STANZA:
            return "\n".join(i)
        case _:
            raise TypeError(f"mode must be either ONELINE or STANZA, not {type(mode)}")
