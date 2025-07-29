CLI Usage Examples
==================

This section provides comprehensive examples of how to use the Portfolio Toolkit command-line interface (CLI). The CLI has been built using the Click framework for an intuitive and user-friendly experience.

Installation and Quick Start
-----------------------------

After installing the package, you can access the CLI directly:

.. code-block:: bash

   # Install the package
   pip install portfolio-toolkit

   # View available commands
   portfolio-toolkit --help

   # Check version
   portfolio-toolkit --version

Basic Commands
--------------

Help and Information
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Main help - shows all command groups
   portfolio-toolkit --help

   # Help for specific command group
   portfolio-toolkit ticker --help
   portfolio-toolkit portfolio --help
   portfolio-toolkit optimization --help
   portfolio-toolkit watchlist --help

   # Help for specific subcommand
   portfolio-toolkit ticker print --help
   portfolio-toolkit portfolio plot --help

Version Information
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Show version
   portfolio-toolkit --version

Command Structure Overview
~~~~~~~~~~~~~~~~~~~~~~~~~~

The CLI is organized into logical command groups:

.. code-block:: text

   Portfolio Toolkit CLI
   ├── ticker          Ticker analysis commands
   │   ├── print       Print ticker information
   │   ├── plot        Plot ticker data
   │   ├── compare     Compare multiple tickers
   │   ├── correlation Calculate correlations
   │   ├── evolution   Plot price evolution
   │   └── export      Export ticker data
   ├── portfolio       Portfolio analysis commands
   │   ├── print       Print portfolio information
   │   ├── plot        Plot portfolio data
   │   ├── open-positions    Show open positions
   │   ├── closed-positions  Show closed positions
   │   ├── export      Export portfolio data
   │   └── suggest     Portfolio suggestions
   ├── watchlist       Watchlist analysis commands
   │   └── print       Print watchlist information
   ├── optimization    Portfolio optimization commands
   │   ├── calc        Calculate optimization metrics
   │   ├── optimize    Optimize portfolio
   │   ├── backtest    Backtest strategies
   │   ├── plot        Plot optimization data
   │   ├── print       Print optimization info
   │   └── export      Export optimization data
   └── clear-cache     Clear cached data

Ticker Analysis Commands
------------------------

Ticker Information
~~~~~~~~~~~~~~~~~~

Get detailed information about specific tickers:

.. code-block:: bash

   # Show detailed ticker information
   portfolio-toolkit ticker print info AAPL

   # Show ticker statistics (volatility, mean, etc.)
   portfolio-toolkit ticker print stats AAPL

   # Show beta relative to benchmark
   portfolio-toolkit ticker print beta AAPL

   # Get help for ticker print commands
   portfolio-toolkit ticker print --help

Example output (when implemented):

.. code-block:: text

   📊 Ticker Information: AAPL
   ==================================================
   💰 Currency: USD
   🏢 Company Name        : Apple Inc.
   🏭 Sector             : Technology
   🔧 Industry           : Consumer Electronics
   🌍 Country            : United States
   💹 Market Cap         : $3.2T
   💵 Current Price      : 208.62 USD

Ticker Price Evolution
~~~~~~~~~~~~~~~~~~~~~~

Plot price evolution of specific assets:

.. code-block:: bash

   # Plot single asset evolution
   portfolio-toolkit ticker evolution AAPL USD

   # Plot multiple assets
   portfolio-toolkit ticker evolution AAPL,MSFT,GOOGL EUR

   # Plot with different currency
   portfolio-toolkit ticker evolution SHOP,RY.TO CAD

Ticker Correlation Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Calculate correlation between multiple assets:

.. code-block:: bash

   # Basic correlation analysis
   portfolio-toolkit ticker correlation AAPL,MSFT,GOOGL

   # Correlation with international stocks
   portfolio-toolkit ticker correlation AAPL,ASML,TSM

Example output (when implemented):

.. code-block:: text

   |-------------------------------------|
   | Ticker 1  | Ticker 2  | Correlation |
   |-----------|-----------|-------------|
   | AAPL      | MSFT      | 0.7521      |
   | AAPL      | GOOGL     | 0.6834      |
   | MSFT      | GOOGL     | 0.8102      |
   |-------------------------------------|

