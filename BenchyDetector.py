"""
Brandon Zupan

BenchyBot for 3DPrinters

Used for detecting if there is a benchy in an image
"""

from os import remove
from datetime import datetime
import cv2


class BenchyData():
    """
    Has all data for detecting a benchy
    """
    cascade_path = "cascade.xml"    #Path to the cascade

    def __init__(self, image):
        self.cascade = cv2.CascadeClassifier(self.cascade_path)     #Creates the cascade
        self.image = image

def is_benchy(image_path):
    """
    Returns amount of benchys in an image, and path to saved image
    Saves the image with current time as name
    """
    directory = "HopefullyBenchys"  #where we save dem benchys
    benchy = BenchyData(image=cv2.imread(image_path, cv2.COLOR_BGR2GRAY))



    detections = benchy.cascade.detectMultiScale(
        image=benchy.image,
        minSize=(200, 200),
        minNeighbors=10
    )

    #Save original image for comparison
    time = datetime.now()
    filename = directory + '/' + time.strftime("2019%m%d%H%M%S")

    cv2.imwrite(filename + '-og.png', benchy.image)

    # Draw a rectangle around the benchys
    for (x, y, w, h) in detections:
        cv2.rectangle(benchy.image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    print(filename)
    cv2.imwrite(filename + '.png', benchy.image)
    cv2.waitKey(0)

    #Delete image after it is read
    remove(image_path)

    return (len(detections), filename)

#yeet = is_benchy("temp/benchy1.png")
