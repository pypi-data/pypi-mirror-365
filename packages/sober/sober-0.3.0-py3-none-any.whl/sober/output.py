"""Classes for defining outputs."""

from __future__ import annotations

import enum
import itertools as it
import json
import math
import os
import shutil
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import sober.config as cf
from sober._simulator import _run_readvars
from sober._tools import _parsed_path, _parsed_str_iterable, _run, _uuid

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path
    from typing import Any, Final, Literal

    from sober._typing import AnyCoreLevel, AnyLanguage, AnyStrPath

    type _AnyObjectiveDirection = Literal["minimise", "maximise"]
    type _AnyConstraintBounds = tuple[float, float]
    type _AnyEPOutputType = Literal["variable", "meter"]

    # TODO: below goes to tests when made
    # assert [
    #     item.upper() for item in get_args(_AnyObjectiveDirection)
    # ] == _ObjectiveDirection._member_names_
    # assert [
    #     item.upper() for item in get_args(_AnyEPOutputType)
    # ] == _EPOutputType._member_names_


@enum.unique
class _ObjectiveDirection(enum.IntEnum):
    MINIMISE = 1
    MAXIMISE = -1


@enum.unique
class _EPOutputType(enum.StrEnum):
    VARIABLE = "eplusout.eso"
    METER = "eplusout.mtr"


#############################################################################
#######                     ABSTRACT BASE CLASSES                     #######
#############################################################################
class _Collector(ABC):
    """An abstract base class for output collector."""

    __slots__ = (
        "_filename",
        "_level",
        "_objectives",
        "_constraints",
        "_objective_direction",
        "_constraint_bounds",
        "_is_final",
        "_is_copied",
    )

    _filename: str
    _level: AnyCoreLevel
    _objectives: tuple[str, ...]
    _constraints: tuple[str, ...]
    _objective_direction: _ObjectiveDirection
    _constraint_bounds: _AnyConstraintBounds
    _is_final: bool
    _is_copied: bool

    @abstractmethod
    def __init__(
        self,
        filename: str,
        level: AnyCoreLevel,
        objectives: str | Iterable[str],
        constraints: str | Iterable[str],
        objective_direction: _AnyObjectiveDirection,
        constraint_bounds: _AnyConstraintBounds,
        is_final: bool,
    ) -> None:
        self._filename = filename
        self._level = level
        self._objectives = _parsed_str_iterable(objectives, "objectives")
        self._constraints = _parsed_str_iterable(constraints, "constraints")
        self._objective_direction = _ObjectiveDirection[objective_direction.upper()]
        self._constraint_bounds = constraint_bounds
        self._is_final = is_final
        self._is_copied = False

    @abstractmethod
    def __call__(self, cwd: Path) -> None: ...

    @abstractmethod
    def _check_args(self) -> None:
        if self._objectives:
            if (self._level != "job") and (not self._is_copied):
                raise ValueError(
                    f"a collector containing objectives needs to be at the 'job' level: {self._filename}."
                )

            if not self._is_final:
                raise ValueError(
                    f"a collector containing objectives needs to be final: {self._filename}."
                )

        if self._constraints:
            if (self._level != "job") and (not self._is_copied):
                raise ValueError(
                    f"a collector containing constraints needs to be at the 'job' level: {self._filename}."
                )

            if not self._is_final:
                raise ValueError(
                    f"a collector containing constraints needs to be final: {self._filename}."
                )

            low, high = self._constraint_bounds
            if (
                (math.isnan(low) or math.isnan(high))
                or (math.isinf(low) and math.isinf(high))
                or (math.isinf(low) and low > 0)
                or (math.isinf(high) and high < 0)
                or (low >= high)
            ):
                raise ValueError(
                    f"invalid constraint bounds: {self._constraint_bounds}."
                )

        if self._is_final and (self._filename.split(".")[-1] != "csv"):
            raise ValueError(
                f"a final output needs to be a csv file: {self._filename}."
            )

    def _to_objective(self, value: float) -> float:
        # convert each objective to minimise
        return value * self._objective_direction.value

    def _to_constraint(self, value: float) -> float:
        # convert each constraint to <= 0
        low, high = self._constraint_bounds
        if math.isinf(low):
            return value - high
        elif math.isinf(high):
            return low - value
        else:
            # low <= value <= high
            # ==> - (high - low) / 2 <= value - (high + low) / 2 <= (high - low) / 2
            # ==> abs(2 < value - (high + low) / 2) <= (high - low) / 2
            return abs(value - (high + low) / 2) - (high - low) / 2


