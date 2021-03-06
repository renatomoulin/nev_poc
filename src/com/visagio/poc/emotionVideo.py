from __future__ import print_function

import time
import requests
import cv2
import operator
import numpy as np



# Import library to display results
import matplotlib.pyplot as plt

# Variables
_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
_key = '1d41ff43c73e4102af4c96a621e2c56b'
_maxNumRetries = 10


def processRequest(json, data, headers, params):
    """
    Helper function to process the request to Project Oxford

    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """

    retries = 0
    result = None

    while True:

        response = requests.request('post', _url, json=json, data=data, headers=headers, params=params)

        if response.status_code == 429:

            print("Message: %s" % (response.json()['error']['message']))

            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()['error']['message']))

        break

    return result


def renderResultOnImage(result, img):
    """Display the obtained results onto the input image"""

    for currFace in result:
        faceRectangle = currFace['faceRectangle']
        cv2.rectangle(img, (faceRectangle['left'], faceRectangle['top']),
                      (faceRectangle['left'] + faceRectangle['width'], faceRectangle['top'] + faceRectangle['height']),
                      color=(255, 0, 0), thickness=5)

    for currFace in result:

        if 'faceAttributes' in currFace:
            faceRectangle = currFace['faceRectangle']
            faceAttributes = currFace['faceAttributes']
            currEmotion = max(faceAttributes['emotion'].items(), key=operator.itemgetter(1))[0]
            gender = faceAttributes['gender']
            age = faceAttributes['age']

            textToWrite = "%s" % (currEmotion)
            cv2.putText(img, textToWrite, (faceRectangle['left'], faceRectangle['top'] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

            textToWrite = "%s" % (gender)
            cv2.putText(img, textToWrite, (faceRectangle['left'], faceRectangle['top'] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

            textToWrite = "%s" % (age)
            cv2.putText(img, textToWrite, (faceRectangle['left'], faceRectangle['top'] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)


# Load raw image file into memory
headers = dict()
headers['Ocp-Apim-Subscription-Key'] = _key
headers['Content-Type'] = 'application/octet-stream'
params = dict()
params['returnFaceId'] = 'true'
params['returnFaceLandmarks'] = 'false'
params['returnFaceAttributes'] = 'gender,age,emotion'
pathToFileInDisk = r'C:\temp\Victor.mp4'
vidcap = cv2.VideoCapture(pathToFileInDisk)
success,image = vidcap.read()
count = 0
startFrame = 233
endFrame = 233
success = True
while success:
  success,image = vidcap.read()

  if count >= startFrame and count<=endFrame:
    pathToOutputFile = ("c:/temp/frames_in/frame%d.jpg" % count)
    cv2.imwrite(pathToOutputFile, image)  # save frame as JPEG file
    with open(pathToOutputFile, 'rb') as f:
      data = f.read()

    json = None
    result = processRequest(json, data, headers, params)

    if result is not None:
          # Load the original image from disk
        data8uint = np.fromstring(data, np.uint8)  # Convert string to an unsigned int array
        img = cv2.cvtColor(cv2.imdecode(data8uint, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

        renderResultOnImage(result, img)
        cv2.imwrite("c:/temp/frames_out/frame%d.jpg" % count, img)  # save frame as JPEG file

        # plt.imshow(img)
        # plt.colorbar()
        # plt.title("frame%d.jpg" % count)
        # plt.show()

  count += 1