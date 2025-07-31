Example Usage
=============


Creating Models
---------------

To create a model, you have to specify the desired generators and prosumers in
`YAML` format. To start, generators are fairly simple:

.. code-block:: yaml

    # Generator01.yaml
    Generators:  # Top level key must be 'Generators'
      # Required keys
      name: WindOffshore
      id: G05  # Must be unique
      marginal_cost_quadratic: 0.007
      marginal_cost_linear: 5
      installed_capacity: 6000
      # Optional keys
      availability_factor: WIND_OFFSHORE  # Timeseries column name


The name under the optional ``availability_factor`` key will be used to look up a timeseries from the
dataframe that is passed in separately, otherwise availability will be set to ``1`` at all times ``t``.
The production ``gen_power[t]`` of the specified generator will then be constrained by:

.. code-block:: python

    0 <= gen_power[t] <= installed_capacity * availability_factor[t]


A simple prosumer with just some fixed demand would look like this:

.. code-block:: yaml

    # Prosumer01.yaml
    Prosumers:
      name: Simple_demand
      id: P01
      demand:
        commercial:
          carrier: electricity
          base:
            peak: 100


We can make prosumers more interesting by adding ``flexible`` demand and ``assets``. Multiple demands
can be added, each with their own ``flexible`` and ``base`` (inflexible) components. Furthermore, there
are three kinds of ``assets``: ``generator``, ``converter`` and ``storage``. Here's a more complex prosumer
with flexible demand and one of each asset type:

.. code-block:: yaml

    # Prosumer01.yaml
    Prosumers:
      name: Heat_system_operator
      id: P02
      demand:
        hot_water:
          carrier: heat  # Must be 'electricity', or output of an asset
          # At least `base` or `flexible` demand must be present
          base:
            peak: 300
          flexible:  # `flex+N` encodes a demand with `N` timesteps of flexibility
            flex+2:
              peak: 125000
              n_profile: P02-flexible-demand  # similar to `availability_factor` for generators
            flex+3:
              peak: 50
      assets:
        solar_pv:
          behavior_type: generator
          input: light
          output: electricity
          installed_capacity: 1000
          availability_factor: SOLAR_WEST  # Optional
          operational_costs:
            marginal_cost_quadratic: 0.007
            marginal_cost_linear: 5
        chp:
          behavior_type: converter
          # Can convert 1-to-1, 1-to-many or many-to-1
          input: methane
          output:
            - heat
            - electricity
          installed_capacity: 1000
          # if converting 1-to-many or many-to-1, specify efficiency for each of the 'many'
          efficiency:
            heat: 0.4
            electricity: 0.4
        heat_storage:
          behavior_type: storage
          input: heat
          output: heat
          energy_capacity: 5000
          initial_energy: 50
          charge_capacity: 500
          discharge_capacity: 500
          charge_efficiency: 0.8
          discharge_efficiency: 0.65


Performing Co-Optimization
--------------------------

To use Cronian for a co-optimization run, you first have to specify an additional
``general_config.yaml`` file, and place it in the same folder as your generator and prosumer
configuration files.

.. code-block:: yaml

    # general_config.yaml
    General:
      number_of_timesteps: 24


Then in code you can create and run the model as follows:

.. code-block:: python

    from pathlib import Path
    from cronian.run_co_optimization import main
    import pandas as pd

    main(
        configurations_folder=Path("/path/to/configurations/"),
        timeseries_data=pd.read_csv("/path/to/availability/factors/timeseries.csv", index_col=0, parse_dates=True),
        price_timeseries=pd.read_csv("/path/to/prices/for/external/carriers.csv", index_col=0, parse_dates=True),
        explicit_prosumer_configuration=None,
        explicit_prosumer_timeseries_data=None,
        number_of_timesteps=None,
        include_base_load=True,
        results_folder=Path("/path/to/folder/for/output"),
    )

Some intermediate information will be printed on ``stdout``, and all final results will be stored in
the specified ``results_folder``.


External Usage Examples
-----------------------

Cronian can also be used to build smaller models to be used by other methods.

- Distributed optimization: `demoses-ADMM <https://gitlab.tudelft.nl/demoses/demoses-admm/-/blob/main/src/demoses_admm/build_prosumer_agent.py?ref_type=heads>`_
- Agent-based simulation: `Annular <https://gitlab.tudelft.nl/demoses/demoses-coupling/-/blob/main/src/demoses_coupling/satellite_model/optimizer_bidding_strategy.py?ref_type=heads>`_
