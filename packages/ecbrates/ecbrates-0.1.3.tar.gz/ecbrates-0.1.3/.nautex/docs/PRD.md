#  Product Specification

## [PRD-21] Introduction & Vision

This document outlines the requirements for ecbrates, a Python package designed to provide historical and current foreign exchange rates against the Euro (EUR). The package will fetch data directly from the European Central Bank (ECB), provide robust caching to ensure performance and reliability, and offer a simple programmatic and command-line interface for developers and users. The core problem being solved is the need for a simple, reliable, and efficient way to access ECB exchange rate data within Python applications. The vision is to create a lightweight, well-tested, and easy-to-use tool that intelligently manages data freshness and handles common data availability issues (like weekends and holidays) gracefully.

## [PRD-47] Target Audience & User Personas

[PRD-53] Python Developers: Professionals and hobbyists building applications that require currency conversion, financial analysis, or data reporting. They need a library that is easy to integrate, reliable, and performs well.

[PRD-7] Data Analysts / Scientists: Users who may need to script quick lookups for historical exchange rates for analysis without building a full application.

[PRD-65] System Administrators / DevOps Engineers: Users who might leverage the Command-Line Interface (CLI) for scripting or quick checks on servers.

## [PRD-43] User Stories / Use Cases

[PRD-27] As a developer, I want to retrieve the exchange rate between two currencies for a specific date so that I can accurately convert monetary values in my application.

[PRD-12] As a developer, I want to get the latest available exchange rate without specifying a date so that I always have the most current data for real-time calculations.

[PRD-24] As a developer, I want the package to automatically find the most recent prior day's rate if data for my requested date is not available (e.g., on a weekend or holiday), so my application remains resilient and avoids errors.

[PRD-57] As a developer, I want the exchange rate data to be cached locally so that my application is fast and minimizes redundant network requests to the ECB.

[PRD-18] As a developer, I want the cache to automatically expire when the ECB is expected to publish new data, ensuring data freshness without manual intervention.

[PRD-5] As a developer, I want to be able to programmatically trigger a cache refresh to force an update when necessary.

[PRD-72] As a developer, I want access to console logs to understand the package's behavior, such as cache hits/misses, network activity, and fallback logic.

[PRD-46] As a CLI user, I want to quickly look up an exchange rate from my terminal so that I can get information without writing a Python script.

[PRD-35] As a CLI user, I want a simple command to manually refresh the local data cache to ensure it is up-to-date.

## [PRD-6] Functional Requirements

[PRD-60] The package must be named ecbrates.

[PRD-64] The system must provide a CurrencyRates class.

[PRD-29] The CurrencyRates class must have a method with the signature get_rate(self, base_cur: str, dest_cur: str = 'EUR', date_obj: datetime.datetime=None).

[PRD-36] If the date_obj parameter is not provided (None), the get_rate method must return the exchange rate from the most recent day available in the data source.

[PRD-55] If the data for the requested date_obj or a requested currency on that date is not available, the system must search for the nearest prior date that has valid data for the requested currencies and use that rate.

[PRD-34] An exception must be raised only if no prior rate can be found in the entire historical dataset for the requested currencies.

[PRD-13] The CurrencyRates class must include a method to manually refresh the cache.

[PRD-48] The system must fetch exchange rate data from the URL: https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml.

[PRD-67] Fetched XML data must be loaded on demand and cached on disk.

[PRD-45] The cache folder location must be configurable via an environment variable named ECB_CACHE.

[PRD-22] If the ECB_CACHE environment variable is not set, the cache path must default to .cache/ecbrates.

[PRD-42] The cache Time-To-Live (TTL) must be dynamic, expiring at the time of the next scheduled daily update from the ECB, based on its official schedule, including logic for weekends and holidays.

[PRD-4] Currency codes provided to get_rate must be treated as case-sensitive.

[PRD-41] The package must provide a Command-Line Interface (CLI).

[PRD-14] The CLI must include a command to query for an exchange rate.

[PRD-66] The CLI query command must accept a base currency, an optional destination currency, and an optional date in YYYY-MM-DD format.

[PRD-26] The CLI must include a separate command to manually refresh the cache.

[PRD-40] The output of the CLI query command must be plain text.

[PRD-17] The package must include logging functionality.

[PRD-31] Log output must be directed to the console only.

[PRD-10] The default logging level must be INFO.

[PRD-15] The CLI must provide an option (e.g., a flag) to set the logging level to DEBUG.

[PRD-19] In case of a network error during a data fetch/refresh, the system must use existing data from the cache if it contains a record for the requested date.

[PRD-61] The package must be compatible with Python 3.10 and newer.

[PRD-28] The project must use the uv package manager for dependency management and packaging.

[PRD-62] The package must include a suite of unit tests.

[PRD-49] Unit tests must cover core functionality (data fetching, caching, dynamic TTL, fallback logic) and the CLI commands.

## [PRD-23] Non-Functional Requirements

[PRD-70] Performance: The system should feel responsive for users. Subsequent requests for the same data should be near-instantaneous due to effective caching.

[PRD-33] Reliability: The application should be resilient to temporary network failures, relying on cached data whenever possible to ensure availability.

[PRD-54] Usability: Both the Python library API and the CLI should be simple, intuitive, and well-documented.

[PRD-44] Maintainability: The code should be clean, well-structured, and have high test coverage to allow for easy future updates.

[PRD-8] Configuration: Configuration should be simple and rely on a standard mechanism (environment variables) that is easy to manage in various deployment environments.

[PRD-3] TODO: Quantify acceptable latency for cached vs. uncached get_rate calls. Stakeholder: Product Manager

## [PRD-68] Scope

### [PRD-30] In Scope

[PRD-16] A Python package named ecbrates.

[PRD-37] CurrencyRates class with get_rate and manual cache refresh methods.

[PRD-32] On-demand data fetching from the specified ECB XML URL.

[PRD-69] Disk-based caching using diskcache.

[PRD-39] Dynamic TTL for the cache based on the official ECB update schedule (including weekends/holidays).

[PRD-51] Date-based fallback logic for unavailable rates.

[PRD-20] Configuration of cache directory via ECB_CACHE environment variable.

[PRD-1] A CLI with two commands: one for querying rates and one for refreshing the cache.

[PRD-38] Console-based logging with configurable verbosity (INFO/DEBUG).

[PRD-63] Unit test suite for core logic and CLI.

[PRD-2] Support for Python 3.10+.

[PRD-59] Use of uv package manager.

### [PRD-25] Out of Scope

[PRD-52] Configuration via pyproject.toml or any other configuration files.

[PRD-11] User-configurable cache TTL via an environment variable.

[PRD-50] A CLI command to list all available currencies.

[PRD-71] Logging to a file.

[PRD-9] JSON or other structured output formats for the CLI.

[PRD-58] Support for any data source other than the specified ECB XML file.

## [PRD-56] Success Metrics

TODO: Define key success metrics for the package. Examples could include number of downloads on PyPI, low rate of bug reports related to core logic (caching, fallback), or positive feedback on developer experience. Stakeholder: Product Manager
