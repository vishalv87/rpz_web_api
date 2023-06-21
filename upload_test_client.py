from __future__ import print_function
import requests
import json
import cv2

addr = "http://127.0.0.1:8002"
test_url = addr + "/api/test"

# prepare headers for http request
content_type = "image/png"
headers = {"content-type": content_type}

img = cv2.imread("./chessboard.png")
# encode image as jpeg
_, img_encoded = cv2.imencode(".png", img)
# send http request with image and receive response
response = requests.post(test_url, data=img_encoded.tostring(), headers=headers)
# decode response
print(json.loads(response.text))
