from pathlib import Path
from datetime import datetime


line ='"Zimbabwe";"Victoria Falls";"962"\n'
columns = line.split(";")

for i in columns:
    print(i)