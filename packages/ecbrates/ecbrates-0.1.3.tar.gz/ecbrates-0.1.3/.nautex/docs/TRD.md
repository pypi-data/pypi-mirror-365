#  Technical Specification

## [TRD-33] System Overview

ecbrates is a self-contained Python library packaged for distribution via PyPI. It is composed of a core logic module encapsulating the 

CurrencyRates

 class, a data source module responsible for fetching and parsing ECB data, a caching module that wraps 

diskcache

 to provide intelligent caching, and a CLI module that exposes functionality to the command line. The system is designed to be stateless from the application's perspective, with all persistent state managed within the disk cache.

## [TRD-28] Architectural Goals & Constraints

[TRD-84] Goal: Achieve high performance for repeated data access through an intelligent, dynamic TTL-based caching strategy.

[TRD-10] Goal: Ensure high reliability by implementing robust error handling for network issues and graceful fallback logic for missing data points.

[TRD-15] Goal: Maintain simplicity in design and dependencies to keep the package lightweight and easy to maintain.

[TRD-21] Constraint: The sole external data source is the ECB's historical XML file.

[TRD-74] Constraint: All configuration must be managed via environment variables (ECB_CACHE).

[TRD-135] Constraint: The package must be developed for Python 3.10+ and use uv.

[TRD-16] Constraint: Caching must be implemented using the diskcache library.

[TRD-43] Architectural Pattern Guidance: A simple 3-tier layered architecture is sufficient.

[TRD-112] Presentation Layer: The CLI module (cli.py).

[TRD-133] Business Logic Layer: The core module containing the CurrencyRates class (core.py).

[TRD-113] Data Access Layer: Modules for handling data fetching (datasource.py) and caching (cache.py).

## [TRD-82] Proposed High-Level Architecture

The system will be composed of four main modules:

[TRD-93] Core Module (ecbrates/core.py): Contains the primary public-facing CurrencyRates class. This class orchestrates calls to the data and caching layers to fulfill user requests. It holds the business logic for calculating exchange rates and implementing the date fallback mechanism.

[TRD-130] Caching Module (ecbrates/cache.py): A wrapper around the diskcache library. It will be responsible for storing and retrieving the parsed XML data. Its key responsibility is to calculate the dynamic TTL based on the ECB's official update schedule before setting any cache item. It reads the ECB_CACHE environment variable to initialize the cache directory.

[TRD-24] Data Source Module (ecbrates/datasource.py): This module is responsible for all external interactions. It contains functions to download the XML file from the ECB's URL and parse it into a standardized Python dictionary format that is easy to query. It will handle network-related exceptions.

[TRD-71] CLI Module (ecbrates/cli.py): Implements the command-line interface. It parses arguments, sets up logging verbosity, and instantiates CurrencyRates to execute the user's requested command (query or refresh).The interaction flow is as follows: A client (either a user via the CLI or another Python script) calls a method on the CurrencyRates object. This object first consults the Caching Module. If a valid, non-expired cache entry exists, the data is returned immediately. If not (a cache miss or expiration), it triggers the Data Source Module to fetch and parse the fresh data from the ECB. The newly fetched data is then handed to the Caching Module to be stored with a dynamically calculated TTL, and finally, the result is returned to the client.

## [TRD-95] Technology Stack

[TRD-86] Language: Python 3.10+

[TRD-36] Package Manager: uv

[TRD-4] Used for dependency management, virtual environment creation, and running project scripts.

[TRD-20] Caching: diskcache

[TRD-109] Used for persistent, on-disk caching of the parsed XML data.

[TRD-99] HTTP Client: requests

[TRD-149] A robust and user-friendly library for downloading the XML file. It will be used within the Data Source Module.

[TRD-63] XML Parsing: xml.etree.ElementTree (from Python Standard Library)

[TRD-77] Used for efficiently parsing the large ECB XML data file into a memory-friendly structure.

[TRD-50] CLI Framework: Typer

[TRD-69] A modern and easy-to-use library for building the CLI, providing auto-generated help messages and argument parsing. It will be used in the CLI Module.

[TRD-136] Testing Framework: pytest

