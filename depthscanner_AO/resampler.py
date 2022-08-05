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

#oldimage = Image.open("D:\OneDrive - PennO365\Research\EMLab\BayWatch\BayWatch\depthscanner\Test_Image.JPEG")
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
    #img_filepath = r"C:\Users\aaron\Downloads\test.bmp"

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
        
            #pal_src = "C:\Windows\System32\depthscanner\palette_src.bmp" ##GRASSHOPPER DOESN'T LIKE PIL TO OPEN BMP
            #fo = open(pal_src)
            #print("Name of the file: ", fo.name)
            #print("Closed or not : ", fo.closed)
            # Close opend file
            #fo.close()
            #np_src = Image.open("C:\Windows\System32\depthscanner\palette_src.bmp")
            #pal_array = np.asarray(np_src)
        
            # read image using cv2 as numpy array
            #pal_img = cv.imread(pal_src) 

            # convert the color (necessary)
            #pal_img = cv.cvtColor(pal_img, cv.COLOR_BGR2RGB) 

        # Make an array to build a bigger image to array 
        pal_array = [
            #217, 184, 114,    #1 goldenrod
            226, 226, 115,      #dirty pastel yellow
            #251,229,166,    #2 yellow
            82, 19, 0,        #3 red
            255, 170, 170,      #3 alt pink
            #255, 185, 178,   #3 alt pink
            54, 31, 29,       #4 scarlet
            #170, 85, 0,     #"rusty red"
            #200, 0, 0,      #rusty red alt
            160, 98, 84,     #rusty red alt 2
            #0, 0, 0,          #5 black
            66, 66, 66,       #6 darker grey
            135, 135, 135,    #7 mid grey
            210, 210, 210,    #8 light grey
            #255,255,255,    #9 white
        ]

            #alternative colors
            #255, 170, 170 pink or 255, 185, 178
            #255, 255, 170 yellow
            #170, 85, 0 "rusty red"
            #85, 0, 0 scarlet


        #pallete = np.reshape(pal_array,(3,3))

        # create a new image and place the palette in there
        pal_img = Image.new('P',(9,9))
        pal_img.putpalette(pal_array * 9)
        #pal_img.show()
        #src = Image.fromarray(pal_array).convert('P')
        #src = src.resize((27,27))
        
        #src.show()
        
        color_image = Image.fromarray(color_image)
        print("newarray")
        newimage = color_image.quantize(palette=pal_img, dither=0)
        print("quantized")

        #src.show()
        #color_image.show()
        #newimage.show()

        #downsample = newimage.resize((int(w/2),int(h/2)))

        #Bring the image back to size and into cv2 format to save
        #upsample = downsample.resize((w,h), PIL.Image.Resampling.BICUBIC )
        upsample = newimage.convert('RGB')
        upsample = np.asarray(upsample)
        upsample = cv.cvtColor(upsample, cv.COLOR_RGB2BGR)
    finally:
        print("whoopsie")
    #upsample.save("EMtest_up.png")       

    print("exported")

    #color_image.show()
    #newimage.show()
    #downsample.show()
    #upsample.show()

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