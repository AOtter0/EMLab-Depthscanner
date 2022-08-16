import PIL
from PIL import Image
from PIL import ImagePalette as ip
import cv2 as cv
import numpy as np
import os
import pathlib 
from pathlib import Path
import time



print("Hello, EMLab.")

#img_filepath = Image.open("D:\OneDrive - PennO365\Research\EMLab\BayWatch\BayWatch\depthscanner\Test_Image.JPEG")
## Perform the resampling
def resample(img_filepath):

    #wait for any files to finish saving
    #naptime = 3
    #while naptime > 0:
    #    print(naptime)
    #    time.sleep(1)
        #countdown
    #    naptime -= 1
    #print("Ready to go")

    print("resample start")

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

        # Make an array to build a bigger image to array 
        pal_array = [
            226, 226, 115,      #dirty pastel yellow
            82, 19, 0,        # red
            255, 170, 170,      # alt pink
            54, 31, 29,       # scarlet
            160, 98, 84,     #rusty red alt 2
            66, 66, 66,       # darker grey
            135, 135, 135,    # mid grey
            210, 210, 210,    # light grey
        ]

            #alternative colors
            #255, 170, 170 pink or 255, 185, 178
            #255, 255, 170 yellow
            #170, 85, 0 "rusty red"
            #85, 0, 0 scarlet
            ##255,255,255,    #9 white
            #217, 184, 114,    #1 goldenrod
            #251,229,166,    #2 yellow
            #255, 185, 178,   #3 alt pink
            #170, 85, 0,     #"rusty red"
            #200, 0, 0,      #rusty red alt
            #0, 0, 0,          #5 black


        #pallete = np.reshape(pal_array,(3,3))

        # Create a new image and place the palette in there
        pal_img = Image.new('P',(9,9))
        pal_img.putpalette(pal_array * 9)

        ##Turn the image back into an array to be processed.        
        color_image = Image.fromarray(color_image)
        print("newarray")
        newimage = color_image.quantize(palette=pal_img, dither=0)
        print("quantized")

        ##Enable this code to show the processed images. Use this for 'color debugging.'
        #src.show()
        #src.show()
        #color_image.show()
        #newimage.show()

        #Bring the image back to size and into cv2 format to save
        upsample = newimage.convert('RGB')
        upsample = np.asarray(upsample)
        upsample = cv.cvtColor(upsample, cv.COLOR_RGB2BGR)
    finally:
        print("Try this!")
    #upsample.save("EMtest_up.png")       

    print("exported")

    #save the finished image for FF to bring into GH
    head = os.path.splitext(img_filepath)[0]
    tail = os.path.splitext(img_filepath)[-1]

    save_path = head+"_new"+tail
    #save_path2 = head+"_new"
    complete = cv.imwrite(save_path, upsample)
    #complete = upsample.save()

    return save_path

if __name__ == "__main__":
    resample("")