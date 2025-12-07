# Weather Dashboard CLI

A command-line weather application that fetches current conditions and 5-day forecasts using the OpenWeatherMap API. Features colorful terminal output, favorite cities management, and an interactive menu interface.

![Tests](https://github.com/cameronrubino/is4010-final-Weather-Dashboards-CLI/actions/workflows/tests.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/cameronrubino/is4010-final-Weather-Dashboards-CLI.git
   cd is4010-final-Weather-Dashboards-CLI
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your API key:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your [OpenWeatherMap API key](https://openweathermap.org/api).

## Usage

**Get current weather:**
```bash
python weather.py London
```

**Get 5-day forecast:**
```bash
python weather.py Tokyo -f
```

**Add a city to favorites:**
```bash
python weather.py -a Paris
```

**List favorite cities:**
```bash
python weather.py -l
```

**Show weather for all favorites:**
```bash
python weather.py -s
```

**Remove a favorite:**
```bash
python weather.py -r London
```

**Interactive menu mode:**
```bash
python weather.py
```

## Features

- Current weather lookup for any city worldwide
- 5-day weather forecast with detailed conditions
- Save and manage favorite cities
- View weather for all favorites at once
- Colorful terminal output with Rich library
- Weather condition emojis (☀️ 🌧️ ❄️ ⛈️)
- Interactive menu interface
- Comprehensive error handling

## Testing

Run the test suite with pytest:

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

## AI-Assisted Development

This project was developed with assistance from AI tools including GitHub Copilot and Claude. For details, see [AGENTS.md](AGENTS.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
