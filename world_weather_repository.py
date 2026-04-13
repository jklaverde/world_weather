
'''


'''

from pathlib import Path
import pandas as pd
import polars as pl
from scrap_kaggle import ScrapKaggle
from scrap_wmo import ScrapCitiesWmo
from scrap_utils import ScrapUtil
import json

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
    _ensure_directory_structure()
    scrap_kaggle = ScrapKaggle()
    ruta = scrap_kaggle._download_kaggle_repository("nelgiriyewithana/global-weather-repository", kaggle_folder["source"])

    #Converts the csv file downloaded to hdf5
    ScrapUtil._convert_csv_to_hdf5(kaggle_folder["source"]/"GlobalWeatherRepository.csv", kaggle_folder["hdf5"]/"GlobalWeatherRepository.h5")

    # instantiate a scrap object for wmo
    scrap_cities_wmo = ScrapCitiesWmo(url_cities_list="https://worldweather.wmo.int/en/json/full_city_list.txt",
                                      path_source_files=wmo_folder["source"],
                                      url_city_scrap="https://worldweather.wmo.int/en/json/cityid_en.json")
    
    # scrap the list of cities and creates a file on output_path (cities_yyyymmdd_hhmmss)
    cities_file_name = scrap_cities_wmo.scrap_cities_list()
    print(f"        Cities file name: {cities_file_name}            ")

    scrap_cities_wmo.scrap_weather_from_latest_city_file()

    

if __name__ == "__main__":
    main()