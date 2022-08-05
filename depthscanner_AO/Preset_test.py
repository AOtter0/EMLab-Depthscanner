import pyrealsense2 as rs
import numpy as np
from PIL import Image

# Declare pointcloud object, for calculating pointclouds and texture mappings
pc = rs.pointcloud()
# We want the points object to be persistent so we can display the last cloud when a frame drops
points = rs.points()

# Create pipeline and config stream_align the streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30) 
config.enable_stream(rs.stream.color, 1280, 720, rs.format.rgb8, 30)

profile = config.resolve(pipeline)
#pipeline.start(config)

# Define HIGH ACCURACY preset
pipe_profile = pipeline.start(config)

depth_sensor = pipe_profile.get_device().first_depth_sensor()

preset_range = depth_sensor.get_option_range(rs.option.visual_preset)
current_preset = depth_sensor.get_option(rs.option.visual_preset)
print('preset range:'+str(preset_range)+str(current_preset))

for i in range(int(preset_range.max)):
    visulpreset = depth_sensor.get_option_value_description(rs.option.visual_preset,i)
    print('%02d: %s'%(i,visulpreset))
    if visulpreset == "High Accuracy":
        depth_sensor.set_option(rs.option.visual_preset, i)
        current_preset = depth_sensor.get_option(rs.option.visual_preset)
        print('current preset:'+str(current_preset))


# Create an align object to match both resolutions
# The "align_to" is the stream type to which other stream will be aligned.
align_to = rs.stream.depth
align = rs.align(align_to)

# Get frames
frames = pipeline.wait_for_frames() # Wait until a frame is available

# Align the color frame to depth frame
aligned_frames = align.process(frames)
depth_frame = aligned_frames.get_depth_frame()
color_frame = aligned_frames.get_color_frame()

# Ensure that both frames are valid
if depth_frame and color_frame:

    # Turn depth frame into an pointcloud (with x, y, z values) and store it in a numpy array
    point_cloud = pc.calculate(depth_frame)

    # Turn the frames into numpy arrays
    depth = np.array(point_cloud.get_vertices(3)) # shape: resolution * 3 -> e.g. 1024*768 * (x,y,z)
    color = np.array(color_frame.get_data()) # shape: aligned resolution * 3 -> e.g. 1024*768 * (r,g,b)

    # Save arrays for future uses
    np.save('numpy_depth.npy', depth)
    np.save("numpy_color.npy", color)

    # Save image
    im = Image.fromarray(color)
    im.save("depth_image.jpg")

pipeline.stop()