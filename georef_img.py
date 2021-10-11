import numpy as np
import cv2 #pip install opencv-python
import xml.etree.ElementTree as ET
from pyproj import Proj
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info


class georef_img():
    def __init__(self, img_file, up_left_cord_x, up_left_cord_y, x_scale, y_scale = None, x_skew = 0, y_skew = 0, proj = None) -> None:
        self.img_file = img_file
        self.proj = proj
        if y_scale is None:
            y_scale = -x_scale
        self.pix2coord_matrix = np.matrix([[x_scale, x_skew, up_left_cord_x], 
                                           [y_skew, y_scale, up_left_cord_y]])
        self.coord2pix_matrix = np.matrix([[y_scale, -x_skew, x_skew * up_left_cord_y - y_scale * up_left_cord_x], 
                                           [-y_skew, x_scale, y_skew * up_left_cord_x - x_scale * up_left_cord_y]]) / (x_scale * y_scale - x_skew * y_skew)
        self.scale = np.sqrt(np.sqrt(x_scale**2 + y_skew**2) * np.sqrt(y_scale**2 + x_skew**2))

    def __repr__(self):
         return f"georef_img(file: {self.img_file},\n\tpix2coord_matrix: {self.pix2coord_matrix},\n\tcoord2pix_matrix: {self.coord2pix_matrix})"
    
    def pix2coord(self, x, y):
        res = self.pix2coord_matrix * np.array([x ,y , 1])
        return (res[0], res[1])
    
    def coord2pix(self, lat, lon):
        if self.proj is None:
            self.proj = Proj(int(query_utm_crs_info(
                datum_name="WGS 84",
                area_of_interest=AreaOfInterest(
                    west_lon_degree=lon,
                    south_lat_degree=lat,
                    east_lon_degree=lon,
                    north_lat_degree=lat,
                ),
            )[0].code))
        x,y = self.proj(lon,lat)
        res = self.coord2pix_matrix * np.matrix([x , y, 1]).T
        return (res[0,0], res[1,0]) 

    def get_img(self):
        return cv2.imread(self.img_file)

    def from_kml(file):
        xmlfile = ET.parse(file)
        lat_lon_box = xmlfile.find('.//{*}LatLonBox')
        north = float(lat_lon_box.find("./{*}north").text)
        south = float(lat_lon_box.find("./{*}south").text)
        east  = float(lat_lon_box.find('./{*}east').text)
        west  = float(lat_lon_box.find('./{*}west').text)
        rot   = float(lat_lon_box.find('./{*}rotation').text)

        img_href = xmlfile.find('.//{*}Icon/{*}href').text
        img_file = "example-data/" + img_href               # TODO: Make relative paths work
        (width, height) = cv2.imread(img_file).shape[1::-1]
        proj = Proj(int(query_utm_crs_info(
            datum_name="WGS 84",
            area_of_interest=AreaOfInterest(
                west_lon_degree=west,
                south_lat_degree=south,
                east_lon_degree=east,
                north_lat_degree=north,
            ),
        )[0].code))
        # Realworld bounding box (relative to current UTM zone)
        x_min, y_min = proj(west, north)
        x_max, y_max = proj(east, south)
        real_width = x_max - x_min
        real_height = y_max - y_min
        bb_center = np.array(((x_min + x_max)/2, (y_min + y_max)/2))
        # Image rotation around center
        image_rotation = np.radians(rot)
        sin = np.sin(image_rotation)
        cos = np.cos(image_rotation)
        # Size of image bounding box after rotation
        rot_width = abs(sin)*height + abs(cos)*width
        rot_height = abs(sin)*width + abs(cos)*height
        # Scale and skew for x and y (for transforming pixel to real world point)
        x_scale = cos * real_width / rot_width
        y_scale = cos * real_height / rot_height
        x_skew = sin * real_width / rot_width
        y_skew = sin * real_height / rot_height
        # Real world point for up-left corner of image
        center_to_up_left = np.array((-width/2, -height/2))
        rotation_matrix = np.array(((cos, sin), (-sin, cos)))
        scale_skew = np.array(((x_scale, x_skew), (y_skew, y_scale)))
        up_left = scale_skew.dot(rotation_matrix.dot(center_to_up_left)) + bb_center
        # Finally make georef_img object
        return georef_img(img_file, up_left[0], up_left[1], x_scale, y_scale, x_skew, y_skew, proj=proj)
    
    def from_world_file(world_file, img_file):
        with open(world_file, 'r') as f:
            lines = f.readlines()
            assert(len(lines) >= 6)
            return georef_img(img_file, float(lines[4]), float(lines[5]), float(lines[0]), float(lines[3]), float(lines[2]), float(lines[1]))

    def get_img_with_gps_line(self, coordinates, line_thickness=5):
        img = self.get_img()
        last_point = (0,0)
        first = True
        for coord in coordinates:
            x,y = self.coord2pix(coord[0], coord[1])
            point = (int(x), int(y))
            if first:
                first = False
            else:
                cv2.line(img, last_point, point, (0,0,255), thickness=int(line_thickness*self.scale))
            last_point = point
        return img
