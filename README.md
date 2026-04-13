# World Weather Repository

A Python-based data collection and wrangling project that aggregates global weather data from two independent sources:

- **Kaggle** — [Global Weather Repository](https://www.kaggle.com/datasets/nelgiriyewithana/global-weather-repository) (static, historical dataset)
- **WMO** — [World Meteorological Organization](https://worldweather.wmo.int) (live weather data per city)

---

## Table of Contents

- [Project Structure](#project-structure)
- [Data Sources](#data-sources)
- [Setup](#setup)
- [Usage](#usage)
- [CLI Arguments](#cli-arguments)
- [Examples](#examples)
- [Module Reference](#module-reference)

---

## Project Structure

```
world_weather_repository/
├── world_weather_repository.py   # Main entry point
├── scrap_kaggle.py               # Kaggle dataset downloader
├── scrap_wmo.py                  # WMO city list and weather scraper
├── scrap_utils.py                # CSV-to-HDF5 conversion utility
├── requirements.txt              # Python dependencies
│
├── source_repository/            # Raw downloaded/scraped data
│   ├── kaggle/
│   │   └── GlobalWeatherRepository.csv
│   └── wmo/
│       ├── cities_YYYYMMDD_HHMMSS.csv   # Cached city lists
│       └── <Country>/
│           └── <City>_YYYYMMDD_HHMMSS.json
│
└── processed_files/              # Converted/processed data
    ├── kaggle/
    │   ├── hdf5/
    │   │   └── GlobalWeatherRepository.h5
    │   └── parquet/
    └── wmo/
        ├── hdf5/
        └── parquet/
```

---

## Data Sources

### Kaggle — Global Weather Repository

A static CSV dataset (~34 MB, ~134,000 records) with historical weather observations worldwide.

| Field Category | Fields |
|---|---|
| Location | country, location_name, latitude, longitude, timezone |
| Weather | temperature_celsius, temperature_fahrenheit, condition_text |
| Wind | wind_mph, wind_kph, wind_degree, wind_direction, gust_mph, gust_kph |
| Atmosphere | humidity, cloud, pressure_mb, precip_mm, vis_km, uv_index |
| Air Quality | air_quality_CO, air_quality_O3, air_quality_NO2, air_quality_SO2, air_quality_PM2.5, air_quality_PM10, air_quality_us-epa-index, air_quality_gb-defra-index |
| Astronomy | sunrise, sunset, moonrise, moonset, moon_phase, moon_illumination |
| Timestamp | last_updated_epoch, last_updated |

After download, the CSV is automatically converted to HDF5 format (key: `global_weather`) for efficient storage and retrieval.

### WMO — World Meteorological Organization

Live weather data scraped from [worldweather.wmo.int](https://worldweather.wmo.int). The process has two steps:

1. **City list** — fetched from `full_city_list.txt` and saved locally as `cities_YYYYMMDD_HHMMSS.csv`. By default the latest cached file is reused to avoid unnecessary requests.
2. **Weather per city** — one JSON file per city, organized into `source_repository/wmo/<Country>/` directories.

---

## Setup

### Prerequisites

- Python 3.10+
- A Kaggle account with an API token configured (`~/.kaggle/kaggle.json`)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd world_weather_repository

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

### Kaggle API Setup

Follow the [Kaggle API documentation](https://github.com/Kaggle/kaggle-api#api-credentials) to place your `kaggle.json` credentials file in `~/.kaggle/`.

---

## Usage

Run the main script from the project root:

```bash
python world_weather_repository.py [OPTIONS]
```

With no arguments, the script performs a **full run**:
1. Downloads the Kaggle dataset and converts it to HDF5
2. Reuses the latest cached WMO city list
3. Scrapes live weather data for every city in the list

---

## CLI Arguments

| Argument | Type | Default | Description |
|---|---|---|---|
| `--cities` | one or more strings | _(none)_ | Scrape only the specified city names |
| `--countries` | one or more strings | _(none)_ | Scrape all cities within the specified countries |
| `--skip-kaggle` | flag | `False` | Skip the Kaggle download and HDF5 conversion |
| `--update-city-list` | flag | `False` | Re-fetch the WMO city list before scraping |

**Matching rules:**
- City and country names are matched **case-insensitively** and **exactly** (e.g. `germany` matches `Germany` but not `West Germany`)
- When both `--cities` and `--countries` are provided, a city is scraped if it matches **either** filter (union)
- If the filters produce no matches, the script prints a warning and exits without scraping

---

## Examples

```bash
# Full run (Kaggle + all WMO cities, reuse cached city list)
python world_weather_repository.py

# Scrape WMO data for specific countries only, skip Kaggle
python world_weather_repository.py --skip-kaggle --countries Germany France

# Scrape WMO data for specific cities only, skip Kaggle
python world_weather_repository.py --skip-kaggle --cities "New York" London Tokyo

# Mix: scrape all cities in Brazil plus the city of Berlin
python world_weather_repository.py --skip-kaggle --countries Brazil --cities Berlin

# Refresh the WMO city list, then scrape all cities in Japan
python world_weather_repository.py --skip-kaggle --update-city-list --countries Japan

# Full run and refresh the WMO city list
python world_weather_repository.py --update-city-list
```

---

## Module Reference

### `world_weather_repository.py`

Main entry point. Parses CLI arguments, ensures the directory structure exists, and orchestrates the Kaggle and WMO scraping pipelines.

### `scrap_kaggle.py` — `ScrapKaggle`

| Method | Description |
|---|---|
| `_download_kaggle_repository(remote_repository_name, source_folder)` | Downloads the specified Kaggle dataset to `source_folder` using `kagglehub` |

### `scrap_wmo.py` — `ScrapCitiesWmo`

| Method | Description |
|---|---|
| `scrap_cities_list()` | Fetches the WMO city list and saves it as `cities_YYYYMMDD_HHMMSS.csv`. Returns the file name. |
| `scrap_city_weather(country, city_name, city_id, file_name)` | Fetches and saves the weather JSON for a single city |
| `scrap_weather_from_latest_city_file(cities, countries)` | Reads the latest cached city list and scrapes weather data, optionally filtered by `cities` and/or `countries` |

### `scrap_utils.py` — `ScrapUtil`

| Method | Description |
|---|---|
| `_convert_csv_to_hdf5(source_csv, target_hdf5)` | Reads a CSV file with pandas and writes it as an HDF5 file (key: `global_weather`) |
