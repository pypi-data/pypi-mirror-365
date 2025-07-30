from math import sqrt

from dag_modelling.lib.statistics import Chi2, CNPStat, MonteCarlo
from dag_modelling.core.graph import Graph
from dag_modelling.core.input import Input
from dag_modelling.lib.abstract import OneToOneNode
from dag_modelling.lib.common import Array
from dag_modelling.parameters import Parameters
from dag_modelling.plot.graphviz import savegraph
from dag_modelling.plot.plot import plot_array_1d
from matplotlib import pyplot as plt
from numpy import allclose, array, linspace
from numpy.random import MT19937, Generator, SeedSequence
from pytest import mark
from scipy.stats import norm

from dgm_fit.iminuit_minimizer import IMinuitMinimizer

_NevScale = 10000


class Model(OneToOneNode):
    __slots__ = ("_mu", "_sigma", "_const")
    _mu: Input
    _sigma: Input
    _const: Input

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mu = self._add_input("mu", positional=False)
        self._sigma = self._add_input("sigma", positional=False)
        self._const = self._add_input("const", positional=False)

    def _function(self):
        mu = self._mu.data[0]
        sigma = self._sigma.data[0]
        const = self._const.data[0]
        for indata, outdata in zip(self.inputs.iter_data(), self.outputs.iter_data_unsafe()):
            outdata[:] = _NevScale * norm.pdf(indata[:], loc=mu, scale=sigma) + const


