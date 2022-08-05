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
    cfg.enable_stream(rs.stream.depth, w, h, rs.format.z16, 15) 
    cfg.enable_stream(rs.stream.color, w, h, rs.format.rgb8, 15)
    profile = cfg.resolve(_pipe)


    ## Establish HIGH ACCURACY preset
    # create pipeline
    pipe_profile = _pipe.start(cfg)

    #define the depth sensor
    depth_sensor = pipe_profile.get_device().first_depth_sensor()

    #what are the preset options?
    preset_range = depth_sensor.get_option_range(rs.option.visual_preset)
    current_preset = depth_sensor.get_option(rs.option.visual_preset)
    #print('preset range: '+str(preset_range)+str(current_preset))

    # set the visual reset to high accuracy
    #for i in range(int(preset_range.max)):
    #    visulpreset = depth_sensor.get_option_value_description(rs.option.visual_preset,i)
    #    print('%02d: %s'%(i,visulpreset))
    depth_sensor.set_option(rs.option.visual_preset, 5)
    current_preset = depth_sensor.get_option(rs.option.visual_preset)
    print('current preset: '+str(current_preset))    


    ## Set Advanced mode features
    advnc_mode = rs.rs400_advanced_mode(profile.get_device())
    DS5_product_ids = ["0AD1", "0AD2", "0AD3", "0AD4", "0AD5", "0AF6", "0AFE", "0AFF", "0B00", "0B01", "0B03", "0B07", "0B3A", "0B5C"]

    def find_device_that_supports_advanced_mode() :
        ctx = rs.context()
        ds5_dev = rs.device()
        devices = ctx.query_devices();
        for dev in devices:
            if dev.supports(rs.camera_info.product_id) and str(dev.get_info(rs.camera_info.product_id)) in DS5_product_ids:
                if dev.supports(rs.camera_info.name):
                    print("Found device that supports advanced mode:", dev.get_info(rs.camera_info.name))
                return dev
        raise Exception("No D400 product line device that supports advanced mode was found")

    try:
        dev = find_device_that_supports_advanced_mode()
        advnc_mode = rs.rs400_advanced_mode(dev)
        print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")

        # Loop until we successfully enable advanced mode
        while not advnc_mode.is_enabled():
            print("Trying to enable advanced mode...")
            advnc_mode.toggle_advanced_mode(True)
            # At this point the device will disconnect and re-connect.
            print("Sleeping for 5 seconds...")
            time.sleep(5)
            # The 'dev' object will become invalid and we need to initialize it again
            dev = find_device_that_supports_advanced_mode()
            advnc_mode = rs.rs400_advanced_mode(dev)
            print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")
            
    except Exception as e:
        print(e)
        pass

    ## AMP FACTOR TO 0.18 FOR REFINED VISUALIZATION
    #advnc_mode.get_amp_factor()
    #print(advnc_mode.get_amp_factor())
    #factor = rs.STAFactor()
    #factor.a_factor = 0.18
    #advnc_mode.set_amp_factor(factor)
    #print(advnc_mode.get_amp_factor())

    ## Change depth table and set range of vision
    #depth_table_units = advnc_mode.get_depth_table()
    #depth_units = rs.STDepthTableControl()
    #depth_units.depthClampMax = 4500
    #depth_units.depthUnits = 500
    #advnc_mode.set_depth_table(depth_units)
    #print(advnc_mode.get_depth_table())

    ## Define increase laser and autoexposure set value to push more power to laser
    #ae_ctrl = advnc_mode.get_ae_control()
    #ae_ctrl.meanIntensitySetPoint = 1500
    #advnc_mode.set_ae_control(ae_ctrl)
    #print(advnc_mode.get_ae_control())
    #laser_pwr = depth_sensor.get_option(rs.option.laser_power)
    #print("laser power = ", laser_pwr)
    #laser_range = depth_sensor.get_option_range(rs.option.laser_power)
    #print("laser power range = " , laser_range.min , "~", laser_range.max)
    #set_laser = 300
    #depth_sensor.set_option(rs.option.laser_power, set_laser)
    #print(laser_pwr)


    ## OR we can load a json file
    jfile = open(r"C:\Windows\System32\depthscanner\test-MD-250D_D3T.json")
    as_json_object = json.load(jfile)
    print("jfile loaded")

    # For Python 2, the values in 'as_json_object' dict need to be converted from unicode object to utf-8
    if type(next(iter(as_json_object))) != str:
        as_json_object = {k.encode('utf-8'): v.encode("utf-8") for k, v in as_json_object.items()}
    # The C++ JSON parser requires double-quotes for the json object so we need
    # to replace the single quote of the pythonic json to double-quotes
    json_string = str(as_json_object).replace("'", '\"')
    advnc_mode.load_json(json_string)
    print("advanced settings set")

    #Defining frames and framesets for processing
    frameset = _pipe.wait_for_frames()
    color_frame = frameset.get_color_frame()
    depth_frame = frameset.get_depth_frame()


    try:
        ## Gather the Frames
        # Skip first frames to give syncer and auto-exposure time to adjust
        for _ in range(60):                                       
            _pipe.wait_for_frames()


        ##APPLY POST-PROCESSING FILTERS
        Decimation Filter
        decimation = rs.decimation_filter(2)
        decimated_depth = decimation.process(depth_frame)
        
        # Create a tuple of depth_frames for temporal filter 
        depth_frames = []
        for _ in range(10):                                       
            depth_frames.append(frameset.get_depth_frame())
        print("Depth frames captured")

        # define settings for temporal filter
        tempo_alpha = 0.10
        tempo_delta = 50
        tempo_pers = 1

        # process those frames together
        temporal = rs.temporal_filter(tempo_alpha, tempo_delta, tempo_pers)
        frame = []
        for x in range(10):
            frame = depth_frames[x]
            frame = decimation.process(frame)
            frame = temporal.process(frame)

        ## Redefine depth frame from the temporal filter
        depth_frame = frame

        ## Create an align object to match both resolutions
        # The "align_to" is the stream type to which other stream will be aligned.
        align_to = rs.stream.depth
        align = rs.align(align_to)

        ## Transition the frames to image arrays
        depth_image = np.asanyarray(depth_frame.get_data())
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

        #newimage.show()

        downsample = newimage.resize((int(w/2),int(h/2)))
        #downsample.save("EMTest_down.png")
        # need to figure out how to group the colors better...

        upsample = downsample.resize((w,h), PIL.Image.Resampling.BICUBIC )
        upsample = upsample.convert('RGB')
        #upsample.save("EMtest_up.png")       
        print("exported")
        color_image.show()
        upsample.show()


        ## Shape the image info to align with depth
        rgb = np.asarray(upsample).reshape(w * h,3)
        print("arrayed")
        print(pts.dtype)
       

        #nonzero in both
        ptx = []
        rgbx = []
        for x, y in zip(pts, rgb):
            if x[0] != 0:
                ptx.append(x)
                rgbx.append(y)
        print("ptx is:",type(ptx),"and ",len(ptx))
        print("rgbx is:",type(rgbx),"and ",len(rgbx))

        [list(x) for x in ptx]
        print("lists processed")
            
        ## flatten
            
        ## make r,g,b, lists - don't think we need these
        R = []
        G = []
        B = []
        for i in rgbx:
            R.append(i[0])
            G.append(i[1])
            B.append(i[2])
        print("rgb divided")

        rgbx = list(zip(R, G, B))
        print("rgbx reconstituted")
        print(ptx[2432])

        ## Dispatch 0 points from rgb

        print("NUMBER OF POINTS:")
        print(len(ptx))
         

        ##Zip the two lists together
        ptss = list(zip(ptx, rgbx))

        print(pts[0])
        #print(ptss[0])
        return ptss

        
       
    finally:
        _pipe.stop()
        print("pcScan Complete.")


if __name__ == "__main__":
    s = pcScan()
