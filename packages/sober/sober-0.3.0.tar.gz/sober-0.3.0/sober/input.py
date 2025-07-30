"""Classes for defining inputs."""

from __future__ import annotations

import math
import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, cast, final

import scipy.stats
from eppy.bunchhelpers import makefieldname

from sober._tools import _parsed_path, _uuid
from sober._typing import AnyModelModifierValue, AnyModifierValue

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator
    from typing import Concatenate, Self

    from eppy.bunch_subclass import EpBunch

    from sober._typing import AnyStrPath, AnyTagger, SupportsPPF

    class _SupportsStr(Protocol):
        __slots__ = ()

        def __str__(self) -> str: ...

    # NOTE: ... implies accepting args and kwargs, but only kwargs are accepted
    #       could be corrected using Protocol, but why bother
    # TODO: consider resticting at least one previous output
    type _AnyFunc = Callable[
        Concatenate[tuple[AnyModifierValue, ...], ...], AnyModelModifierValue
    ]


##############################  module typing  ##############################
# https://github.com/python/typing/issues/60#issuecomment-869757075
# this can be removed with the new type syntax from py3.12


class _IDF(Protocol):
    """A minimum stub to help mypy recognise variance."""

    __slots__ = ()

    def getobject(self, key: str, name: str) -> EpBunch: ...


_TM = TypeVar("_TM", _IDF, str)  # AnyTaggerModel
_MK_contra = TypeVar("_MK_contra", float, int, contravariant=True)  # AnyModifierKey
_MV_co = TypeVar("_MV_co", bound=AnyModifierValue, covariant=True)  # AnyModifierValue
#############################################################################


@final
class _Noise(Any):  # type: ignore[misc]
    """A helper class for _hype_ctrl_value."""

    __slots__ = ("_s",)

    _s: str

    def __new__(cls, s: str, /) -> Self:
        self = super().__new__(cls)
        self._s = s
        return self  # type: ignore[no-any-return]

    def __str__(self) -> str:
        """Control csv.writer."""
        return f"<noise {self._s}>"


#############################################################################
#######                     ABSTRACT BASE CLASSES                     #######
#############################################################################
class _Tagger(ABC, Generic[_TM]):
    """An abstract base class for taggers."""

    __slots__ = ("_tags",)

    _tags: tuple[str, ...]

    @abstractmethod
    def __init__(self, *feature_groups: tuple[str, ...]) -> None:
        self._tags = tuple(_uuid(type(self).__name__, *item) for item in feature_groups)

    @abstractmethod
    def _tagged(self, model: _TM) -> _TM: ...

    def _detagged(self, tagged_model: str, value: _SupportsStr) -> str:
        for tag in self._tags:
            tagged_model = tagged_model.replace(tag, str(value))

        return tagged_model


class _IDFTagger(_Tagger[_IDF]):
    """An abstract base class for taggers in the IDF format."""

    __slots__ = ()

    @abstractmethod
    def _tagged(self, model: _IDF) -> _IDF: ...


class _TextTagger(_Tagger[str]):
    """An abstract base class for taggers in the text format."""

    __slots__ = ()

    @abstractmethod
    def _tagged(self, model: str) -> str: ...


