import cv2
import sys

# Get user supplied values
imagePath = "benchydetection/testImages/test6.jpg"
cascPath = "benchydetection/data/cascade.xml"

# Create the haar cascade
faceCascade = cv2.CascadeClassifier(cascPath)

# Read the image
image = cv2.imread(imagePath)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#image = cv2.resize(image, (600, 400))

# Detect faces in the image
faces = faceCascade.detectMultiScale(
    image=gray,
    minSize=(500,500),
    minNeighbors=10
)

#rects = faces[0]
#neighbors = faces[1]
#weights = faces[2]

print("Found {0} faces!".format(len(faces)))

'''
for i in weights:
    print(i)
'''


# Draw a rectangle around the faces
for (x, y, w, h) in faces:
    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

cv2.imwrite("result.jpg", image)
cv2.waitKey(0)


#pictures to train with

#https://imgur.com/gallery/YokSF
#https://github.com/boyEstrogen/Anime-Girls-Holding-Programming-Books