Document: Files Tree [FILE]
  └── Files Tree
      ├── pyproject.toml                          // Project configuration and dependency management file.
      ├── README.md                               // Provides documentation and usage examples for the project.
      ├── .gitignore                              // Configuration file for ignoring files in version control.
      ├── src                                     // Container directory for the application's source code.
      │   └── ecbrates                            // The main Python package directory for 'ecbrates'.
      │       ├── __init__.py                     // Initializes the Python package and defines its public API.
      │       ├── core.py                         // Contains the core business logic and CurrencyRates class.
      │       ├── cache.py                        // Manages on-disk caching with dynamic TTL to boost performance.
      │       ├── datasource.py                   // Handles fetching and parsing of data from the ECB source.
      │       ├── cli.py                          // Provides the command-line interface (CLI) for the application.
      │       └── exceptions.py                   // Defines custom application-specific exceptions.
      └── tests                                   // Directory for all automated tests, supporting a Test-Driven Development (TDD) approach.
          ├── __init__.py                         // Test package initializer.
          ├── test_core.py                        // Tests for the core business logic.
          ├── test_cache.py                       // Tests for the caching module.
          ├── test_datasource.py                  // Tests for the data source module.
          ├── test_cli.py                         // Tests for the command-line interface.
          └── conftest.py                         // Pytest fixtures and test configuration file.