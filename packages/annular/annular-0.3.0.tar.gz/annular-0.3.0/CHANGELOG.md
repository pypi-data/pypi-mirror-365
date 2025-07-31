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

## [0.3.0] - 2025-07-30

### Added
- Add MultiProfileBiddingStrategy that takes a price forecast, derives multiple scenarios from it, determines a demand profile for each, and submits those profiles in an exclusive group. ([!71](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/71))
- Add support for profile block bids and exclusive groups thereof. ([!76](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/76))
  - A profile block is a collection of bids for multiple timestamps that have the same `profile_block_id`. All bids in a profile block are accepted or rejected together, based on their weighted average price.
  - An exclusive group is a collection of profile blocks of which at most one is accepted. Exclusive groups are encoded by sharing an `exclusive_group_id`. Note: a profile block must exist in a single exclusive group to be treated as such, otherwise they are treated as individual bids.
- Add SimpleMultiHourBiddingStrategy that can submit bids for multiple timestamps in one go, by picking one timestamp per flexible demand. ([!61](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/61))

### Changed
- Renamed package from 'demoses-coupling' to 'annular' ([!80](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/80))
- OptimizerBiddingStrategy no longer calculates bids for prices above ceiling price. ([!77](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/77))
- When exchanging bids, the index is no longer expected to be `timestamps, demand`, but is now `exclusive_group_id, profile_block_id, timestamp`. The `bid_price` column has also been renamed to just `price`. ([!76](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/76))
  - All bidding strategies have been updated to match this new format.
  - As part of this change, all submitted bids are no longer treated as being 100% curtailable. For individual bids that are not submitted as part of a profile block, this means they are individually non-curtailable.

### Removed
- Removed all obsolete ISGT files. ([!81](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/81))
- Paths given through configuration files are no longer assumed relative to the project's root. Instead, the paths should either be specified as absolute, or should be valid relative to the process' working directory.
- The `pyprojroot` package has been moved to be only a dev dependency. ([!78](https://gitlab.tudelft.nl/demoses/demoses-coupling/-/merge_requests/78))

## [0.2.0] - 2025-04-19

### Added
- OptimizerBiddingStrategy now takes in separate dataframes for electricity price forecasts
  and fixed prices for other energy carriers such as methane ([!49](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/49))
- Satellite models now support 'expanding' a generic configuration into multiple specific configurations:
  Optimizer-bidding-strategy can now specify a folder as `model_config_path`, where a specific configuration will be
  made for each model configuration in that folder. The original configuration remains unchanged, and specific configs
  are stored in the `results_path` location. ([!46](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/46))
- Migrate market model implementation from pypsa/linopy to pyomo ([!44](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/44))
- Add support for arbitrary numbers of satellite models ([!43](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/43))
- Add satellite model based on (simple) optimization model, works for 1h rolling step ([!38](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/38))
- Add consumer model that solves using rolling horizon
- Add logistic price scaling function for HeuristicBiddingStrategy
- Add shift parameter for price scaling functions for HeuristicBiddingStrategy
- Add code style preferences to README.dev.md

### Changed
- Bid prices are no longer determined naively based on linear interpolation from ceiling to floor price. Instead, bid prices are now determined based on the opportunity costs of shifting to a different time or different energy carrier. ([!62](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/62))
- Simulations are no longer restricted to a rolling step size of 1 timestamp, but can now be run for
  arbitrary window sizes, with 24h being the intended (but not hardcoded) size.
  ([!54](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/54))
- The Market clearing price is now determined solely by the marginal cost of generators. That is, only the generation side (but not the demand side) sets the market price. ([!56](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/56))
- Optimizer-bidding-strategy is now updated to be compatible with the latest version of `Cronian`([!45](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/45))
- Expected model coupling settings (ymmsl) file adjusted: only 'settings' part is expected.
  Components and Ports now hardcoded specified as part of `main()`.
  Satellite models are now specified through a "satellite_configs" key, pointing to a folder containing separate yml files per satellite. ([!43](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/43))
- Optimizer-bidding-strategy can now use a co_optimization specified model instead of built-in hardcoded model ([!40](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/40))
- make satellite_model subpackage
- specify SatelliteModel interface as ABC with abstractmethods
- Flexible demand given to HeuristicBiddingStrategy is now interpreted as ahead-shiftable instead of delay-shiftable ([!39](https://gitlab.tudelft.nl/demoses/annular/-/merge_requests/39))

### Removed
- Removed Constant and Repeating bidding strategies

## [0.1.1]

### Added
- Add CLI argument to specify output format
- Add ymax argument to plot_simulation_results
- automatically transform input timeseries to valid for queue strategy

### Changed
- fix: list complete co-optimization results path in README instructions
- results stored with timestamp
- replace renewable_capacity file with calculation based on supply and capacity factors files
- reduce and simplify plot output files
- update figure sizes for ISGT paper
- update README instructions

### Removed
- remove examples folder: use input/ and tests/data/;


## [0.1.0] - 2024-07-31

- initial release

[Unreleased]: https://gitlab.tudelft.nl/demoses/annular/compare/v0.3.0...HEAD
[0.3.0]: https://gitlab.tudelft.nl/demoses/annular/-/releases/v0.3.0
[0.2.0]: https://gitlab.tudelft.nl/demoses/annular/-/releases/v0.2.0
[0.1.1]: https://gitlab.tudelft.nl/demoses/annular/-/releases/v0.1.1
[0.1.0]: https://gitlab.tudelft.nl/demoses/annular/-/releases/v0.1.0
