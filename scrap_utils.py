
from pathlib import Path
import pandas as pd


class ScrapUtil:

    # convert to hdf5 with pandas
    @staticmethod
    def _convert_csv_to_hdf5(source_csv: str, target_hdf5: str):
        print(f"        Converting from: {source_csv} to {target_hdf5}                  ")
        # read and create a data frame with the csv content
        csv_path = Path(source_csv)
        df = pd.read_csv(csv_path)

        # crete a new file hdf5 
        output_path = Path(target_hdf5)
        output_path.parent.mkdir(exist_ok=True)
        df.to_hdf(output_path, key="global_weather", mode="w")
        print(f"\n      HDF5 saved to: {output_path}")