[TRD-34] Used for writing and running the unit test suite.

[TRD-123] Logging: logging (from Python Standard Library)

[TRD-88] Used for all application logging, configured to output to the console.

[TRD-80] TODO: Finalize choice of library for determining ECB/TARGET2 holidays for the dynamic TTL calculation. Potential candidates include holidays or a custom implementation based on a documented schedule.

## [TRD-47] Data Management Strategy

Data management is centered around a single cached object.

### [TRD-120] Data Model

The XML data will be parsed into a nested dictionary structure and stored as a single item in the cache. The proposed structure is:

### [TRD-131] Storage

The 

diskcache.Cache

 object will be used for storage. The cache directory is determined by the 

ECB_CACHE

 environment variable, defaulting to 

.cache/ecbrates

.

### [TRD-58] Cache Key

A single, constant string key (e.g., 

ECB_RATES_DATA

) will be used to store the parsed data dictionary.

### [TRD-11] Data Migration

Not applicable, as the cache can be cleared and rebuilt from the source at any time.

## [TRD-57] API Design

### [TRD-98] Python Class API

Python Class API
A custom RateNotFound exception will be raised if no prior rate can be found in the entire historical dataset for the requested currencies. This provides a more specific error than a generic ValueError.

## [TRD-83] Security Considerations (Technical)

[TRD-146] Data Source Integrity: The package will connect to the ECB URL via HTTPS, relying on TLS to ensure data integrity in transit.

[TRD-67] Dependency Management: Project dependencies will be pinned, and uv pip audit should be integrated into the CI/CD pipeline to scan for known vulnerabilities.

[TRD-138] Input Sanitization: While the risk is low, all inputs from the CLI (currency codes, dates) must be validated for format and type before being processed to prevent unexpected errors. Currency codes should be validated against the list of known currencies from the parsed data.

[TRD-127] TODO: Establish a policy for handling and reporting security vulnerabilities found in the package.

## [TRD-140] Scalability & Performance (Technical)

The primary performance bottleneck is the initial download and parsing of the large XML file. The caching strategy directly addresses this.

[TRD-14] The diskcache library is performant for on-disk key-value storage.

[TRD-66] The dynamic TTL calculation prevents stale data while minimizing network requests, balancing freshness and performance.

[TRD-59] The XML should be parsed in a memory-efficient way, for example, by iterating over the file rather than loading the entire DOM into memory at once if it becomes a concern.

## [TRD-81] Deployment & Operations

[TRD-56] CI/CD: A CI/CD pipeline (e.g., using GitHub Actions) will be set up to automatically run pytest and uv pip audit on every push and pull request.

[TRD-18] Packaging: The package will be configured using pyproject.toml and built into a wheel for distribution on PyPI.

[TRD-114] Logging: Logging will be configured in the CLI module. The root logger will be configured with a StreamHandler to print to the console. The log level will be set to INFO by default and changed to DEBUG if the corresponding CLI flag is present.

[TRD-46] Monitoring: Not applicable for a library, but logs will provide operational insight into its usage within a larger application.

## [TRD-38] Detailed Functional Requirements (Technical View)

### [TRD-40] Caching Module

[TRD-159] Will use diskcache.Cache initialized with the path from the ECB_CACHE environment variable (or its default).

[TRD-35] Will contain a function _get_next_update_ttl() -&gt; int which returns the number of seconds until the next ECB update.

[TRD-104] _get_next_update_ttl Algorithm:

[TRD-137] Determine the ECB's next update time. Assume 16:00 CET on weekdays that are not TARGET2 holidays.

[TRD-45] TODO: Confirm the official ECB update time and find a reliable source for the TARGET2 holiday calendar.

[TRD-102] Get the current time (timezone-aware).

[TRD-157] If the current time is before today's update time (and today is an update day), the TTL is the difference.

[TRD-48] If the current time is after today's update time, find the next valid update day (skipping weekends and holidays) and calculate the TTL until that day's update time.

[TRD-124] When setting data, it will use cache.set(key, value, expire=ttl).

### [TRD-115] Data Source Module

