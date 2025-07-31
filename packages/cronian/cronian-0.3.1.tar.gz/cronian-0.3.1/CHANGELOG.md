# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
-

### Changed
-

### Removed
-

## [0.3.1] - 2025-07-30

### Added
-

### Changed
- Dependencies have been made generic instead of pinned versions. ([!83](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/83))

### Removed
-

## [0.3.0] - 2025-05-10

### Added
- Cronian now supports two types of storage model: `simple` and `complex`. A `simple` storage model might charge and discharge simultaneously if electricity prices are negative. Such an unrealistic behavior is avoided with the `complex` storage model that strictly avoids this behavior using MILP. ([!79](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/79))

### Changed
- Fixed bug in the `validate_prosumer_relevance` function. We were checking that an asset's `output` or `input` == `electricity`. This will not work for assets with multiple `inputs` or `outputs`. This has now been fixed such that it instead checks if `electricity` is in an asset's list of `inputs` or `outputs`. ([!80](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/80))

## [0.2.1] - 2025-03-28

### Added
- Cronian now reports the total amount of externally priced energy carriers (e.g., methane, hydrogen, biomass, etc.) consumed by all assets for each prosumer. ([!77](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/77))

### Changed
- Solver name and solver options for solving the optimization problem can now be passed to `main`. The default solver is `gurobi`, which is used with its default options. ([!76](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/76))
- The `include_base_load` argument is now false by default, and it is removed as an argument from `create_optimization_model` and other lower functions.([!75](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/75))

## [0.2.0] - 2025-03-12

### Added
- Functions to extract timeseries data from the solved pyomo model are now implemented. ([!66](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/66))
- Assets are now assigned a `behavior_type` attribute which determines if they should be constructed as `generators`, `converters`, or `storage` assets. Additionally, tests for `validate.py` has been added with configurations that trigger/raise all the errors against which generator/prosumer agents are checked. ([!56](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/56))
- New `init_store_level` argument for `build_generic_prosumer` ([!49](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/49))

### Changed
- Changed repository URL to https://gitlab.tudelft.nl/demoses/cronian ([!70](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/70))
- Functions for building prosumers no longer return tuples. `Cronian` is now stricter when building prosumers, it does not proceed with building other prosumers on the first failed attempt ([!68](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/68))
- Checking for duplicate IDs in configurations is now first done on a per-subfolder basis to simplify the internal API ([!67](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/67))
- Package has been renamed from `demoses-co-optimization` to `cronian` ([!64](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/64))
- Generator and prosumer agents can now be defined in separate config files. The `load_configurations` function loads all individual config files and combines them into a single python `dict` ([!47](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/47))
- Flexible storage is now modelled as a single store instead of one per flexible demand
- Parsing amount of flexibility when determining store min/max levels can now deal with prefixes and suffixes ([!45](https://gitlab.tudelft.nl/demoses/cronian/-/merge_requests/45))

### Removed
- The definitions.py file which determine asset type by name is now redundant and has been deleted.

## [0.1.1] - 2024-08-14

- Simplify file names for input and output data
- Fix file and command references in README

## [0.1.0] - 2024-07-31

- Initial Release

[Unreleased]: https://gitlab.tudelft.nl/demoses/cronian/compare/v0.3.1...HEAD
[0.3.1]: https://gitlab.tudelft.nl/demoses/cronian/-/releases/v0.3.1
[0.3.0]: https://gitlab.tudelft.nl/demoses/cronian/-/releases/v0.3.0
[0.2.1]: https://gitlab.tudelft.nl/demoses/cronian/-/releases/v0.2.1
[0.2.0]: https://gitlab.tudelft.nl/demoses/cronian/-/releases/v0.2.0
[0.1.1]: https://gitlab.tudelft.nl/demoses/cronian/-/releases/v0.1.1
[0.1.0]: https://gitlab.tudelft.nl/demoses/cronian/-/releases/v0.1.0
