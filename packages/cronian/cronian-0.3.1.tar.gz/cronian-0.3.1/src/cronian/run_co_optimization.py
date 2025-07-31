"""Run the sector-coupled co-optimization in a centralized manner.

By default, this script runs the optimization using the yaml configurations,
timeseries_data, price_timeseries csv files provided in the tests/data
directory. Generators and prosumers are each defined in their respective yaml
configuration file. The timeseries_data csv file contains the timeseries data
such as VRE generators' availability factors, demand profiles,
minimum_state_of_charge and availability of EVs doing vehicle-to-grid (V2G), etc.
The price_timeseries csv file contains the prices of non-electricity energy
carriers such methane, hydrogen, biomass, etc. Finally, a general_config.yaml
file is also needed where general parameters such as number of timesteps for
which to run the simulation, etc., are defined.

NOTE: If you want to add a prosumer with a more detailed model than the one
build by this package, explicitly build its model and add it to the simulation.
See explicit_heat.py as an example. This design choice gives the user more
flexibility in building its own explicit prosumers to be added to the simulation.
"""

import argparse
from pathlib import Path

import pandas as pd
import pyomo.environ as pyo
import yaml
from pyprojroot import here

from .base_model import create_optimization_model
from .configuration import load_configurations
from .explicit_heat import add_explicit_heat_to_model
from .generators import add_all_generators
from .objective_func import set_model_objective_function
from .prosumers import add_built_prosumers_to_optimization_model
from .results import extract_market_schedule, extract_market_schedule_milp, extract_prosumer_dispatch
from .system_balance import set_system_electric_power_balance_constraint
from .validate import validate_all_agents


def main(
    configurations_folder: Path,
    timeseries_data: pd.DataFrame,
    price_timeseries: pd.DataFrame,
    explicit_prosumer_configuration: dict | None,
    explicit_prosumer_timeseries_data: pd.DataFrame | None,
    number_of_timesteps: int,
    storage_model: str,
    results_folder: Path,
    include_base_load: bool = False,
    solver_name: str = "gurobi",
    solver_options: dict | None = None,
) -> None:
    """Solve the sector-coupled optimization model in a centralized manner.

    Args:
    -----
        configurations_folder: Path to folder containing configuration files.
        explicit_prosumer_configuration: Configuration file of explicit prosumer.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...
        price_timeseries: Dataframe containing the prices of energy carriers.
        explicit_prosumer_timeseries_data: The csv file containing timeseries
            data for the explicit prosumer.
        number_of_timesteps: Number of timesteps to run the optimization for.
        storage_model: Type of storage model to use: `simple` or `complex`.
        results_folder: Path to the folder where the results will be saved.
        include_base_load: if True, base load from passive consumers is
            included in the optimization model.
        solver_name: Name of the solver to use.
        solver_options: Solver options to be passed to the solver.
    """
    configurations = load_configurations(configurations_folder)
    generators = configurations["Generators"]
    prosumers = configurations["Prosumers"]
    if number_of_timesteps is None:
        number_of_timesteps = configurations["General"]["number_of_timesteps"]

    validate_all_agents(configurations, timeseries_data)

    if include_base_load:
        base_load_series = timeseries_data.loc[:, "BaseLoad"]
    else:
        base_load_series = None

    model = create_optimization_model(base_load_series, price_timeseries, number_of_timesteps)
    add_all_generators(model, generators, timeseries_data)
    add_built_prosumers_to_optimization_model(model, prosumers, timeseries_data, number_of_timesteps, storage_model)

    # Add explicit heat to the model if provided
    if explicit_prosumer_configuration:
        add_explicit_heat_to_model(
            model, explicit_prosumer_configuration, explicit_prosumer_timeseries_data, number_of_timesteps
        )

    set_system_electric_power_balance_constraint(model)
    set_model_objective_function(model, prosumers, price_timeseries)

    model_instance = model.create_instance()

    solver = pyo.SolverFactory(solver_name)
    if solver_options:
        solver.options.update(solver_options)

    model_instance.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)

    results = solver.solve(model_instance, tee=False)

    if results.solver.termination_condition == pyo.TerminationCondition.optimal:
        if storage_model.lower() == "simple":
            market_schedule = extract_market_schedule(model_instance, generators.keys() | prosumers.keys())
        elif storage_model.lower() == "complex":
            market_schedule = extract_market_schedule_milp(model_instance, generators.keys() | prosumers.keys())
        print("======================== Market prices ========================")
        print(market_schedule["market-price"])
        print("---------------------------------------------------------------")
        print("=========================== DONE !!! ==========================")
    else:
        print()
        print("###############################################################")
        print("====== INTERRUPTED !!! Model is infeasible or unbounded. ======")
        print("###############################################################")

    # Write market schedule results to csv files.
    results_folder.mkdir(parents=True, exist_ok=True)
    market_schedule.to_csv(results_folder / "market_schedule.csv")

    # Extract and save the dispatch schedule of prosumers
    for prosumer in prosumers:
        prosumer_schedule = extract_prosumer_dispatch(model_instance, prosumers[prosumer])
        prosumer_schedule.to_csv(results_folder / f"{prosumer}_schedule.csv")