class _Modifier(ABC, Generic[_MK_contra, _MV_co]):
    """An abstract base class for input modifiers."""

    __slots__ = (
        "_bounds",
        "_distribution",
        "_is_ctrl",
        "_is_noise",
        "_tagger",
        "_name",
        "_index",
        "_label",
    )

    _bounds: tuple[float, float]
    _distribution: SupportsPPF
    _is_ctrl: bool
    _is_noise: bool
    _tagger: AnyTagger | None
    _name: str
    _index: int
    _label: str

    @abstractmethod
    def __init__(
        self,
        bounds: tuple[float, float],
        distribution: SupportsPPF,
        is_noise: bool,
        tagger: AnyTagger | None,
        name: str,
    ) -> None:
        self._bounds = bounds
        self._distribution = distribution
        self._is_ctrl = not is_noise  # FunctionalModifier is neither, overwrites later
        self._is_noise = is_noise
        self._tagger = tagger
        self._name = name

    @abstractmethod
    def __call__(self, key: _MK_contra) -> _MV_co: ...

    @abstractmethod
    def _check_args(self) -> None:
        # called by _InputManager
        # as FunctionalModifier needs the index info assigned by _InputManager

        low, high = self._bounds
        distribution_low, distribution_high = self._distribution.support()

        if low > high:
            raise ValueError(f"the low '{low}' is greater than the high '{high}'.")

        if math.isinf(distribution_low) or math.isinf(distribution_high):
            warnings.warn(
                f"the support of the distribution is infinite: '{self._distribution}'.",
                stacklevel=2,
            )
        elif distribution_low != low or distribution_high != high:
            raise ValueError(
                f"the support of the distribution is inconsistent: '{self._distribution}'."
            )

    def _detagged(self, tagged_model: str, *values: _SupportsStr) -> str:
        if self._tagger is None:
            # TODO: tagger `input` is allowed to be None in airallergy/sober#8
            #       but since EP decoupling has not finished at this stage
            #       tagger being None is still not implemented
            # TODO: maybe a void tagger is a better idea than allowing None
            raise NotImplementedError

        return self._tagger._detagged(tagged_model, *values)

    @abstractmethod
    def _key_icdf(self, *quantiles: float) -> tuple[float, ...]:
        # NOTE: scipy rv_discrete ppf does not convert to int, but rvs does
        #       this surprising behaviour is handled manually
        return tuple(self._distribution.ppf(quantiles).tolist())  # type: ignore[arg-type]  # numpy/scipy typing is not quite there

    def _hype_ctrl_key(self) -> int:
        assert not self._is_ctrl
        return 0  # assuming the hype ctrl is an integral variable with one item

    @abstractmethod
    def _hype_ctrl_value(self) -> _MV_co: ...

    def _hype_ctrl_len(self) -> int:
        assert not self._is_ctrl
        return 1  # assuming the hype ctrl is an integral variable with one item


class _RealModifier(_Modifier[float, float]):
    """An abstract base class for input modifiers of real variables."""

    __slots__ = ()

    @abstractmethod
    def __init__(
        self,
        bounds: tuple[float, float],
        distribution: SupportsPPF | None,
        is_noise: bool,
        tagger: AnyTagger | None,
        name: str,
    ) -> None:
        if distribution is None:
            low, high = bounds
            distribution = scipy.stats.uniform(loc=low, scale=high - low)

        super().__init__(bounds, distribution, is_noise, tagger, name)

    def __call__(self, key: float) -> float:
        return key

    def _key_icdf(self, *quantiles: float) -> tuple[float, ...]:
        return super()._key_icdf(*quantiles)

    def _hype_ctrl_value(self) -> float:
        assert not self._is_ctrl
        return _Noise("(...)")


class _IntegralModifier(_Modifier[int, _MV_co]):
    """An abstract base class for input modifiers of integral variables."""

    __slots__ = ("_options",)

    _options: tuple[_MV_co, ...]

    @abstractmethod
    def __init__(
        self,
        options: tuple[_MV_co, ...],
        distribution: SupportsPPF | None,
        is_noise: bool,
        tagger: AnyTagger | None,
        name: str,
    ) -> None:
        self._options = options

        bounds = (0, len(self) - 1)

        if distribution is None:
            low, high = bounds
            distribution = scipy.stats.randint(low=low, high=high + 1)

        super().__init__(bounds, distribution, is_noise, tagger, name)

    def __iter__(self) -> Iterator[_MV_co]:
        yield from self._options

    def __len__(self) -> int:
        return len(self._options)

    def __getitem__(self, key: int, /) -> _MV_co:
        return self._options[key]

    def __call__(self, key: int) -> _MV_co:
        return self[key]

    def _key_icdf(self, *quantiles: float) -> tuple[int, ...]:
        return tuple(map(int, super()._key_icdf(*quantiles)))

    def _hype_ctrl_value(self) -> _MV_co:
        # FunctionalModifier overwrites later
        assert not self._is_ctrl
        return _Noise("{...}")


