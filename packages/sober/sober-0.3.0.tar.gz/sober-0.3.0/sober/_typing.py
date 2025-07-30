from os import PathLike
from typing import TYPE_CHECKING, Literal

##############################  package typing  ##############################
# need to remove casts etc. to resolve this block

# python
type AnyStrPath = str | PathLike[str]


# input
type AnyModifierKey = float | int
type AnyModelModifierValue = float | str
type AnyModifierValue = AnyStrPath | AnyModelModifierValue

## this contains hype ctrl keys only used for populating jobs
type AnyCtrlKeyVec = tuple[int, *tuple[AnyModifierKey, ...]]
#############################################################################


if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path
    from typing import NotRequired, Protocol, TypedDict, TypeVar

    import numpy as np
    from numpy.typing import NDArray

    from sober.input import (
        CategoricalModifier,
        ContinuousModifier,
        DiscreteModifier,
        FunctionalModifier,
        _IDFTagger,
        _IntegralModifier,
        _RealModifier,
        _TextTagger,
    )

    # python
    type AnyCmdArgs = tuple[AnyStrPath, ...]

    # input
    RVV = TypeVar("RVV", np.double, np.int_)  # AnyRandomVarValue

    class SupportsPPF(Protocol):
        # NOTE: not yet seeing a benefit differing float and int
        __slots__ = ()

        def support(self) -> tuple[RVV, RVV]: ...
        def ppf(self, q: Iterable[float]) -> NDArray[np.double]: ...

    type AnyTagger = _IDFTagger | _TextTagger
    type AnyModifier = _RealModifier | _IntegralModifier[AnyModifierValue]

    ## TODO: use Intersection after python/typing#213
    type AnyIntegralModelModifier = (
        DiscreteModifier | CategoricalModifier | FunctionalModifier
    )
    type AnyRealModelModifier = ContinuousModifier
    type AnyModelModifier = AnyRealModelModifier | AnyIntegralModelModifier

    # output
    type AnyCoreLevel = Literal["task", "job"]
    type AnyLevel = Literal[AnyCoreLevel, "batch", "epoch"]

    # io managers
    type AnyModelTask = tuple[AnyModelModifierValue, ...]
    type AnyTask = tuple[Path, *AnyModelTask]
    type AnyTaskItem = tuple[str, AnyTask]
    type AnyJob = tuple[AnyTaskItem, ...]
    type AnyJobItem = tuple[str, AnyJob]
    type AnyBatch = tuple[AnyJobItem, ...]
    type AnyUIDs = tuple[str, ...]

    # problem
    type AnySampleMode = Literal["elementwise", "cartesian", "auto"]

    # config
    type AnyModelType = Literal[".idf", ".imf"]
    type AnyLanguage = Literal["python"]

    class ElementwiseNoiseSampleKwargs(TypedDict):
        mode: Literal["elementwise"]
        size: int
        method: Literal["random", "latin hypercube"]
        seed: NotRequired[int]

    class CartesianNoiseSampleKwargs(TypedDict):
        mode: Literal["cartesian"]

    class AutoNoiseSampleKwargs(TypedDict):
        mode: Literal["auto"]
        size: NotRequired[int]
        method: NotRequired[Literal["random", "latin hypercube"]]
        seed: NotRequired[int]

    type NoiseSampleKwargs = (
        ElementwiseNoiseSampleKwargs
        | CartesianNoiseSampleKwargs
        | AutoNoiseSampleKwargs
    )

    # pymoo
    type AnyX = dict[str, np.int_ | np.double]
    type AnyF = NDArray[np.double]
    type AnyG = NDArray[np.double]
    type AnyReferenceDirections = NDArray[np.double]
