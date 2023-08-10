# Crypto Arbitrage Analyzer with Dash 💼 📈

Harness the power of Python and Dash Framework to explore and visualize real-time arbitrage opportunities across various
crypto platforms!

## Features 🌟

- **Live Arbitrage Visualization**: Witness real-time differences in asset prices across platforms.
- **Interactive Dashboards**: Deep dive into data with intuitive and dynamic charts.
- **Cross-Platform Analysis**: Compare opportunities across multiple crypto exchanges.
- **Responsive Design**: Access your analyzer on any device.

## Built With 🛠️

- [Python](https://www.python.org/)
- [Dash Framework](https://plotly.com/dash/)

## Getting Started 🚀

### Prerequisites

- Python 3.10.x
- pip

or

- docker
- docker-compose

### Installation

1. Clone the repo:

```bash
git clone https://github.com/StepanTita/crypto-trading.git
```

2. Install necessary python packages:

```bash
pip install -r requirements.txt
```

3. Add `CONFIG` environment variable to contain the path to the config file.
4. Add `LOCALE` environment variable to contain the path to `localization.yaml`
5. Change current directory to backend: `cd backend`
4. Start the server with `python wsgi.py` and access UI on localhost:9090

## Configuration ⚙️

- **config.yaml** - this file configures the dates range, symbols, and platforms, as well as database connection
- **backend/config.py** - is the flask configuration file, normally you should not use that
- **localization.yaml** -

## License 📄

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.

## TODO:

- p2p arbitrage