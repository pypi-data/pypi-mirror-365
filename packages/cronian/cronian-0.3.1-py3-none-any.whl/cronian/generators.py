"""This builds all generator agents at once.

Unlike build_prosumer function that builds a single prosumer agent at a time.
This is because the focus of DEMOSES is on modeling prosumers in detail.
Moreover, generator agents here are all modeled with a similar structure and
only differ in their parameters.
"""

import pandas as pd
import pyomo.environ as pyo


def add_all_generators(
    model: pyo.AbstractModel,
    generator_agents: dict,
    timeseries_data: pd.DataFrame,
) -> pyo.AbstractModel:
    """Build and add all generator agents' to the optimization model.

    Args:
    -----
        model: Pyomo AbstractModel to which generators are added.
        generator_agents: Dictionary containing generator agents' details.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...

    Returns:
    --------
        Pyomo AbstractModel with generators added.
    """
    # Initialize set of generators (AbstractModel doesn't support dict_keys, must convert to list)
    model.gens = pyo.Set(initialize=list(generator_agents.keys()), ordered=True)

    # Helper function to extract the parameters of each generator
    def extract_gen_param(param_name):
        return {g: gen_data[param_name] for g, gen_data in generator_agents.items()}

    # Cost parameters and installed capacity
    model.gen_marginal_cost_quadratic = pyo.Param(model.gens, initialize=extract_gen_param("marginal_cost_quadratic"))
    model.gen_marginal_cost_linear = pyo.Param(model.gens, initialize=extract_gen_param("marginal_cost_linear"))
    model.gen_installed_cap = pyo.Param(model.gens, initialize=extract_gen_param("installed_capacity"))

    # Generator available capacity (installed capacity * availability factor)
    def gen_available_capacity(model, gen, t):
        if "availability_factor" in generator_agents[gen].keys():
            availability_factor = timeseries_data.loc[t, generator_agents[gen]["availability_factor"]]
        else:
            availability_factor = 1  # Conventional generators
        return model.gen_installed_cap[gen] * availability_factor

    # Set gen_available_cap as an expression that is dynamically calculated during instantiation unlike a parameter to
    # avoid `Cannot iterate over AbstractOrderedScalarSet` error due to iterating over a set that is not constructed.
    model.gen_available_cap = pyo.Expression(model.gens, model.time, rule=gen_available_capacity)

    # Decision variable
    model.gen_power = pyo.Var(model.gens, model.time, domain=pyo.NonNegativeReals, initialize=0)

    # Constraints
    def gen_capacity_limit_rule(model, gen, t):
        return model.gen_power[gen, t] <= model.gen_available_cap[gen, t]

    model.gen_capacity_limit_constraint = pyo.Constraint(model.gens, model.time, rule=gen_capacity_limit_rule)

    return model
