"""Functions for configuring sober."""

from __future__ import annotations

import os
import platform
import sys
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, overload

import psutil

from sober._tools import _parsed_path

if TYPE_CHECKING:
    from typing import Final, Literal, TypedDict

    from sober._typing import AnyLanguage, AnyModelType, AnyStrPath

    class _RecordsFilenames(TypedDict):
        task: str
        job: str
        batch: str
        epoch: str

    class _Config(TypedDict, total=False):
        schema_energyplus: str
        exec_energyplus: str
        exec_epmacro: str
        exec_expandobjects: str
        exec_readvars: str
        exec_python: str
        n_processes: int

    type _AnyPathConfigName = Literal[
        "schema_energyplus",
        "exec_energyplus",
        "exec_epmacro",
        "exec_expandobjects",
        "exec_readvars",
        "exec_python",
    ]
    type _AnyIntConfigName = Literal["n_processes"]
    type _AnyConfigName = Literal[_AnyPathConfigName, _AnyIntConfigName]


_RECORDS_FILENAMES: Final[_RecordsFilenames] = {  # python/typing#1388
    "task": "task_records.csv",
    "job": "job_records.csv",
    "batch": "batch_records.csv",
    "epoch": "epoch_records.csv",  # not used
}

_config: _Config
_has_batches: bool  # dependent on analysis type (parametrics or optimisation)


def __getattr__(  # type: ignore[misc]  # python/mypy#8203
    name: Literal["_config"], /
) -> _Config:
    """Lazily set these attributes when they are called for the first time."""
    match name:
        case "_config":
            global _config

            _config = {}
            return _config
        case _:
            raise AttributeError(f"module '{__name__}' has no attribute '{name}'.")


#############################################################################
#######                    CONFIGURATION FUNCTIONS                    #######
#############################################################################
def _parsed_exec_filename(filename: str) -> str:
    if platform.system() == "Windows":
        filename += ".exe"
    return filename


def _set_config(config: _Config) -> None:
    """Set configuration.

    This helps copy configuration into child processes when using multiprocessing.
    """
    for name, value in config.items():
        _set_config_item(name, value)  # type: ignore[call-overload]  # python/mypy#7981


def _check_config(
    model_type: AnyModelType,
    has_templates: bool,
    has_rvis: bool,
    languages: frozenset[AnyLanguage],
) -> None:
    """Check the configuration sufficiency."""
    if "n_processes" not in _config:
        _config["n_processes"] = psutil.cpu_count(logical=False) - 1

    if model_type == ".imf" and ("exec_epmacro" not in _config):
        raise ValueError(
            f"a macro model is input, but the epmacro executable is not configured: {_config}."
        )

    if has_templates and ("exec_expandobjects" not in _config):
        raise ValueError(
            f"HVAC templates are used, but the expandobjects executable is not configured: {_config}."
        )

    if has_rvis and ("exec_readvars" not in _config):
        raise ValueError(
            f"an RVICollector is used, but the readvars executable is not configured: {_config}."
        )

    for item in languages:
        if "exec_" + item not in _config:
            raise ValueError(
                f"an ScriptCollector of {item} is used, but the {item} executable is not configured: {_config}."
            )


@overload
def _set_config_item(name: _AnyPathConfigName, value: Path) -> None: ...
@overload
def _set_config_item(name: _AnyIntConfigName, value: int) -> None: ...
def _set_config_item(name: _AnyConfigName, value: Path | int) -> None:
    if name in sys.modules[__name__]._config:  # pep562 usage
        is_equal = (
            os.path.samefile(_config[name], value)
            if isinstance(value, Path)
            else _config[name] == value
        )

        if not is_equal:
            warnings.warn(
                f"'{name}' has been configured to '{_config[name]}', and will be overriden by '{value}'.",
                stacklevel=2,
            )

    _config[name] = os.fsdecode(value) if isinstance(value, Path) else value


