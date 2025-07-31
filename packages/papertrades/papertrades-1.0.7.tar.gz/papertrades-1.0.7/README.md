# papertrades

`papertrades` is a package to simulate and analyze paper trades in Python.

Many tools exist online for simulation paper trading. However, users may not find them to be up to their standards. `papertrades` changes this by allowing full customization.

- HomePage: https://github.com/kzhu2099/Paper-Trades
- Issues: https://github.com/kzhu2099/Paper-Trades/issues

[![PyPI Downloads](https://static.pepy.tech/badge/papertrades)](https://pepy.tech/projects/papertrades) ![PyPI version](https://img.shields.io/pypi/v/papertrades.svg)

Author: Kevin Zhu

THIS IS NOT FINANCIAL ADVICE; `papertrades` IS A TOOL TO SIMULATE THE MARKET FOR EDUCATIONAL PURPOSES.

## Features

- multiple portfolios
- automatic asset price calculation based on your last trade
- plotting of the value of your portfolio
- remaining cash (balance) calculation & value calculation
- asset breakdown

## Installation

To install `papertrades`, use pip: ```pip install papertrades```.

However, many prefer to use a virtual environment (or any of their preferred choice).

macOS / Linux:

```sh
# make your desired directory
mkdir /path/to/your/directory
cd /path/to/your/directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install papertrades
source .venv/bin/activate
pip install papertrades

deactivate # when you are completely done
```

Windows CMD:

```sh
# make your desired directory
mkdir C:path\to\your\directory
cd C:path\to\your\directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install papertrades
.venv\Scripts\activate
pip install papertrades

deactivate # when you are completely done
```

## Usage

Create a portfolio with a starting balance and a path for its trades.
Once you make trades, you make save the trades to use later, and load them from the portfolio.
See the example for complete functionality with all methods!

After a lot of time,

## License

The License is an MIT License found in the LICENSE file.