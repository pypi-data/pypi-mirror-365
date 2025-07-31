import pandas as pd
import yaml

from cronian.run_co_optimization import main, parse_command_line_args

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