@mark.parametrize("corr", (False, True))
@mark.parametrize(
    "mu,sigma,const,mu_limits",
    (
        (-1.531654, 0.567543, 10, None),
        (2.097123, 1.503321, 20, (-5, None)),
        (-1.531654, 0.567543, 30, (None, 5)),
        (2.097123, 1.503321, 40, (-5, 5)),
    ),
)
@mark.parametrize("mode", ("asimov", "normal-stats"))
@mark.parametrize("verbose", (False, True))
def test_IMinuitMinimizer(corr, mu, sigma, const, mu_limits, mode, verbose: bool, testname):
    size = 201
    x = linspace(-10, 10, size)

    # start values of the fitting
    mu_fit = mu - 0.3 * sigma
    sigma_fit = sigma * 1.1
    const_fit = const * 1.1
    with Graph(close_on_exit=True) as graph:
        # setting of true parameters
        Mu0 = Array("mu 0", [mu], mode="fill")
        Sigma0 = Array("sigma 0", [sigma], mode="fill")
        Const0 = Array("const 0", [const], mode="fill")
        X = Array("x", x, mode="fill")

        # build input data for the MC simulation
        pdf0 = Model("normal pdf for MC")
        X >> pdf0
        Mu0 >> pdf0("mu")
        Sigma0 >> pdf0("sigma")
        Const0 >> pdf0("const")
        model = pdf0.outputs[0]

        # perform fluctuations of data within MC and shift the result with constant background
        (sequence,) = SeedSequence(0).spawn(1)
        gen = Generator(MT19937(sequence))
        mc = MonteCarlo("MC", mode=mode, generator=gen)
        model >> mc

        # build a model to fit exp data
        pars = Parameters.from_numbers(
            [mu_fit, sigma_fit, const_fit],
            names=["mu_fit", "sigma_fit", "const_fit"],
            sigma=[1, 1, 1],
            correlation=[[1, -0.95, 0], [-0.95, 1, 0], [0, 0, 1]] if corr else None,
        )
        MuFit, SigmaFit, ConstFit = pars.outputs()
        # MuFit = Array("mu fit", [mufit], mode="fill")
        # SigmaFit = Array("sigma fit", [sigmafit], mode="fill")
        pdf_fit = Model("normal pdf for the Model")
        X >> pdf_fit
        MuFit >> pdf_fit("mu")
        SigmaFit >> pdf_fit("sigma")
        ConstFit >> pdf_fit("const")

        # eval errors
        cnp = CNPStat("CNP stat")
        (mc, pdf_fit) >> cnp

        # eval Chi2
        chi = Chi2("Chi2")
        mc >> chi("data")
        pdf_fit >> chi("theory")
        cnp.outputs[0] >> chi("errors")

    # check if the MC data is valid: negative events -> wrong model
    assert min(mc.outputs[0].data) >= 0

    limits = {}
    if mu_limits:
        limits["mu"] = mu_limits

    # perform a minimization
    par_mu, par_sigma, par_const = pars.parameters
    minimizer = IMinuitMinimizer(
        statistic=chi.outputs[0],
        parameters={
            "mu": par_mu,
            "sigma": par_sigma,
            "const": par_const,
        },
        limits=limits,
        verbose=verbose,
    )
    res = minimizer.fit()

    assert res["success"]
    assert res["nfev"] > 1

    names = res["names"]
    assert (
        len(res["x"])
        == len(names)
        == len(res["errorsdict"])
        == len(res["errors"])
        == len(res["xdict"])
        == res["npars"]
        == 3
    )

    atol = 2.0 / sqrt(_NevScale)
    res_fit = [mu, sigma, const]
    assert allclose(
        res["x"][:2],
        res_fit[:2],
        rtol=0,
        atol=atol if mode == "normal-stats" else 2e-5,
    )
    assert allclose(
        res["x"][2:],
        res_fit[2:],
        rtol=0,
        atol=0.55 if mode == "normal-stats" else 4.0e-3,
    )
    rel_dev = (res["x"] - res_fit) / res["errors"]
    assert allclose(
        rel_dev,
        0,
        rtol=0,
        atol=2 if mode == "normal-stats" else 1.0e-2,
    )
    if mode == "asimov":
        assert res["fun"] < 0.1
    assert allclose(
        res["covariance"],
        minimizer.calculate_covariance(),
        rtol=0,
        atol=mode == "asimov" and 1e-6 or 1.0e-5,
    )
    assert all(res["errorsdict"][key] == res["errors"][i] for i, key in enumerate(names))

    # errors checks
    errors = minimizer.profile_errors()
    assert errors["names"] == names
    errs = array(errors["errors"])
    assert allclose(errs[:, 1], res["errors"], atol=4e-3)
    assert allclose(-errs[:, 0], res["errors"], atol=4e-3)
    assert all((errors["errorsdict"][key] == errs[i]).all() for i, key in enumerate(names))
    for name in names:
        for key in ("is_valid", "lower_valid", "upper_valid"):
            assert errors["errors_profile_status"][name][key]
        assert errors["errors_profile_status"][name]["message"] == ""

    # save plot and graph
    draw_params(res["x"], mu, sigma, minimizer, f"output/{testname}-params.png")
    draw_fit(x, mc, model, pdf_fit.outputs[0], mode, f"output/{testname}-plot.png")
    savegraph(graph, f"output/{testname}.png")


def draw_params(res, mu, sigma, minimizer, figname):
    _, ax = plt.subplots()
    for cl in (1, 2, 3):
        contours = minimizer._minimizer.mncontour(0, 1, cl=cl)
        ax.plot(contours[:, 0], contours[:, 1], label=f"{cl}σ")
    ax.scatter(*[mu, sigma], label="true")
    ax.scatter(*res, label="fit")
    plt.xlabel("mu")
    plt.ylabel("sigma")
    plt.legend()
    plt.xlim([mu - 0.01, mu + 0.01])
    plt.ylim([sigma - 0.01, sigma + 0.01])
    plt.savefig(figname)
    print("Write", figname)
    plt.close()


def draw_fit(x, mc, model, modelfit, mode, figname):
    ax = plt.subplot(111)
    ax.minorticks_on()
    ax.grid()
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    plot_array_1d(
        mc.outputs[0].data,
        meshes=x,
        color="black",
        label="data+fluct." if mode != "asimov" else "asimov MC",
    )
    plot_array_1d(model.data, meshes=x, linestyle="--", label="data")
    plot_array_1d(modelfit.data, meshes=x, linestyle="--", label="fit")
    ax.legend()
    plt.savefig(figname)
    print("Write", figname)
    plt.close()