#############################################################################
#######                       COLLECTOR CLASSES                       #######
#############################################################################
class RVICollector(_Collector):
    """Collects outputs by RVI.

    This collector retrieves EnergyPlus simulation results defined by either
    `Output:Variable` or `Output:Meter` via the ReadVarsESO programme, the required RVI
    file is auto-generated.

    Parameters
    ----------
    ep_output_names : str or iterable of str
        EnergyPlus output names.
    ep_output_type : {'variable', 'meter'}
        EnergyPlus output type.
    filename : str
        Output filename, this must end with `.csv`.
    ep_output_keys : str or iterable of str, optional
        Specific names for EnergyPlus variable outputs, only applicable when
        `ep_output_type` is set to `variable`.
    ep_output_frequency : str, optional
        EnergyPlus output frequency.
    objectives : str or iterable of str, optional
        Optimisation objectives, which must match the output names in the output file.
    constraints : str or iterable of str, optional
        Optimisation constraints, which must match the output names in the output file.
    objective_direction : {'minimise', 'maximise'}, default: `'minimise'`
        Optimisation objective direction.
    constraint_bounds : tuple of float, default: `(-math.inf, 0)`
        Optimisation constraint bounds.
    is_final : bool, default: `True`
        Whether the output is final and recorded.
    """

    # TODO: consider switching to/adding EP native csv once NREL/EnergyPlus#9395

    __slots__ = (
        "_ep_output_names",
        "_ep_output_type",
        "_ep_output_keys",
        "_ep_output_frequency",
        "_rvi_file",
    )

    _ep_output_names: tuple[str, ...]
    _ep_output_type: _EPOutputType
    _ep_output_keys: tuple[str, ...]
    _ep_output_frequency: str
    _rvi_file: Path

    def __init__(
        self,
        ep_output_names: str | Iterable[str],
        ep_output_type: _AnyEPOutputType,
        filename: str,
        /,
        ep_output_keys: str | Iterable[str] = (),
        ep_output_frequency: str = "",
        *,
        objectives: str | Iterable[str] = (),
        constraints: str | Iterable[str] = (),
        objective_direction: _AnyObjectiveDirection = "minimise",
        constraint_bounds: _AnyConstraintBounds = (-math.inf, 0),
        is_final: bool = True,
    ) -> None:
        self._ep_output_names = _parsed_str_iterable(ep_output_names, "ep output names")
        self._ep_output_type = _EPOutputType[ep_output_type.upper()]
        self._ep_output_keys = _parsed_str_iterable(ep_output_keys, "ep output keys")
        self._ep_output_frequency = ep_output_frequency

        super().__init__(
            filename,
            "task",
            objectives,
            constraints,
            objective_direction,
            constraint_bounds,
            is_final,
        )

    def __call__(self, cwd: Path) -> None:  # noqa: D102  # astral-sh/ruff#8085
        _run_readvars(cwd, self._rvi_file, self._ep_output_frequency)

        # remove trailing space
        # with open(cwd / self._filename) as fp:
        #     lines = fp.read().splitlines()
        # with open(cwd / self._filename, "w") as fp:
        #     fp.write("\n".join(line.strip() for line in lines) + "\n")

    def _check_args(self) -> None:
        super()._check_args()

        if self._filename.split(".")[-1] != "csv":
            raise ValueError(
                f"an RVICollector output needs to be a csv file: {self._filename}."
            )

        if self._ep_output_type is _EPOutputType.METER and self._ep_output_keys:
            raise ValueError("meter variables do not accept keys.")

    def _touch(self, config_dir: Path) -> None:
        rvi_str = f"{self._ep_output_type.value}\n{self._filename}\n"
        if self._ep_output_keys:
            rvi_str += "\n".join(
                f"{key},{name}"
                for key, name in it.product(self._ep_output_keys, self._ep_output_names)
            )
        else:
            rvi_str += "\n".join(self._ep_output_names)

        rvi_str += "\n0\n"

        rvi_filestem = _uuid(type(self).__name__, *rvi_str.splitlines())
        self._rvi_file = config_dir / (rvi_filestem + ".rvi")
        with open(self._rvi_file, "w") as fp:
            fp.write(rvi_str)