Ticker Comparison and Export
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compare multiple tickers and export data:

.. code-block:: bash

   # Compare multiple tickers
   portfolio-toolkit ticker compare AAPL MSFT GOOGL

   # Export ticker data
   portfolio-toolkit ticker export AAPL --format csv

Portfolio Analysis Commands
---------------------------

Portfolio Information and Printing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Display portfolio information in various formats:

.. code-block:: bash

   # Show general portfolio information
   portfolio-toolkit portfolio print -f portfolio.json

   # Show current open positions
   portfolio-toolkit portfolio open-positions -f portfolio.json

   # Show closed positions
   portfolio-toolkit portfolio closed-positions -f portfolio.json

   # Show positions for a specific date
   portfolio-toolkit portfolio open-positions -f portfolio.json -d 2025-06-15

Example output for open positions:

.. code-block:: text

   Current positions as of 2025-07-17:
   | Ticker  | Price Base  | Cost        | Quantity  | Value Base  | Return (%)  |
   |---------|-------------|-------------|-----------|-------------|-------------|
   | AAPL    | 181.06      | 500.25      | 5.00      | 905.29      | 80.97       |
   | __EUR   | 1.00        | 499.75      | 499.75    | 499.75      | 0.00        |
   |---------|-------------|-------------|-----------|-------------|-------------|
   | TOTAL   |             | 1000.00     |           | 1405.04     | 40.50       |

Portfolio Visualization
~~~~~~~~~~~~~~~~~~~~~~~

Plot and visualize portfolio data:

.. code-block:: bash

   # Plot portfolio evolution
   portfolio-toolkit portfolio plot -f portfolio.json

   # Plot with specific date range
   portfolio-toolkit portfolio plot -f portfolio.json --start-date 2025-01-01 --end-date 2025-07-01

Example output: Opens a matplotlib window showing portfolio evolution over time.

Portfolio Export and Suggestions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Export portfolio data and get investment suggestions:

.. code-block:: bash

   # Export portfolio data
   portfolio-toolkit portfolio export -f portfolio.json --format csv

   # Get portfolio suggestions
   portfolio-toolkit portfolio suggest -f portfolio.json

Example export output:

.. code-block:: text

   Date,Ticker,Type,Quantity,Price,Currency
   2023-01-15,AAPL,buy,10,150.25,USD
   2023-02-01,__EUR,deposit,500.00,1.00,EUR
   2023-03-15,AAPL,sell,2,160.50,USD

Watchlist Management Commands
-----------------------------

Watchlist Information
~~~~~~~~~~~~~~~~~~~~~

Manage and analyze your investment watchlists:

.. code-block:: bash

   # Print watchlist information
   portfolio-toolkit watchlist print -f watchlist.json

   # Print specific watchlist
   portfolio-toolkit watchlist print -f watchlist-sector-etf-us.json

Example output (when implemented):

.. code-block:: text

   Watchlist Information:
   | Ticker  | Name                    | Sector      | Price   | Change (%) |
   |---------|-------------------------|-------------|---------|------------|
   | VTI     | Vanguard Total Stock    | ETF         | 245.32  | +0.8%      |
   | QQQ     | Invesco QQQ Trust       | ETF         | 389.45  | +1.2%      |

Portfolio Optimization Commands
-------------------------------

Optimization Calculations
~~~~~~~~~~~~~~~~~~~~~~~~~

Calculate various optimization metrics for your portfolio:

.. code-block:: bash

   # Calculate basic optimization metrics
   portfolio-toolkit optimization calc -f portfolio.json

   # Calculate with specific parameters
   portfolio-toolkit optimization calc -f portfolio.json --risk-tolerance 0.5

Portfolio Optimization
~~~~~~~~~~~~~~~~~~~~~~

Optimize your portfolio allocation:

.. code-block:: bash

   # Basic portfolio optimization
   portfolio-toolkit optimization optimize -f portfolio.json

   # Optimize with constraints
   portfolio-toolkit optimization optimize -f portfolio.json --max-weight 0.3 --min-weight 0.05

