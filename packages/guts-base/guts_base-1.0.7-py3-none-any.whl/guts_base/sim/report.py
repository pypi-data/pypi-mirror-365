from functools import partial
import os
import itertools as it
from typing import List, Dict, Literal, Optional, Union
import numpy as np
import pandas as pd
import xarray as xr
import arviz as az

from pymob import SimulationBase
from pymob.sim.report import Report, reporting
from pymob.inference.analysis import round_to_sigfig, format_parameter

from guts_base.plot import plot_survival_multipanel, plot_exposure_multipanel
from guts_base.sim.ecx import ECxEstimator

class GutsReport(Report):
    ecx_estimates_times: List = [1, 2, 4, 10]
    ecx_estimates_x: List = [0.1, 0.25, 0.5, 0.75, 0.9]
    ecx_draws: int = 250
    ecx_force_draws: bool = False
    set_background_mortality_to_zero = True
    table_parameter_stat_focus = "mean"
    units = xr.Dataset({
        "metric": ["unit"],
        "k_d": ("metric", ["1/t"])
    })


    def additional_reports(self, sim: "SimulationBase"):
        super().additional_reports(sim=sim)
        self.model_fits(sim)
        self.LCx_estimates(sim)

    @reporting
    def model_input(self, sim: SimulationBase):
        self._write("### Exposure conditions")
        self._write(
            "These are the exposure conditions that were assumed for parameter inference. "+
            "Double check if they are aligned with your expectations. Especially short " +
            "exposure durations may not be perceivable in this view. In this case it is "+
            "recommended to have a look at the exposure conditions in the numerical "+
            "tables provided below." 
        )
        
        out_mp = plot_exposure_multipanel(
            sim=sim,
            results=sim.model_parameters["x_in"],
            ncols=6,
        )

        lab = self._label.format(placeholder='exposure')
        self._write(f"![Exposure model fits.\label{{{lab}}}]({os.path.basename(out_mp)})")

        return out_mp

    @reporting
    def model_fits(self, sim: SimulationBase):
        self._write("### Survival model fits")
        
        self._write(
            "Survival observations on the unit scale with model fits. The solid line is "+
            "the average of individual survival probability predictions from multiple "+
            "draws from the posterior parameter distribution. In case a point estimator "+
            "was used the solid line indicates the best fit. Grey uncertainty intervals "+
            "indicate the uncertainty in survival probabilities. Note that the survival "+
            "probabilities indicate the probability for a given individual or population "+
            "to be alive when observed at time t."
        )

        out_mp = plot_survival_multipanel(
            sim=sim,
            results=sim.inferer.idata.posterior_model_fits,
            ncols=6,
        )

        lab = self._label.format(placeholder='survival_fits')
        self._write(f"![Surival model fits.\label{{{lab}}}]({os.path.basename(out_mp)})")

        return out_mp
    
    @reporting
    def LCx_estimates(self, sim):
        X = self.ecx_estimates_x
        T = self.ecx_estimates_times
        P = sim.predefined_scenarios()

        if self.set_background_mortality_to_zero:
            conditions = {sim.background_mortality: 0.0}

        estimates = pd.DataFrame(
            it.product(X, T, P.keys()), 
            columns=["x", "time", "scenario"]
        )

        ecx = []

        for i, row in estimates.iterrows():
            ecx_estimator = ECxEstimator(
                sim=sim,
                effect="survival", 
                x=row.x,
                time=row.time, 
                x_in=P[row.scenario], 
                conditions_posterior=conditions
            )
            
            ecx_estimator.estimate(
                mode=sim.ecx_mode,
                draws=self.ecx_draws,
                force_draws=self.ecx_force_draws,
                show_plot=False
            )

            ecx.append(ecx_estimator.results.copy(deep=True))
            
        results = pd.DataFrame(ecx)
        estimates[results.columns] = results

        out = self._write_table(tab=estimates, label_insert="$LC_x$ estimates")
        
        return out


    @reporting
    def table_parameter_estimates(self, posterior, indices):

        if self.rc.table_parameter_estimates_with_batch_dim_vars:
            var_names = {
                k: k for k, v in self.config.model_parameters.free.items()
            }
        else:
            var_names = {
                k: k for k, v in self.config.model_parameters.free.items()
                if self.config.simulation.batch_dimension not in v.dims
            }

        var_names.update(self.rc.table_parameter_estimates_override_names)

        if len(self.rc.table_parameter_estimates_exclude_vars) > 0:
            self._write(f"Excluding parameters: {self.rc.table_parameter_estimates_exclude_vars} for meaningful visualization")

            var_names = {
                k: k for k, v in var_names.items() 
                if k not in self.rc.table_parameter_estimates_exclude_vars
            }

        tab_report = create_table(
            posterior=posterior,
            vars=var_names,
            error_metric=self.rc.table_parameter_estimates_error_metric,
            units=self.units,
            significant_figures=self.rc.table_parameter_estimates_significant_figures,
            nesting_dimension=indices.keys(),
            parameters_as_rows=self.rc.table_parameter_estimates_parameters_as_rows,
        )

        # rewrite table in the desired output format
        tab = create_table(
            posterior=posterior,
            vars=var_names,
            error_metric=self.rc.table_parameter_estimates_error_metric,
            units=self.units,
            significant_figures=self.rc.table_parameter_estimates_significant_figures,
            fmt=self.rc.table_parameter_estimates_format,
            nesting_dimension=indices.keys(),
            parameters_as_rows=self.rc.table_parameter_estimates_parameters_as_rows,
        )

        self._write_table(tab=tab, tab_report=tab_report, label_insert="Parameter estimates")


