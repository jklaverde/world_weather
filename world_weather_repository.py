# International University (Internationale Hochschule) - Written assignment complementary project

'''
This academic project is complementary to written assignment of the course "Data Quality and Data Wrangling" (DLBDSDQDW01)

Task: Scrape the Web
Student Name: Juan Carlos Laverde
Student Id: UPS10797707
Tutor: Dr. PhD. Christian Müller-Kett


The project has as purpose to practice and train the skills acquired along the course
specifically scrapping a web application through APIs, in this case

'''

from pathlib import Path
import pandas as pd
import polars as pl
from scrap_kaggle import ScrapKaggle
from scrap_wmo import ScrapCitiesWmo
from scrap_utils import ScrapUtil
import json
import argparse

# Folder in which the remote files (kaggle) are downloaded locally
SOURCE_FOLDER = Path("source_repository")
PROCESSED_FILES = Path("processed_files")


kaggle_folder = {
    "source": SOURCE_FOLDER/"kaggle",
    "kaggle": PROCESSED_FILES/"kaggle",
    "hdf5": PROCESSED_FILES/"kaggle"/"hdf5",
    "parquet": PROCESSED_FILES/"kaggle"/"parquet"
}

wmo_folder = {
    "source": SOURCE_FOLDER/"wmo",
    "kaggle": PROCESSED_FILES/"wmo",
    "hdf5": PROCESSED_FILES/"wmo"/"hdf5",
    "parquet": PROCESSED_FILES/"wmo"/"parquet"
}


# ensures directory structure
def _ensure_directory_structure():
    print("        Creating folder structure (if not already exists)       ")

    # source and processed folder
    Path(SOURCE_FOLDER).mkdir(exist_ok=True)
    Path(PROCESSED_FILES).mkdir(exist_ok=True)

    # create the folder structure for kaggle files (if not exists)
    for folder in kaggle_folder.values():
        Path(folder).mkdir(exist_ok=True)
    
    # directory for file processed for world meteorological organization
    for folder in wmo_folder.values():
        Path(folder).mkdir(exist_ok=True)





# main
def main():
    parser = argparse.ArgumentParser(description="World Weather Repository scraper")
    parser.add_argument("--cities", nargs="+", metavar="CITY",
                        help="Scrape only the specified city names (case-insensitive, exact match)")
    parser.add_argument("--countries", nargs="+", metavar="COUNTRY",
                        help="Scrape all cities within the specified countries (case-insensitive, exact match)")
    parser.add_argument("--skip-kaggle", action="store_true",
                        help="Skip the Kaggle download and HDF5 conversion")
    parser.add_argument("--update-city-list", action="store_true",
                        help="Re-fetch the WMO city list before scraping (default: reuse latest cached)")
    args = parser.parse_args()

    _ensure_directory_structure()

    if not args.skip_kaggle:
        scrap_kaggle = ScrapKaggle()
        ruta = scrap_kaggle._download_kaggle_repository("nelgiriyewithana/global-weather-repository", kaggle_folder["source"])
        ScrapUtil._convert_csv_to_hdf5(kaggle_folder["source"]/"GlobalWeatherRepository.csv", kaggle_folder["hdf5"]/"GlobalWeatherRepository.h5")
    else:
        print("        Skipping Kaggle download (--skip-kaggle)        ")

    # instantiate a scrap object for wmo
    scrap_cities_wmo = ScrapCitiesWmo(url_cities_list="https://worldweather.wmo.int/en/json/full_city_list.txt",
                                      path_source_files=wmo_folder["source"],
                                      url_city_scrap="https://worldweather.wmo.int/en/json/cityid_en.json")

    if args.update_city_list:
        cities_file_name = scrap_cities_wmo.scrap_cities_list()
        print(f"        Cities file name: {cities_file_name}            ")
    else:
        print("        Reusing latest cached city list (use --update-city-list to refresh)        ")

    scrap_cities_wmo.scrap_weather_from_latest_city_file(cities=args.cities, countries=args.countries)



if __name__ == "__main__":
    main()