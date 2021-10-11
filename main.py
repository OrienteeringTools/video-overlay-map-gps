import os, sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
from datetime import datetime
import rioxarray as rxr #pip install rioxarray
import cv2 #pip install opencv-python

from georef_img import georef_img

class orienteeringRaceOverlay():
    def __init__(self, gpsFile='example-data/activity_1.gpx'):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.gpsFile = gpsFile
        self.mapFile = 'example-data/map1.tif'
        self.worldFile = 'example-data/map1.tfw'
        self.kmlFile = 'example-data/map2.kml'
        self.videoFile = ''
        self.timeAveragingWindow = 10 #in seconds

    def readMapfile(self, kml=False):
        if kml:
            return georef_img.from_kml(self.kmlFile)
        else:
            return georef_img.from_world_file(self.worldFile, self.mapFile)

    def readGPSfile(self):
        data = open(self.gpsFile).read()
        lat = np.array(re.findall(r'lat="([^"]+)',data),dtype=float)
        lon = np.array(re.findall(r'lon="([^"]+)',data),dtype=float)
        coordinates = np.array(list(zip(lat,lon))).astype(float)
        dtSeries = pd.Index.to_series(pd.to_datetime(re.findall(r'<time>([^\<]+)',data))).diff(periods=1)
        dt = np.diff((dtSeries.index.values - dtSeries.index.values.astype('datetime64[D]'))/np.timedelta64(1,'s'))
        return coordinates, dt

    def readVideo(self):
        cap = cv2.VideoCapture(self.videoFile)

    def calcHeading(self, coordinates, dt):
        N = round(self.timeAveragingWindow/np.mean(dt))
        dx = pd.Series(np.diff(coordinates[:,1])).rolling(window=N).mean().iloc[N-1:].values
        dy = pd.Series(np.diff(coordinates[:,0])).rolling(window=N).mean().iloc[N-1:].values
        heading = np.arctan2(dy,dx)
        return heading

if __name__ == '__main__':
    # map = orienteeringRaceOverlay().readMapfile()
    # coordinates, dt = orienteeringRaceOverlay().readGPSfile()
    # img = map.get_img_with_gps_line(coordinates)
    # cv2.imwrite("out1.png", img)

    map2 = orienteeringRaceOverlay().readMapfile(kml=True)
    coordinates2, dt2 = orienteeringRaceOverlay(gpsFile='example-data/activity_2.gpx').readGPSfile()
    img2 = map2.get_img_with_gps_line(coordinates2)
    cv2.imwrite("out2.png", img2)

    #orienteeringRaceOverlay().readVideo()
    #heading = orienteeringRaceOverlay().calcHeading(coordinates, dt)
    #orienteeringRaceOverlay().plotTrack(coordinates, heading)