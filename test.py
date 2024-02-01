import pandas as pd
import numpy as np

df = pd.read_csv('./pd_database.csv')
ppdata =df['ppdata']
def latlon(value):
    lat = value[:, 0]
    lon = value[:, 1]
    return lat, lon

for i in range(len(ppdata)):
    value = ppdata[i]
    value = value[1:-1]
    value = value.split()
    value = np.array(value).reshape(-1, 8)
    lat, lon = latlon(value)
    print(lat)
    print(lon)
print(1)