[TRD-37] _fetch_data() will use requests.get() to download the XML, with a reasonable timeout. It will catch requests.exceptions.RequestException and handle it as a network error.

[TRD-100] _parse_data(xml_string) will use xml.etree.ElementTree.iterparse for efficient parsing. It will build the nested dictionary structure described in section 2.5 and return it.

### [TRD-49] Core Module

[TRD-41] Algorithm:

[TRD-75] Request data from the Caching Module.

[TRD-22] If the Caching Module triggers a fetch/parse due to a cache miss, handle any potential network/parse errors. If a network error occurs, attempt to read from the cache, ignoring the TTL, as per requirements.

[TRD-62] Once data is loaded, determine the target date. If date_obj is None, use the latest date key from data['rates']. Otherwise, use the provided date_obj.

[TRD-119] Create a sorted list of all available dates from the data, in descending order.

[TRD-76] Starting from the target date, iterate backwards through the sorted list.

[TRD-64] For each date, check if both base_cur and dest_cur exist in that day's rates dictionary (note: 'EUR' is implicitly available with a rate of 1.0).

[TRD-92] The first date found that contains both currencies is the effective_date.

[TRD-52] If the loop completes without finding a suitable date, raise a RateNotFound exception.

[TRD-6] If effective_date is different from the originally requested date, log a WARNING.

[TRD-55] Retrieve the rates for the effective_date: rate_base = rates[effective_date].get(base_cur, 1.0) and rate_dest = rates[effective_date].get(dest_cur, 1.0).

[TRD-121] Calculate the final rate: (1 / rate_base) * rate_dest. Return the result.

## [TRD-126] Non-Functional Requirements (Technical Detail & Verification)

[TRD-151] Response Time (Cached): The p99 latency for a get_rate call that results in a cache hit must be below 10ms.

[TRD-148] Verification: A benchmark test will be created using pytest-benchmark to measure the performance of repeated calls.

[TRD-128] Response Time (Uncached): The time for a get_rate call that results in a cache miss should primarily be determined by the network download and parsing time. This should be benchmarked but will not have a strict threshold.

[TRD-39] Verification: Log the duration of the download and parse steps.

[TRD-42] Development Methodology & Test Coverage: Development will follow a Test-Driven Development (TDD) approach. Consequently, code coverage must be maintained at or above 90%.

[TRD-61] Verification: Adherence to TDD will be verified through code reviews. A tool like pytest-cov will be integrated into the CI/CD pipeline, failing the build if coverage drops below the 90% threshold.

[TRD-31] Logging Verification: Unit tests will assert that specific log messages (e.g., fallback warnings, cache refresh events) are emitted under the correct conditions. The caplog fixture in pytest will be used for this.

## [TRD-87] Phase 1: MVP (Minimum Viable Product)

Goal:

 Deliver the core 

CurrencyRates

 class with working 

get_rate

 functionality, including date fallback and basic caching.

[TRD-110] Scope:

[TRD-72] CurrencyRates class.

[TRD-158] get_rate method with fallback logic.

[TRD-129] Data fetching and parsing from the ECB URL.

[TRD-79] Caching with diskcache using a simple, fixed 1-day TTL to start.

[TRD-153] A comprehensive unit test suite for the above features.

[TRD-8] Milestones:

[TRD-103] M1: Setup project structure with uv and pyproject.toml. Implement the Data Source Module to fetch and parse the XML.

[TRD-54] M2: Implement the Core Module with the get_rate method and date fallback logic.

[TRD-160] M3: Integrate the Caching Module with a fixed 1-day TTL.

[TRD-143] M4: Write comprehensive unit tests for all implemented logic, ensuring correctness of rate calculation and fallback behavior.

## [TRD-12] Phase 2 onwards (Future Enhancements)

Goal:

 Add the CLI, dynamic TTL, and final polish.

[TRD-90] Scope:

[TRD-105] Implement the dynamic TTL calculation based on the ECB schedule.

[TRD-91] Implement the manual cache refresh method.

[TRD-145] Build the CLI using Typer.

[TRD-139] Integrate the logging framework throughout the codebase.

[TRD-25] Expand unit tests to cover all new functionality.

[TRD-122] Milestones:

[TRD-132] M1: Research and implement the ECB schedule logic to enable the dynamic TTL in the Caching Module. Update tests.

[TRD-60] M2: Implement the refresh_cache method in the Core Module.

[TRD-144] M3: Implement the CLI module with query and refresh commands, and the --debug flag for logging.

[TRD-147] M4: Publish version 1.0.0 of the package to PyPI.

[TRD-68] TODO: Refine post-MVP phasing based on MVP outcomes and feedback.

## [TRD-118] Components Diagram

TODO: Review and refine component boundaries and interactions with Tech Lead/Architect based on finalized architecture.

## [TRD-17] User Experience Flow Diagram

TODO: Validate UX flow against all key User Stories and edge cases identified in PRD 1.3.

## [TRD-7] Entity Relationship Diagram (ERD)

<u>

Note: This ERD models the logical structure of the data parsed from the XML, not a relational database schema.

</u>

TODO: Review data types and relationships with development team. This conceptual model should guide the parsing logic.

## [TRD-117] User Interface Key Requirements

### [TRD-107] General Look & Feel

The user interface is a Command-Line Interface (CLI). All output must be plain text.

[TRD-5] Interaction should be clear, standard, and feel familiar to users of command-line tools.

[TRD-94] Successful command execution should print the result to standard output.

[TRD-1] All errors, warnings, and debug messages should be printed to standard error.

[TRD-161] The user flow is centered around two main commands: query and refresh.

[TRD-32] TODO: Finalize style guide/design system details with UI/UX designer. This is a CLI, so the "style guide" refers to consistent output formatting, error messaging, and argument naming conventions.

### [TRD-101] Key Screens / Views (Commands)

#### [TRD-27] Help View

[TRD-13] Trigger: ecbrates --help, ecbrates query --help, etc.

[TRD-134] Content: Auto-generated by Typer. Must clearly list all available commands (query, refresh), their purpose, and all associated arguments and options with descriptions.

#### [TRD-23] Query Command

[TRD-142] Invocation: ecbrates query &lt;BASE_CUR&gt; [DEST_CUR] [--date &lt;YYYY-MM-DD&gt;] [--debug]

[TRD-154] Components:

[TRD-108] BASE_CUR (Required): The base currency 3-letter code (e.g., USD).

[TRD-2] DEST_CUR (Optional): The destination currency 3-letter code. Defaults to EUR.

[TRD-152] --date &lt;YYYY-MM-DD&gt; (Optional): The target date. If omitted, the latest available date is used.

[TRD-156] --debug (Optional): A flag to enable DEBUG level logging.

[TRD-97] Success Output:

[TRD-9] 1.0 USD = 0.9523 EUR on 2023-10-27

[TRD-116] Error Output (to stderr):

[TRD-26] "Error: Invalid currency code 'US'."

[TRD-53] "Error: Invalid date format '27-10-2023'. Please use YYYY-MM-DD."

[TRD-3] "Error: Could not find any exchange rate for currencies USD, JPY."

[TRD-150] Links to UX Flow: Query Flow.

#### [TRD-96] Refresh Command

[TRD-141] Invocation: ecbrates refresh

[TRD-73] Components: None, it's a simple command.

[TRD-65] Success Output:

[TRD-85] Cache successfully refreshed.

[TRD-19] Error Output (to stderr):

[TRD-78] Error: Cache refresh failed due to a network error. Please check your connection.

[TRD-70] Links to UX Flow: Refresh Flow.

### [TRD-51] Data Presentation

[TRD-89] Exchange Rates: Must be displayed as floating-point numbers.

[TRD-44] TODO: Clarify the required precision (number of decimal places) for displaying exchange rates. Stakeholder: Product Manager

[TRD-106] Dates: Must always be presented in YYYY-MM-DD format for consistency.

[TRD-111] Log Messages:

[TRD-30] INFO: [INFO] Cache miss. Fetching new data from ECB...

[TRD-155] WARNING: [WARNING] No data for 2023-10-28. Using fallback date 2023-10-27.

[TRD-125] DEBUG: [DEBUG] Calculated next update TTL: 3600 seconds.
