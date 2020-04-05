import cv2
import numpy as np
import os

def store_raw_images():
    picNumber = 2940
    victimName = 'benchydetection/subredditstuff/roastme'
    resultName = 'benchydetection/neg'
    #Make directory if it doesnt exist
    if not os.path.exists(resultName):
        os.makedirs(resultName)
    
    #Iterate through the files
    for picture in os.listdir(victimName):
        #Get filename
        filename = os.fsdecode(picture)
        print(filename)
        print("Picture number "+ str(picNumber))
        #Open and make it greyscale
        img = cv2.imread(victimName + '/' + filename, cv2.IMREAD_GRAYSCALE)
        #resize
        resized_image = cv2.resize(img, (600, 400))
        #Write
        cv2.imwrite(resultName+'/'+str(picNumber)+".png", resized_image)
        picNumber += 1

def mirrorImages():
    """
    Mirrors all images in a folder and saves in new folder
    """
    picNumber = 557
    victimName = 'pos'
    resultName = 'flippedPos'

    if not os.path.exists(resultName):
        os.makedirs(resultName)

    for picture in os.listdir(victimName):
        filename = os.fsdecode(picture)
        print(filename)

        img = cv2.imread(victimName + '/' + filename)
        flipped = cv2.flip(img, 1)
        cv2.imwrite(resultName + '/' + str(picNumber) + '.jpg', flipped)
        picNumber += 1

def createbg():
    """
    Creates bg.txt for negatives
    """
    numberofPics = 2142

    with open('bg.txt', 'w') as file:
        for i in range(numberofPics):
            file.write("neg/" + str(i) + '.png\n')

def createinfo():
    """
    Creates info.dat for positives
    """
    numberofPics = 1112

    with open('info.dat', 'w') as file:
        for i in range(numberofPics):
            file.write("pos/" + str(i) + ".jpg 1 0 0 200 200\n")

#createinfo()
#createbg()
#mirrorImages()
store_raw_images()