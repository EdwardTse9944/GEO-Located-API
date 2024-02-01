import pickle
import pandas as pd
from datetime import datetime

import numpy as np
from tqdm import tqdm

pickle_path = '/home/campus.ncl.ac.uk/b7000659/PycharmProjects/GeoTrackNet/GeoTrackNet/data/2208_2310/data_preprocessing/ct_estncl_2208_2310_data_valid.pkl'
with open(pickle_path, 'rb') as f:
    data = pickle.load(f)

# transfer the datetime from date ino timestamp
def custom_parse(dt_str):

    return datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')
for key, value in tqdm(data.items()):
    for i in range(len(value)):
        value[i][5] = custom_parse(value[i][5]).timestamp()
DATA = {}
count = 1
for value in tqdm(data.values()):
    value = value.astype(float)
    DATA[count] = value
    count += 1



#  interpliation (diff/dt)
def t_split(start, end, n):
    if n==0:
        return []
    step = (end - start + 1) / n
    res = [start + i * step for i in range(n)]

    return res

data_itp = {}
count = 1
for key, value in tqdm(DATA.items()):
    x = t_split(value[0, 5].astype(int), value[-1, 5].astype(int), len(value))
    _lon_ip = np.interp(x, value[:, 5], value[:, 1])
    _lat_ip = np.interp(x, value[:, 5], value[:, 0])
    data_itp[count] = np.array([_lat_ip, _lon_ip, value[:, 2], value[:, 3],
                                value[:, 4], value[:, 5], value[:, 6], value[:, 7]]).transpose()
    count += 1


# difference locolization
# data_difloc = {}
# count = 1
# for key, value in tqdm(data_itp.items()):
#     diff_lat = np.diff(value[:, 0].astype(float), n=1, axis = 0)
#     diff_lon = np.diff(value[:, 1].astype(float), n=1, axis = 0)
#     data_difloc[count] = np.array([diff_lat, diff_lon, value[1:, 2], value[1:, 3], value[1:, 4], value[1:, 5], value[1:, 6], value[1:, 7]]).transpose()
#     count += 1



# add 2 zeros colounm

# for key, value in tqdm(data_itp.items()):
#     zero_column = np.zeros((1, len(value)), dtype=float)
#     data_itp[key] = np.insert(data_itp[key], 5, zero_column, axis=1)
#     data_itp[key] = np.insert(data_itp[key], 6, zero_column, axis=1)

ordered_dict = {}
new_key = 1
for key in data_itp:
    ordered_dict[new_key] = data_itp[key].astype(float)
    new_key += 1






with open('./data_valid.pkl', 'wb') as f:
    pickle.dump(ordered_dict, f)


# Convert the dictionary to a DataFrame
df = pd.DataFrame.from_dict(ordered_dict, orient='index').reset_index()
df.columns = ['index', 'ppdata']

# Display the first few rows of the DataFrame
df.to_csv('./data_valid.csv',index=False)




# def ts2dt(ts):
#     m = datetime.fromtimestamp(ts)
#     res = m.strftime('%Y-%m-%dT%H:%M:%S')
#     return res
# # transfer the timestamp into the datetime
# for key, value in tqdm(ordered_dict.items()):
#     time_col = []
#     for t in value[:, 7]:
#         timestr = ts2dt(t)
#         time_col.append(timestr)
#
#     df = pd.DataFrame(value)
#     df[7] = time_col
#     ordered_dict[key] = df
#
# track_idx_len = len(ordered_dict)
# df = pd.DataFrame(ordered_dict, index=range(1, track_idx_len+1), columns=['ppdata'])
# df.to_csv('pd_database.csv')
# print(1)