def parse_command_line_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the sector-coupled co-optimization model.")
    parser.add_argument(
        "--configurations-folder",
        type=Path,
        default=here("tests/data/demo_configurations"),
        help="Path to configuration files folder.",
    )

    parser.add_argument(
        "--timeseries_data",
        type=Path,
        default=here("tests/data/demo_csv/generic-timeseries.csv"),
        help="Path to the timeseries_data file.",
    )

    parser.add_argument(
        "--price_timeseries",
        type=Path,
        default=here("tests/data/demo_csv/price-timeseries.csv"),
        help="Path to the price_timeseries file.",
    )

    parser.add_argument(
        "--explicit-prosumer-config",
        type=Path,
        default=None,
        help="Path to the explicit_prosumer_config file.",
    )

    parser.add_argument(
        "--explicit-prosumer-timeseries-data",
        type=Path,
        default=None,
        help="Path to the explicit_prosumer_timeseries_data file.",
    )

    parser.add_argument(
        "--number-of-timesteps",
        type=int,
        default=None,
        help="Number of timesteps in for which the optimization is run.",
    )

    parser.add_argument(
        "--storage-model",
        type=str,
        default="simple",
        choices=["simple", "complex"],
        help="Type of storage model to use: `simple` or `complex`.",
    )

    parser.add_argument(
        "--include-base-load",
        action="store_true",
        help="Flag whether to include a base load from passive consumers in the optimization model.",
    )

    parser.add_argument(
        "--results-folder",
        type=Path,
        default=here("results"),
        help="Path to the folder where the results will be saved.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_command_line_args()

    explicit_prosumer_configuration = None
    explicit_prosumer_timeseries_data = None

    if args.explicit_prosumer_config and args.explicit_prosumer_timeseries_data:
        with open(args.explicit_prosumer_config, "r") as file:
            explicit_prosumer_configuration = yaml.safe_load(file)
        explicit_prosumer_timeseries_data = pd.read_csv(args.explicit_prosumer_timeseries_data, index_col=0)
    elif args.explicit_prosumer_config or args.explicit_prosumer_timeseries_data:
        raise RuntimeError("Both explicit_prosumer_config and explicit_prosumer_timeseries_data must be provided.")

    main(
        configurations_folder=args.configurations_folder,
        timeseries_data=pd.read_csv(args.timeseries_data, index_col=0),
        price_timeseries=pd.read_csv(args.price_timeseries, index_col=0),
        explicit_prosumer_configuration=explicit_prosumer_configuration,
        explicit_prosumer_timeseries_data=explicit_prosumer_timeseries_data,
        number_of_timesteps=args.number_of_timesteps,
        storage_model=args.storage_model,
        include_base_load=args.include_base_load,
        results_folder=args.results_folder,
    )
