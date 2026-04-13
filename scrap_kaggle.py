
import requests
import json
from pathlib import Path
import kagglehub



class ScrapKaggle:


    def __init__(self):
        return


    # download the latest version of global-weather-repository available in kaggle
    def _download_kaggle_repository(self, remote_repository_name: str, source_folder: str) -> str:
        print ("        Downloading kaggle global-weather-repository        ")
        # create an output path for kaggle files
        output_path = Path(source_folder)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        path = kagglehub.dataset_download(remote_repository_name, force_download=True ,  output_dir=output_path)

        return path

    