def create_table(
    posterior, 
    error_metric: Literal["hdi","sd"] = "hdi", 
    vars: Dict = {}, 
    nesting_dimension: Optional[Union[List,str]] = None,
    units: xr.Dataset = xr.Dataset(),
    fmt: Literal["csv", "tsv", "latex"] = "csv",
    significant_figures: int = 3,
    parameters_as_rows: bool = True,
) -> pd.DataFrame:
    """The function is not ready to deal with any nesting dimensionality
    and currently expects the 2-D case
    """
    tab = az.summary(
        posterior, var_names=list(vars.keys()), 
        fmt="xarray", kind="stats", stat_focus="mean", 
        hdi_prob=0.94
    )

    tab = tab.rename(vars)

    _units = flatten_coords(
        dataset=create_units(dataset=tab, defined_units=units), 
        keep_dims=["metric"]
    )
    tab = flatten_coords(dataset=tab, keep_dims=["metric"])

    tab = tab.apply(np.vectorize(
        partial(round_to_sigfig, sig_fig=significant_figures)
    ))


    if error_metric == "sd":
        arrays = []
        for _, data_var in tab.data_vars.items():
            par_formatted = data_var.sel(metric=["mean", "sd"])\
                .astype(str).str\
                .join("metric", sep=" ± ")
            arrays.append(par_formatted)


        table = xr.combine_by_coords(arrays)
        table = table.assign_coords(metric="mean ± std").expand_dims("metric")
        table = table.to_dataframe().T

    elif error_metric == "hdi":
        stacked_tab = tab.sel(metric=["mean", "hdi_3%", "hdi_97%"])\
            .assign_coords(metric=["mean", "hdi 3%", "hdi 97%"])
        table = stacked_tab.to_dataframe().T

    else:
        raise NotImplementedError("Must use one of 'sd' or 'hdi'")


    if fmt == "latex":
        table.columns.names = [c.replace('_',' ') for c in table.columns.names]
        table.index = [format_parameter(i) for i in list(table.index)]
        table = table.rename(
            columns={"hdi 3%": "hdi 3\\%", "hdi 97%": "hdi 97\\%"}
        )
    else: 
        pass

    table["unit"] = _units.to_pandas().T
    

    if parameters_as_rows:
        return table
    else:
        return table.T

