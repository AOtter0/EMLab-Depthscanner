import PIL
from PIL import Image
from PIL import ImagePalette as ip
import cv2 as cv
import numpy as np
import os
import pathlib 
from pathlib import Path
import time


print("engaged")

## Perform the resampling
def resample(img_filepath):

    print("Hello, EMLab")

    ##Place test filepath name below.
    #img_filepath = r"D:\OneDrive - PennO365\Research\EMLab\Assets\22-0817_1614.bmp"

    str_path = img_filepath
    path = Path(str_path)

    # read image using cv2 as numpy array ##MUST USE CV2 -GRASSHOPPER DOESN'T LIKE PIL TO OPEN BMP
    cv_img = cv.imread(img_filepath) 

    # convert the color (necessary)
    cv_img = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB) 

    # read as PIL image in RGB
    img = Image.fromarray(cv_img).convert('RGB')

    try:
        width, height = img.size
        print(width,height)

        w = width
        h = height

        color_image = np.asarray(img)

        r, g, b = cv.split(color_image)
        color_image = cv.merge((r, g, b))
        print("image processed")
       
            # read image using cv2 as numpy array
            #pal_img = cv.imread(pal_src) 

            # convert the color (necessary)
            #pal_img = cv.cvtColor(pal_img, cv.COLOR_BGR2RGB) 

        # Make an array to build a bigger image to array 
        pal_array = [
            145, 137, 115,      #dirty yellow
            146, 115, 115,      # alt pink
            60, 35, 35,         # scarlet
            45, 45, 45,        # darker grey
            73, 73, 73,        # dark grey
            102, 102, 102,     #mid grey 
            135, 135, 135,       # light grey
            175, 175, 175,        #v light grey
            235, 235, 235,         #nearly white
            178, 150, 150       #another red
        ]

        # create a new image and place the palette in there
        pal_img = Image.new('P',(9,9))
        pal_img.putpalette(pal_array * 9)
        #pal_img.show()
        
        color_image = Image.fromarray(color_image)
        print("newarray")
        newimage = color_image.quantize(palette=pal_img, dither=0)
        print("quantized")

        ##ENABLE THESE TO PREVIEW FILE
        #color_image.show()
        #newimage.show()

        #Bring the image back to size and into cv2 format to save
        upsample = newimage.convert('RGB')
        upsample = np.asarray(upsample)
        upsample = cv.cvtColor(upsample, cv.COLOR_RGB2BGR)
    finally:
        print("Preparing to save file.")
     
    #save the finished image for FF to bring into GH
    head = os.path.splitext(img_filepath)[0]
    tail = os.path.splitext(img_filepath)[-1]

    save_path = head+"_new"+tail
    #save_path2 = head+"_new"
    complete = cv.imwrite(save_path, upsample)

    print("exported")

    return save_path

if __name__ == "__main__":
    resample("")