#############################################################################
#######                        TAGGER CLASSES                         #######
#############################################################################
class IndexTagger(_IDFTagger):
    """Tag regular commands by indexing.

    This tagger locates the EnergyPlus field to be modified through indexing, which is
    informed by an index trio comprising the class name, the object name and the
    field name. Multiple index trios can be specified to modify multiple EnergyPlus
    fields with the same value.

    Currently, tagging inside macro files are not supported.

    Parameters
    ----------
    *index_trios : iterables of str
        Single or multiple index trios.
    """

    __slots__ = ("_index_trios",)

    _index_trios: tuple[tuple[str, str, str], ...]

    def __init__(self, /, *index_trios: Iterable[str]) -> None:
        _index_trios = tuple(map(tuple, index_trios))

        if any(len(item) != 3 for item in _index_trios):
            raise ValueError(
                "each index trio should contain exactly three elements: class_name, object_name, field_name."
            )

        # cast: python/mypy#4573, python/mypy#7853, below works already
        # >>> x = _index_trios[0]
        # >>> assert len(x) == 3
        # >>> reveal_type(x)  # x: tuple[str, str, str]
        _index_trios = cast("tuple[tuple[str, str, str], ...]", _index_trios)

        # remove duplicate trios
        self._index_trios = tuple(set(_index_trios))

        super().__init__(*self._index_trios)

    def _tagged(self, model: _IDF) -> _IDF:
        for (class_name, object_name, field_name), tag in zip(
            self._index_trios, self._tags, strict=True
        ):
            obj = model.getobject(class_name, object_name)
            if obj is None:
                raise ValueError(f"object is not found in the model: '{object_name}'.")
                # eppy throws a proper error for unknown field names

            obj[makefieldname(field_name)] = tag
        return model


class StringTagger(_TextTagger):
    """Tag regular and macro commands by string replacement.

    This tagger locates the regular or the macro command to be modified through string
    replacement, which is informed by an string trio comprising the string, the prefix
    and the suffix. Multiple string trios can be specified to modify multiple regular or
    macro commands with the same value.

    The prefix and the suffix are useful to delimit the right string to be replaced,
    when the string itself is not unique in the EnergyPlus model.

    Currently, tagging inside macro files are not supported.

    Parameters
    ----------
    *string_trios : iterables of str
        Single or multiple string trios.
    """

    __slots__ = ("_string_trios",)

    _string_trios: tuple[tuple[str, str, str], ...]

    def __init__(self, /, *string_trios: Iterable[str]) -> None:
        _string_trios = tuple(map(tuple, string_trios))

        if any(len(item) == 0 for item in _string_trios):
            raise ValueError(
                "each string trio should contain at least one element: string."
            )
        if any(len(item) > 3 for item in _string_trios):
            raise ValueError(
                "each string trio should contain at most three elements: string, prefix, suffix."
            )

        # assign empty string to prefix/suffix if absent
        _string_trios = tuple(item + ("",) * (3 - len(item)) for item in _string_trios)

        # cast: python/mypy#4573, python/mypy#7853 may help, but the above assignment is too dynamic
        _string_trios = cast("tuple[tuple[str, str, str], ...]", _string_trios)

        # remove duplicate trios
        self._string_trios = tuple(set(_string_trios))

        super().__init__(*self._string_trios)

    def _tagged(self, model: str) -> str:
        for (string, prefix, suffix), tag in zip(
            self._string_trios, self._tags, strict=True
        ):
            delimited_string = prefix + string + suffix

            if delimited_string not in model:
                raise ValueError(
                    f"delimited string is not found in the model: '{delimited_string}'."
                )

            model = model.replace(delimited_string, prefix + tag + suffix)
        return model


#############################################################################
#######                       MODIFIER CLASSES                        #######
#############################################################################
class WeatherModifier(_IntegralModifier[Path]):
    """Modify the weather input variable.

    Parameters
    ----------
    *options : strs or path-like objects
        Single or multiple options.
    distribution : SupportsPPF, optional
        Probability distribution defined by `scipy`.
    is_noise : bool, optional
        Whether the variable is uncertain.
    name : str, optional
        Variable name.
    """

    __slots__ = ()

    def __init__(
        self,
        *options: AnyStrPath,
        distribution: SupportsPPF | None = None,
        is_noise: bool = False,
        name: str = "",
    ) -> None:
        super().__init__(
            tuple(_parsed_path(item, "weather file") for item in options),
            distribution,
            is_noise,
            None,
            name,
        )

    def _check_args(self) -> None:
        super()._check_args()

        for item in self._options:
            # check suffix
            if item.suffix != ".epw":
                raise ValueError(f"'{item}' is no epw file.")