Optimization Backtesting
~~~~~~~~~~~~~~~~~~~~~~~~~

Backtest optimization strategies:

.. code-block:: bash

   # Backtest optimization strategy
   portfolio-toolkit optimization backtest -f portfolio.json

   # Backtest with specific date range
   portfolio-toolkit optimization backtest -f portfolio.json --start-date 2023-01-01 --end-date 2024-12-31

Optimization Visualization and Export
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Visualize and export optimization results:

.. code-block:: bash

   # Plot optimization results
   portfolio-toolkit optimization plot -f portfolio.json

   # Print optimization information
   portfolio-toolkit optimization print -f portfolio.json

   # Export optimization data
   portfolio-toolkit optimization export -f portfolio.json --format csv

Export and Debugging Commands
-----------------------------

Data Export
~~~~~~~~~~~

Export various types of data in different formats:

.. code-block:: bash

   # Export portfolio data
   portfolio-toolkit portfolio export -f portfolio.json --format csv

   # Export ticker data
   portfolio-toolkit ticker export AAPL --format json

   # Export optimization results
   portfolio-toolkit optimization export -f portfolio.json --format csv

Utility Commands
----------------

Cache Management
~~~~~~~~~~~~~~~~

Clear cached data to force fresh downloads:

.. code-block:: bash

   # Clear all cache files
   portfolio-toolkit clear-cache

Example output:

.. code-block:: text

   Found 9 cache files to delete:
     - 4 historical data files
     - 5 ticker info files

   Deleted: 20250717-AAPL_historical_data.pkl
   Deleted: 20250717-CADEUR=X_historical_data.pkl
   Deleted: 20250717-USDEUR=X_historical_data.pkl
   Deleted: 20250717-SHOP_historical_data.pkl
   Deleted: 20250717-AAPL_info.pkl

   ✅ Successfully cleared 9 cache files.

Development and Local Usage
---------------------------

For development purposes, you can run commands using the installed package:

.. code-block:: bash

   # Using the installed portfolio-toolkit command
   portfolio-toolkit --help
   portfolio-toolkit portfolio print -f portfolio.json
   portfolio-toolkit ticker print AAPL

   # For development with local changes, use module directly:
   python -m cli.cli --help
   python -m cli.cli portfolio print -f portfolio.json

Common Workflows
----------------

Portfolio Analysis Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complete workflow for analyzing a portfolio:

.. code-block:: bash

   # 1. Check current open positions
   portfolio-toolkit portfolio open-positions -f my_portfolio.json

   # 2. Check closed positions for performance analysis
   portfolio-toolkit portfolio closed-positions -f my_portfolio.json

   # 3. Visualize portfolio evolution
   portfolio-toolkit portfolio plot -f my_portfolio.json

   # 4. Export data for external analysis
   portfolio-toolkit portfolio export -f my_portfolio.json --format csv

   # 5. Get optimization suggestions
   portfolio-toolkit portfolio suggest -f my_portfolio.json

Market Research Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~

Research workflow for new investments:

.. code-block:: bash

   # 1. Get detailed ticker information
   portfolio-toolkit ticker print NVDA

   # 2. Check price evolution
   portfolio-toolkit ticker evolution NVDA EUR

   # 3. Compare with similar stocks
   portfolio-toolkit ticker correlation NVDA,AMD,INTC

   # 4. Compare multiple tickers side by side
   portfolio-toolkit ticker compare NVDA AMD INTC

Portfolio Optimization Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optimize your portfolio allocation:

.. code-block:: bash

   # 1. Calculate current optimization metrics
   portfolio-toolkit optimization calc -f portfolio.json

   # 2. Optimize portfolio allocation
   portfolio-toolkit optimization optimize -f portfolio.json

   # 3. Backtest the optimization strategy
   portfolio-toolkit optimization backtest -f portfolio.json

   # 4. Visualize optimization results
   portfolio-toolkit optimization plot -f portfolio.json

   # 5. Export optimization data
   portfolio-toolkit optimization export -f portfolio.json

Error Handling
--------------

The CLI provides helpful error messages for common issues:

