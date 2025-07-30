from __future__ import annotations

from typing import TYPE_CHECKING

from dag_modelling.core.exception import InitializationError
from dag_modelling.core.output import Output
from dag_modelling.parameters import Parameter
from dag_modelling.tools.logger import Logger, get_logger

from .fit_result import FitResult
from .minimizable import Minimizable

# if we cannot import runtime_error from root we use DagModellingError to avoid any exception capture,
# i.e., if CppRuntimeError==DagModellingError, the exception will be not raised
try:
    import ROOT  # fmt: skip
    CppRuntimeError = ROOT.std.runtime_error
except Exception:
    from dag_modelling.core.exception import DagModellingError  # fmt:skip
    CppRuntimeError = DagModellingError

if TYPE_CHECKING:
    from typing import Any


class MinimizerBase:
    __slots__ = (
        "_name",
        "_label",
        "_minimizable",
        "_minimizer",
        "_parameters",
        "_parameters_names",
        "_result",
        "_statistic",
        "_limits",
        "_verbose",
        "_nbins",
        "_logger",
        "_initial_parameters",
    )

    _name: str
    _label: str
    _minimizable: Minimizable | None
    _parameters: dict[str, Parameter]
    _parameters_names: list[str]
    _result: dict
    _minimizer: Any
    _verbose: bool
    _statistic: Output
    _limits: dict[str, tuple[float | None, float | None]]
    _nbins: int
    _logger: Logger
    _initial_parameters: dict[Parameter, float] | None

    def __init__(
        self,
        statistic: Output,
        parameters: dict[str, Parameter],
        name: str,
        label: str,
        verbose: bool = False,
        logger: Logger | None = None,
        *,
        limits: dict[str, tuple[float | None, float | None]] = {},
        nbins: int = 0,
    ):
        if not isinstance(statistic, Output):
            raise InitializationError(
                f"arg 'statistic' must be an Output, but given {type(statistic)=}, {statistic=}."
            )
        self._statistic = statistic
        self._initial_parameters = {}

        self._parameters = []  # pyright: ignore
        self._parameters_names = []  # pyright: ignore
        if parameters:
            if not isinstance(parameters, dict):
                raise InitializationError(
                    f"'parameters' must be a dict of (str, Parameter), but given {parameters=},"
                    f" {type(parameters)=}!"
                )
            for parameter_name, parameter in parameters.items():
                self.append_name_par(parameter_name, parameter)
                self.copy_initial_values(parameter)

        if isinstance(logger, Logger):
            self._logger = logger
        elif logger is not None:
            raise InitializationError(f"Cannot initialize a Minimizable class with logger={logger}")
        else:
            self._logger = get_logger()

        self._limits = limits

        self._name = name
        self._label = label
        self._verbose = verbose
        self._nbins = nbins
        self._minimizable = None

    @property
    def statistic(self) -> Output:
        return self._statistic

    @property
    def name(self) -> str:
        return self._name

    @property
    def label(self) -> str:
        return self._label

    @property
    def logger(self) -> Logger:
        return self._logger

    @statistic.setter
    def statistic(self, statistic) -> None:
        self._statistic = statistic
        self._minimizable = None

    @property
    def parameters(self) -> list[Parameter]:
        return self._parameters

    @property
    def parameters_names(self) -> list[str]:
        return self._parameters_names

    @property
    def result(self) -> dict:
        return self._result

    @property
    def nbins(self) -> int:
        return self._nbins

    @property
    def npars_free(self) -> int:
        """Return number of free parameters.

        Note
        ----
        It calculates the number of parameters that are considered free at the
        time of initialization. However, if the statistic depends on nuisance
        parameters but does not include pull terms for those parameters, then
        those constrained parameters are not counted as free parameters.

        Returns
        -------
        int
            Number of free parameters.
        """
        return sum(par._parent.is_free for par in self.parameters)

    @property
    def npars_constrained(self) -> int:
        """Return number of constrained parameters.

        Note
        ----
        It calculates the number of parameters that are constrained at the time
        of initialization. However, if the statistic does not include pull terms
        for a parameter, that parameter will be treated as a nuisance parameter.

        Returns
        -------
        int
            Number of constrained parameters.
        """
        return len(self.parameters) - self.npars_free

    def copy_initial_values(self, par: Parameter) -> None:
        self._initial_parameters.update({par: par.value.copy()})

    def push_initial_values(self) -> None:
        for par, value in self._initial_parameters.items():
            par.push(value)

    def append_name_par(self, name: str, par: Parameter) -> None:
        for obj, otype in ((name, str), (par, Parameter)):
            if not isinstance(obj, otype):
                raise RuntimeError(f"'{obj}' must be a {otype}, but given {par=}, {type(par)=}!")
        self._parameters.append(par)
        self._parameters_names.append(name)

    def fit(self, **kwargs) -> dict:
        if len(self.parameters) == 0:
            return self.evalstatistic()
        return self._child_fit(**kwargs)

    def evalstatistic(self) -> dict:
        with FitResult() as fr:
            fun = self._statistic.data

        fr.set(
            x=[],
            errors=[],
            fun=fun,
            success=True,
            summary="stastitics evaluation (no parameters)",
            minimizer="none",
            nfev=1,
        )
        self._result = fr.result
        self.patchresult()

        return self.result

    def _child_fit(self, **_) -> dict:
        raise NotImplementedError("The method must be overriden!")

    def patchresult(self) -> None:
        names = self.parameters_names
        result = self._result
        result["npars"] = len(self.parameters)
        result["names"] = names
        result["xdict"] = dict(zip(names, (float(x) for x in self.result["x"])))
        if self.result["errors"] is not None:
            result["errorsdict"] = dict(zip(names, (float(e) for e in self.result["errors"])))
        else:
            result["errorsdict"] = {}
        result["nbins"] = self.nbins
        result["npars_free"] = self.npars_free
        result["npars_constrained"] = self.npars_constrained
        result["ndof"] = self.nbins - self.npars_free
        result["statistic_name"] = self.statistic.node.name

    def init_minimizable(self) -> Minimizable:
        if self._minimizable is None:
            self._minimizable = Minimizable(
                self.statistic, verbose=self._verbose, logger=self._logger
            )
            for par in self.parameters:
                self._minimizable.append_par(par)
        return self._minimizable