class ScriptCollector(_Collector):
    """Collects outputs by script.

    This collector computes user-defined outputs by calling user-provided scripts, which
    can be used for either the task- or the job-level output collection. The task level
    usually deals with building performance metrics, whilst the job level can calculate
    robustness measures. A `loads_kwargs` method is provided to conveniently retrieve
    useful output-related data inside scripts.

    Currently only a Python script is supported.

    Parameters
    ----------
    script_file : str or path-like object
        Script file path.
    script_language : {'python'}
        Script language, whose executable path must be configured via `config_script`.
    filename : str
        Output filename.
    script_kwargs : dict, optional
        Additional keyword arguments passed into the script.
    level : {'task', 'job'}, default: `'task'`
        Output collection level.
    objectives : str or iterable of str, optional
        Optimisation objectives, which must match the output names in the output file.
    constraints : str or iterable of str, optional
        Optimisation constraints, which must match the output names in the output file.
    objective_direction : {'minimise', 'maximise'}, default: `'minimise'`
        Optimisation objective direction.
    constraint_bounds : tuple of float, default: `(-math.inf, 0)`
        Optimisation constraint bounds.
    is_final : bool, default: `True`
        Whether the output is final and recorded.

    Methods
    -------
    loads_kwargs
    """

    _RESERVED_KWARGS_KEYS: Final = frozenset(
        {"cwd", "filename", "objectives", "constraints"}
    )

    __slots__ = ("_script_file", "_script_language", "_script_kwargs")

    _script_file: Path
    _script_language: AnyLanguage
    _script_kwargs: dict[str, object]

    def __init__(
        self,
        script_file: AnyStrPath,
        script_language: AnyLanguage,
        filename: str,
        /,
        script_kwargs: dict[str, object] | None = None,
        *,
        level: AnyCoreLevel = "task",
        objectives: str | Iterable[str] = (),
        constraints: str | Iterable[str] = (),
        objective_direction: _AnyObjectiveDirection = "minimise",
        constraint_bounds: _AnyConstraintBounds = (-math.inf, 0),
        is_final: bool = True,
    ) -> None:
        self._script_file = _parsed_path(script_file, "script file")
        self._script_language = script_language
        self._script_kwargs = {} if script_kwargs is None else script_kwargs

        super().__init__(
            filename,
            level,
            objectives,
            constraints,
            objective_direction,
            constraint_bounds,
            is_final,
        )

    def __call__(self, cwd: Path) -> None:  # noqa: D102  # astral-sh/ruff#8085
        exec_language = cf._config["exec_" + self._script_language]  # type: ignore[literal-required]  # python/mypy#12554

        cmd_args = (exec_language, self._script_file, self._dumps_kwargs(cwd))

        _run(cmd_args, cwd)

    def _check_args(self) -> None:
        super()._check_args()

        for item in self._RESERVED_KWARGS_KEYS:
            if item in self._script_kwargs:
                raise ValueError(
                    f"'{item}' is reserved and cannot be used in script kwargs."
                )

    def _dumps_kwargs(self, cwd: Path) -> str:
        kwargs = {
            "cwd": os.fsdecode(cwd),
            "filename": self._filename,
            "objectives": self._objectives,
            "constraints": self._constraints,
        } | self._script_kwargs

        return json.dumps(kwargs)

    @staticmethod
    def loads_kwargs() -> Any:  # Any: typeshed  # pep728
        """Retrieve keyword arguments in scripts.

        Returns
        -------
        dict
            Keys of this dictionary are 'cwd', 'filename', 'objectives', 'constraints',
            in addition to any key in `script_kwargs`. If `level` is set to `'task'`,
            the current working directory is the task directory in which this script is
            executed, otherwise it is the job directory.
        """
        import sys

        return json.loads(sys.argv[1])


class _CopyCollector(_Collector):
    """Copy task final outputs as job final outputs.

    This is for handling non-noisy cases only.
    """

    __slots__ = ()

    def __init__(
        self,
        filename: str,
        objectives: tuple[str, ...],
        constraints: tuple[str, ...],
        objective_direction: _ObjectiveDirection,
        constraint_bounds: _AnyConstraintBounds,
        is_final: bool,
    ) -> None:
        # overwrite _Collector's __init__, as all args have been parsed
        self._filename = filename
        self._level = "job"
        self._objectives = objectives
        self._constraints = constraints
        self._objective_direction = objective_direction
        self._constraint_bounds = constraint_bounds
        self._is_final = is_final
        self._is_copied = False

    def __call__(self, cwd: Path) -> None:
        shutil.copyfile(cwd / "T0" / self._filename, cwd / self._filename)

    def _check_args(self) -> None:
        # all args have been checked
        pass