def _default_energyplus_root(major: str, minor: str, patch: str = "0") -> str:
    """Return the default EnergyPlus installation directory."""
    version = f"{major}-{minor}-{patch}"
    match platform.system():
        case "Linux":
            return f"/usr/local/EnergyPlus-{version}"
        case "Darwin":
            return f"/Applications/EnergyPlus-{version}"
        case "Windows":
            return rf"C:\EnergyPlusV{version}"
        case _ as system_name:
            raise NotImplementedError(f"unsupported system: '{system_name}'.")


def config_energyplus(
    *,
    version: str | None = None,
    root: AnyStrPath | None = None,
    schema_energyplus: AnyStrPath | None = None,
    exec_energyplus: AnyStrPath | None = None,
    exec_epmacro: AnyStrPath | None = None,
    exec_expandobjects: AnyStrPath | None = None,
    exec_readvars: AnyStrPath | None = None,
) -> None:
    """Configure EnergyPlus-related file paths.

    Three methods to find these paths are available.

    1. If `version` is specified, the default EnergyPlus installation directory on the
    current operating system will be used to find all paths.
    2. If `version` is not specified and `root` is specified, the user-specified
    EnergyPlus installation directory will be used to find all paths.
    3. If neither `version` nor `root` is specified, each path can be specified
    separately, where `schema_energyplus` and `exec_energyplus` are mandatory.

    Parameters
    ----------
    version : str, optional
        EnergyPlus version.
    root : str or path-like object, optional
        EnergyPlus installation directory path.
    schema_energyplus : str or path-like object, optional
        Energy+.idd file path.
    exec_energyplus : str or path-like object, optional
        EnergyPlus executable path.
    exec_epmacro : str or path-like object, optional
        EPMacro executable path.
    exec_expandobjects : str or path-like object, optional
        ExpandObjects executable path.
    exec_readvars : str or path-like object, optional
        ReadVarsESO executable path.
    """
    # TODO: change this to non-mandatory when metamodelling is supported

    if version is not None:
        root = _default_energyplus_root(*version.split("."))

    if root is not None:
        root = _parsed_path(root, "energyplus root")
        schema_energyplus = root / "Energy+.idd"
        exec_energyplus = root / _parsed_exec_filename("energyplus")
        exec_epmacro = root / _parsed_exec_filename("EPMacro")
        exec_expandobjects = root / _parsed_exec_filename("ExpandObjects")
        exec_readvars = root / "PostProcess" / _parsed_exec_filename("ReadVarsESO")

    if (schema_energyplus is None) or (exec_energyplus is None):
        raise ValueError(
            "one of 'version', 'root' or 'schema_energyplus & exec_energyplus' needs to be provided."
        )

    _set_config_item(
        "schema_energyplus", _parsed_path(schema_energyplus, "energyplus schema")
    )
    _set_config_item(
        "exec_energyplus", _parsed_path(exec_energyplus, "energyplus executable")
    )

    if exec_epmacro is not None:
        _set_config_item(
            "exec_epmacro", _parsed_path(exec_epmacro, "epmacro executable")
        )
    if exec_expandobjects is not None:
        _set_config_item(
            "exec_expandobjects",
            _parsed_path(exec_expandobjects, "expandobjects executable"),
        )
    if exec_readvars is not None:
        _set_config_item(
            "exec_readvars", _parsed_path(exec_readvars, "readvars executable")
        )


def config_parallel(*, n_processes: int | None = None) -> None:
    """Configure parallel-related settings.

    Parameters
    ----------
    n_processes : int, optional
        Number of prcesses to be parallelised, default is the total number of
        accessible CPU cores minus one.
    """
    if n_processes is not None:
        _set_config_item("n_processes", n_processes)


def config_script(*, exec_python: AnyStrPath | None = None) -> None:
    """Configure script language paths.

    Parameters
    ----------
    exec_python : str or path-like object, optional
        Python executable path, which can be obtained by `sys.executable`.
    """
    if exec_python is not None:
        _set_config_item("exec_python", _parsed_path(exec_python, "python executable"))