File Not Found
~~~~~~~~~~~~~~

.. code-block:: bash

   $ portfolio-toolkit portfolio print -f nonexistent.json
   Error: Portfolio file 'nonexistent.json' not found.

Invalid Ticker
~~~~~~~~~~~~~~

.. code-block:: bash

   $ portfolio-toolkit ticker print INVALID
   ❌ Error getting ticker information: No data found for ticker INVALID

Missing Arguments
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ portfolio-toolkit ticker evolution
   Usage: portfolio-toolkit ticker evolution [OPTIONS] TICKERS CURRENCY
   Try 'portfolio-toolkit ticker evolution --help' for help.

   Error: Missing argument 'TICKERS'.

Network Issues
~~~~~~~~~~~~~~

.. code-block:: bash

   $ portfolio-toolkit ticker print AAPL
   ❌ Error getting ticker information: HTTPSConnectionPool(...): Max retries exceeded

Best Practices
--------------

1. **Use absolute paths** for portfolio files when running from different directories:

   .. code-block:: bash

      portfolio-toolkit portfolio print -f /path/to/portfolio.json

2. **Clear cache periodically** to ensure fresh data:

   .. code-block:: bash

      portfolio-toolkit clear-cache

3. **Use specific dates** for historical analysis:

   .. code-block:: bash

      portfolio-toolkit portfolio open-positions -f portfolio.json -d 2025-06-30

4. **Combine commands** for comprehensive analysis:

   .. code-block:: bash

      # Analysis script
      portfolio-toolkit clear-cache
      portfolio-toolkit portfolio open-positions -f portfolio.json
      portfolio-toolkit portfolio plot -f portfolio.json
      portfolio-toolkit optimization calc -f portfolio.json

5. **Export data** for further analysis in other tools:

   .. code-block:: bash

      portfolio-toolkit portfolio export -f portfolio.json --format csv > analysis/transactions.csv

6. **Use command groups** to organize your analysis:

   .. code-block:: bash

      # Start with portfolio analysis
      portfolio-toolkit portfolio --help
      
      # Then move to ticker research
      portfolio-toolkit ticker --help
      
      # Finally optimize
      portfolio-toolkit optimization --help

Command Reference Quick Card
----------------------------

.. code-block:: text

   Portfolio Toolkit CLI - Organized Command Structure
   ==================================================

   Main Command Groups:
   ├── ticker              Ticker analysis and research
   │   ├── print           Show ticker information
   │   ├── plot            Plot ticker price data
   │   ├── compare         Compare multiple tickers
   │   ├── correlation     Calculate correlations
   │   ├── evolution       Plot price evolution
   │   └── export          Export ticker data
   │
   ├── portfolio           Portfolio analysis and management
   │   ├── print           Show portfolio information
   │   ├── plot            Plot portfolio data
   │   ├── open-positions  Show current open positions
   │   ├── closed-positions Show historical closed positions
   │   ├── export          Export portfolio data
   │   └── suggest         Get portfolio suggestions
   │
   ├── watchlist           Watchlist management
   │   └── print           Show watchlist information
   │
   ├── optimization        Portfolio optimization tools
   │   ├── calc            Calculate optimization metrics
   │   ├── optimize        Optimize portfolio allocation
   │   ├── backtest        Backtest optimization strategies
   │   ├── plot            Plot optimization results
   │   ├── print           Show optimization information
   │   └── export          Export optimization data
   │
   └── clear-cache         Clear cached data

   Usage Pattern:
   portfolio-toolkit <group> <command> [OPTIONS] [ARGS]

   Examples:
   portfolio-toolkit ticker print AAPL
   portfolio-toolkit portfolio open-positions -f portfolio.json
   portfolio-toolkit optimization calc -f portfolio.json

Getting Help
------------

For more help with any command:

.. code-block:: bash

   # General help
   portfolio-toolkit --help

   # Command group help
   portfolio-toolkit <group> --help

   # Specific command help
   portfolio-toolkit <group> <command> --help

   # Examples
   portfolio-toolkit ticker --help
   portfolio-toolkit portfolio print --help
   portfolio-toolkit optimization calc --help
