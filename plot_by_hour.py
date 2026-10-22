import requests
import json
import pandas as pd
import time
import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from scipy.cluster.hierarchy import linkage
from  scipy.cluster.hierarchy import fcluster

def extract_data_by_hours(data, device_num, start_hour, end_hour, parameter):
    column_name = f'{device_num}_{parameter}'
    columns_to_select = ['timestamp', column_name]
    data_for_device = data[columns_to_select]
    data_for_device = data_for_device[data_for_device['timestamp'].dt.hour >= start_hour]
    data_for_device = data_for_device[data_for_device['timestamp'].dt.hour < end_hour]
    return data_for_device

def extract_data(data, device_num, start_date, end_date, parameter):
    column_name = f'{device_num}_{parameter}'
    columns_to_select = ['timestamp', column_name]
    data_for_device = data[columns_to_select]
    data_for_device = data_for_device[data_for_device['UTC time'] >= start_date]
    data_for_device = data_for_device[data_for_device['UTC time'] <= end_date]
    return data_for_device

def fetch_data_for_locations_by_hours(start_hour, end_hour, parameter):
    locations = pd.read_csv("data/location_const.csv")
    locations = locations[['id', 'latitude', 'longitude', 'city', 'street', 'number', 'elevation']]
    locations = locations.set_index('id', drop=False)
    airly_data_2018 = pd.read_csv("data/data.csv")
    airly_data_2018['timestamp'] = pd.to_datetime(airly_data_2018['UTC time'])

    for loc in locations['id']:
        try:
            data = extract_data_by_hours(airly_data_2018, loc, start_hour, end_hour, parameter)
            change = data[f'{loc}_{parameter}']
            locations.loc[loc, 'values'] = ','.join(list(map(lambda x: str(x), change)))
        except KeyError:
            locations = locations.drop(index=loc)
            continue

    return locations


def get_avg_data_for_triangle(triangle, values):
    values_for_triangle = list(np.array(values)[triangle])
    values_for_triangle = [x.split(',') for x in values_for_triangle]
    return [np.nanmean(np.array(x).astype(np.float))for x in list(zip(*values_for_triangle))]

def prepare_points_triangles_avg(locations):
    points = [[float(x), float(y)] for x, y in zip(list(locations['longitude']), list(locations['latitude']))]
    points = np.array(points)
    tri = Delaunay(points)
    triangles = tri.simplices

    values = list(locations['values'])
    avg = []
    for triangle in triangles:
        avg.append(get_avg_data_for_triangle(triangle, values))
    return points, triangles, avg

def get_correlation(avg):
    corr_matrix = np.nan_to_num(np.corrcoef(avg))
    dissimilarity = 1 - np.abs(corr_matrix)
    hierarchy = linkage(dissimilarity, method='average')
    labels = fcluster(hierarchy, 0.5, criterion='distance')
    return labels

def plot_points(points, triangles, labels, title, path):
    x = points[:, 0]
    y = points[:, 1]
    triang = mtri.Triangulation(x, y, triangles)

    fig1, ax1 = plt.subplots()
    ax1.set_aspect('equal')
    tpc = ax1.tripcolor(triang, facecolors=labels, edgecolors='k', vmin=0, vmax=40)
    fig1.colorbar(tpc)
    plt.title(title)
    # plt.show()
    plt.savefig(path)


parameter = 'pm1'

for start_hour, end_hour in zip(range(0,23), range(1,24)):
    locations = fetch_data_for_locations_by_hours(start_hour, end_hour, parameter)
    points, triangles, avg = prepare_points_triangles_avg(locations)
    labels = np.array([ np.mean(row)  for row in np.nan_to_num(avg)])
    title = f'{parameter} Mean at {start_hour}-{end_hour} hour (October-December 2018)'
    path = f'plots/{parameter}_mean_by_hour/{parameter}_by_hour_{start_hour}_{end_hour}_mean.png'
    plot_points(points, triangles, labels, title, path)

# locations = fetch_data_for_locations_by_hours(start_hour, end_hour, parameter)
# points, triangles, avg = prepare_points_triangles_avg(locations)
# labels = get_correlation(avg) #np.array([ np.mean(row)  for row in np.nan_to_num(avg)])
# title = f'{parameter} Mean (October/November 2018)'
# path = f'plots/{parameter}_by_hour_{start_hour}_{end_hour}_mean.png'
# plot_points(points, triangles, labels, title, path)