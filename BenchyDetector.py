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
    Returns amount of benchys in an image
    Saves the image with current time as name
    """
    directory = "HopefullyBenchys"  #where we save dem benchys
    benchy = BenchyData(image=cv2.imread(image_path, color=cv2.COLOR_BGR2GRAY))

    #Delete image after it is read
    remove(image_path)

    detections = benchy.cascade.detectMultiScale(
        image=benchy.image,
        minSize=(500, 500),
        minNeighbors=10
    )

    # Draw a rectangle around the benchys
    for (x, y, w, h) in detections:
        cv2.rectangle(benchy.image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    filename = datetime.now.strftime("%y%m%d%H%M%S")
    cv2.imwrite(f"{directory}/{filename}", benchy.image)
    cv2.waitKey(0)

    #Turn into cv2 image
    #Generate the amount of benchys in the image
    #Return the amount of benchys

    return len(detections)
