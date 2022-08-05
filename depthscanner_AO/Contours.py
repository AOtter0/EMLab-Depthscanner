## Developed by Aaron O'Neill for the Univerity of Pennsylvania's Environmental Modeling Lab
# part of the Weitzman School of Design and the Ian L. McHarg Center for Urbanism and Ecology
## Based on the -depthscanner- code originally published by Ilmar Hurkxkens @ilmihur

# First import the libraries
import compas
import pyrealsense2 as rs
import numpy as np
import PIL
import cv2 as cv
import json
from PIL import Image
from PIL import ImagePalette as ip

from timeit import default_timer as timer


# Start the scanner here
# Declare RealSense pipeline, encapsulating the actual device and sensors

_pipe = None
_pipe = rs.pipeline()
cfg = rs.config()

def get_pipe():
    global _pipe
    return _pipe


## Find the Device
selected_devices = []                     # Store connected device(s)

for d in rs.context().devices:
    selected_devices.append(d)
    print(d.get_info(rs.camera_info.name)+ " detected.")
if not selected_devices:
    print("No RealSense device is connected!")



## Define PointCloud Scan - Returns depth at all points returned by scan
# Plus Temporal filters
def pcScan(): 

    # Declare pointcloud object, for calculating pointclouds and texture mappings
    pc = rs.pointcloud()
    
    # We want the points object to be persistent so we can display the last cloud when a frame drops
    points = rs.points()
  
    # Create pipeline and config stream_align the streams #test between 848x480 and 1280x720
    w = 1280
    h = 720
    cfg.enable_stream(rs.stream.color, w, h, rs.format.rgb8, 15)
    profile = cfg.resolve(_pipe)


    ## Establish HIGH ACCURACY preset
    # create pipeline
    pipe_profile = _pipe.start(cfg)
    
    try:
         for _ in range(60):                                       
            _pipe.wait_for_frames()

        color_image = np.array(color_frame.get_data())

        ## Calculate pointcloud and add color to the points
        pts = pc.calculate(depth_frame)
        print('Points acquired..')
        pc.map_to(color_frame)
        print('Color mapped')

        ## to build of pointcloud, we need to deconstruct then reconstruct the arrays - get_vert 2 required to have lists instead of void dtype - necessary to get into rhino quicker
        pts = np.asanyarray(pts.get_vertices(2))


        ## RESAMPLE THE CAPTURED IMAGE TO A SET PHOTOMAP
        r, g, b = cv.split(color_image)
        color_image = cv.merge((r, g, b))
        print("image processed")
        
        src = Image.open("C:\Windows\System32\depthscanner\palette_src.bmp")
        color_image = Image.fromarray(color_image)
        print("newarray")
        newimage = color_image.quantize(palette=src, dither=1)
        print("quantized")
