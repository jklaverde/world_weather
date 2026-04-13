
import requests
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import re


class ScrapCitiesWmo:

    url_cities_list = ""        # remote url in which the txt file with the list of cities is available
    path_source_file = ""       # is the path in which the files will be create (once scrapped from internet)
    url_city_scrap = ""         # the generic url with the weather information per city

    def __init__(self, url_cities_list: str, path_source_files: str, url_city_scrap: str):
        self.url_cities_list = url_cities_list
        self.path_source_file = path_source_files
        self.url_city_scrap = url_city_scrap

    
    def scrap_city_weather(self, country:str, city_name: str, city_id: str, file_name: str) -> str:
        url_city_scrap = self.url_city_scrap.replace("cityid", city_id)
        response = requests.get(url_city_scrap)

        file_name_timestamp = file_name.split(".")[0].split("_", 1)[1]   # extract the "yyyymmdd_hhmmss" of the file name

        # response format as JSON
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"The json file for city {city_id} is not valid, city name: {city_name}")
            return

        json_output_file = Path(f"{self.path_source_file}/{country}/{city_name}_{file_name_timestamp}.json")
        json_output_file.parent.mkdir(parents=True, exist_ok=True)
        json_output_file.write_text(json.dumps(data, indent=4))
        print(f"        Scrapping {country}, just finished the city: {city_name}         ")

    

    # this method scrap the cities and store them in folder "output_path"
    def scrap_cities_list(self) -> str:
        # takes timestamp to concatenate with the cities file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        FILE_NAME = f"cities_{timestamp}.csv"
        cities_scrapped = Path(f"{self.path_source_file}/{FILE_NAME}")
        cities_scrapped.parent.mkdir(parents=True, exist_ok=True)
        cities_scrapped.touch()
        
        # request the content of cities to remote url
        response = requests.get(self.url_cities_list)

        # read the response line per line
        lines = response.text.splitlines()
        columns = [] 
        with open(f"{self.path_source_file}/cities_{timestamp}.csv", "w") as f:
            for line in lines:
                columns = line.split(";")
                if len(columns) > 1:            # if there are "country", "city", "id", write it in the file
                    f.write("".join(line) + "\n")
        return FILE_NAME
    

    # scrap the weather of the cities available in the most recent cities list
    def scrap_weather_from_latest_city_file(self):
        # select the latest file with the list of cities
        files = list(Path(self.path_source_file).glob("*.csv"))
        latest_file = max(files, key=lambda f: f.stem) if files else None

        columns = []  # represent the columns of the file ("country", "city", "id")
        cities = {}
        if latest_file:
            with open(latest_file, "r") as f:
                for line in f:
                    columns = line.replace('\n', '').split(";")
                    country =  re.sub(r'[\\\/]', '', columns[0].replace('"', '')) 
                    city_name =  re.sub(r'[\\\/]', '', columns[1].replace('"', '')) 
                    city_id =  re.sub(r'[\\\/]', '', columns[2].replace('"', '')) 
                    
                    cities[city_id] = [country, city_name] # 0: country_name, 1: city_name

        if cities:
            for key, value in cities.items():
                response = requests.get(self.url_city_scrap)
                self.scrap_city_weather(country=value[0], city_name=value[1], city_id=key, file_name=latest_file.name)
    