def flatten_coords(dataset: xr.Dataset, keep_dims):
    """flattens extra coordinates beside the keep_dim dimension for all data variables
    producing a array with harmonized dimensions
    """
    ds = dataset.copy()
    for var_name, data_var in ds.data_vars.items():
        extra_coords = [k for k in list(data_var.coords.keys()) if k not in keep_dims]
        if len(extra_coords) == 0:
            continue
        
        data_var_ = data_var.stack(index=extra_coords)
        
        # otherwise
        for idx in data_var_["index"].values:
            new_var_name = f"{var_name}[{','.join([str(e) for e in idx])}]"
            # reset coordinates to move non-dim index coords from coordinates to the
            # data variables and then select only the var_name from the data vars
            new_data_var = data_var_.sel({"index": idx}).reset_coords()[var_name]
            ds[new_var_name] = new_data_var

        ds = ds.drop(var_name)

    # drop any coordinates that should not be in the dataset at this stage
    extra_coords = [k for k in list(ds.coords.keys()) if k not in keep_dims]
    ds = ds.drop(extra_coords)

    return ds

def create_units(dataset: xr.Dataset, defined_units: xr.Dataset):
    units = dataset.sel(metric=["mean"]).astype(str)
    units = units.assign_coords({"metric": ("metric", ["unit"])})
    for k, u in units.data_vars.items():
        if k in defined_units:
            units = units.assign({k: defined_units[k].astype(units[k].dtype)})
        else:
            units[k].values = np.full_like(u.values, "")

    return units

class ParameterConverter:
    def __init__(
        self,
        sim: SimulationBase,
    ):
        self.sim = sim.copy()

        # this converts the units of exposure in the copied simulation 
        # and scales the exposure dataarray
        self.sim._convert_exposure_units()
        self.convert_parameters()
        self.sim.prepare_simulation_input()
        self.sim.dispatch_constructor()

        # self.plot_exposure_and_effect(self.sim, sim, _id=7, data_var="D")

        # if parameters are not rescaled this method should raise an error
        self.validate_parameter_conversion_default_params(sim_copy=self.sim, sim_orig=sim)
        self.validate_parameter_conversion_posterior_mean(sim_copy=self.sim, sim_orig=sim)
        self.validate_parameter_conversion_posterior_map(sim_copy=self.sim, sim_orig=sim)

    def convert_parameters(self):
        raise NotImplementedError


    @staticmethod
    def plot_exposure_and_effect(sim_copy, sim_orig, _id=1, data_var="survival"):
        from matplotlib import pyplot as plt
        fig, (ax1, ax2) = plt.subplots(2,1)
        results_copy = sim_copy.evaluate(parameters=sim_copy.config.model_parameters.value_dict)
        results_orig = sim_orig.evaluate(parameters=sim_orig.config.model_parameters.value_dict)

        ax1.plot(results_orig.time, results_orig["exposure"].isel(id=_id), color="red", label="unscaled")
        ax1.plot(results_copy.time, results_copy["exposure"].isel(id=_id), color="blue", ls="--", label="scaled")
        ax2.plot(results_orig.time, results_orig[data_var].isel(id=_id), color="red", label="unscaled")
        ax2.plot(results_copy.time, results_copy[data_var].isel(id=_id), color="blue", ls="--", label="scaled")
        ax1.legend()
        ax2.legend()
        return fig

    @staticmethod
    def validate_parameter_conversion_default_params(sim_copy, sim_orig):
        results_copy = sim_copy.evaluate(parameters=sim_copy.config.model_parameters.value_dict)
        results_orig = sim_orig.evaluate(parameters=sim_orig.config.model_parameters.value_dict)

        np.testing.assert_allclose(results_copy.H, results_orig.H, atol=0.001, rtol=0.001)

    @staticmethod
    def validate_parameter_conversion_posterior_mean(sim_copy, sim_orig):
        results_copy = sim_copy.evaluate(parameters=sim_copy.point_estimate("mean", to="dict"))
        results_orig = sim_orig.evaluate(parameters=sim_orig.point_estimate("mean", to="dict"))

        np.testing.assert_allclose(results_copy.H, results_orig.H, atol=0.001, rtol=0.001)

    @staticmethod
    def validate_parameter_conversion_posterior_map(sim_copy, sim_orig):
        results_copy = sim_copy.evaluate(parameters=sim_copy.point_estimate("map", to="dict"))
        results_orig = sim_orig.evaluate(parameters=sim_orig.point_estimate("map", to="dict"))

        np.testing.assert_allclose(results_copy.H, results_orig.H, atol=0.001, rtol=0.001)