class ContinuousModifier(_RealModifier):
    """Modify a continuous input variable.

    Parameters
    ----------
    low : float
        Lower limit.
    high : float
        Upper limit.
    distribution : SupportsPPF, optional
        Probability distribution defined by `scipy`.
    is_noise : bool, optional
        Whether the variable is uncertain.
    tagger : Tagger, optional
        A tagger object.
    name : str, optional
        Variable name.
    """

    __slots__ = ()

    def __init__(
        self,
        low: float,
        high: float,
        /,
        *,
        distribution: SupportsPPF | None = None,
        is_noise: bool = False,
        tagger: AnyTagger | None = None,
        name: str = "",
    ) -> None:
        super().__init__((low, high), distribution, is_noise, tagger, name)

    def _check_args(self) -> None:
        super()._check_args()

        low, high = self._bounds
        if low == high:
            raise ValueError(f"the low '{low}' is equal to the high '{high}'.")


class DiscreteModifier(_IntegralModifier[float]):
    """Modify a discrete input variable.

    Parameters
    ----------
    *options : floats
        Single or multiple options.
    distribution : SupportsPPF, optional
        Probability distribution defined by `scipy`.
    is_noise : bool, optional
        Whether the variable is uncertain.
    tagger : Tagger, optional
        A tagger object.
    name : str, optional
        Variable name.
    """

    __slots__ = ()

    def __init__(
        self,
        *options: float,
        distribution: SupportsPPF | None = None,
        is_noise: bool = False,
        tagger: AnyTagger | None = None,
        name: str = "",
    ) -> None:
        super().__init__(options, distribution, is_noise, tagger, name)

    def _check_args(self) -> None:
        super()._check_args()


class CategoricalModifier(_IntegralModifier[str]):
    """Modify a categorical input variable.

    Parameters
    ----------
    *options : floats
        Single or multiple options.
    distribution : SupportsPPF, optional
        Probability distribution defined by `scipy`.
    is_noise : bool, optional
        Whether the variable is uncertain.
    tagger : Tagger, optional
        A tagger object.
    name : str, optional
        Variable name.
    """

    __slots__ = ()

    def __init__(
        self,
        *options: str,
        distribution: SupportsPPF | None = None,
        is_noise: bool = False,
        tagger: AnyTagger | None = None,
        name: str = "",
    ) -> None:
        super().__init__(options, distribution, is_noise, tagger, name)

    def _check_args(self) -> None:
        super()._check_args()


class FunctionalModifier(_IntegralModifier[AnyModelModifierValue]):
    """Modify a functional input variable.

    This modifier is useful to define dependent input variables.

    Parameters
    ----------
    func : _AnyFunc
        A function that takes a tuple of input values as the argument and returns an
        input value.
    input_indices : iterable of int
        Coincident input indices to input values passed into `func`.
    func_kwargs : dict, optional
        Additional keyword arguments passed into `func`.
    tagger : Tagger, optional
        A tagger object.
    name : str, optional
        Variable name.
    """

    __slots__ = ("_func", "_input_indices", "_func_kwargs")

    _func: _AnyFunc
    _input_indices: tuple[int, ...]
    _func_kwargs: dict[str, object]  # TODO: restrict this for serialisation

    def __init__(
        self,
        func: _AnyFunc,
        /,
        input_indices: Iterable[int],
        func_kwargs: dict[str, object] | None = None,
        *,
        tagger: AnyTagger | None = None,
        name: str = "",
    ) -> None:
        self._func = func
        self._input_indices = tuple(input_indices)
        self._func_kwargs = {} if func_kwargs is None else func_kwargs

        func_name = f"<function {self._func.__module__ + '.' + self._func.__code__.co_qualname}>"
        super().__init__((func_name,), None, False, tagger, name)

        self._is_ctrl = False

    def __call__(  # noqa: D102  # astral-sh/ruff#8085
        self, key: object, *input_values: AnyModifierValue
    ) -> AnyModelModifierValue:
        del key
        # NOTE: 'key' is (should be) never used
        #       it is technically int, but typed as object to avoid a few casts in loops
        return self._func(input_values, **self._func_kwargs)

    def _check_args(self) -> None:
        super()._check_args()

        if any(item >= self._index for item in self._input_indices):
            raise ValueError(
                f"only previous inputs can be referred to: {self._index}, {self._input_indices}."
            )

    def _hype_ctrl_value(self) -> AnyModelModifierValue:
        # assert not self._is_ctrl  # no need, as hardcoded in __init__
        return self._options[0]
