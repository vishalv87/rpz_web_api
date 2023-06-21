import numpy as np
from flask import Flask, request, jsonify, render_template, send_file, Response
import pickle
import random
import logging
import inspect
import requests
import argparse
import jsonpickle
import cv2

import tensorflow as tf
from tensorflow.keras import models
import numpy as np

from generate_chessboards import generate_random_chessboards, generate_random_chessboard
from generate_tiles import generate_tiles_from_random_chessboard
from pgn_from_2fens import fendiff

from recognize import perform_recognition

from constants import TILES_DIR, NN_MODEL_PATH, FEN_CHARS, USE_GRAYSCALE, DETECT_CORNERS


app = Flask(__name__)
model = models.load_model(NN_MODEL_PATH)

logging.basicConfig(filename="api.log", level=logging.DEBUG)


@app.route("/api-caller")
def api_caller():
    try:
        url = "http://127.0.0.1:8002/generate-tiles-from-random-chessboard"

        response = requests.get(url)

        if response.status_code == 200:
            with open("downloaded_file.zip", "wb") as file:
                file.write(response.content)
            print("file downloaded successfully")
        else:
            print("error occured!")

        return "dummy"
    except Exception as e:
        print(str(inspect.currentframe().f_code.co_name), str(e))


@app.route("/recognize")
def recognize_chessboard():
    chessboard_image_path = "./chessboard.png"
    model = models.load_model(NN_MODEL_PATH)

    mock_args = argparse.Namespace()
    mock_args.quiet = False
    mock_args.debug = False
    mock_args.image_path = chessboard_image_path

    print("recognizer")
    print(mock_args)

    response = perform_recognition(mock_args, chessboard_image_path)
    return response


@app.route("/generate-tiles-from-random-chessboard")
def generate_tiles_from_chessboards():
    try:
        zip_file__path = generate_tiles_from_random_chessboard()
        mime_type = "application/zip"

        # Provide a filename for the downloaded file
        filename = zip_file__path.split("/")[-1]

        return send_file(
            zip_file__path,
            mimetype=mime_type,
            as_attachment=True,
        )
    except Exception as e:
        print(str(inspect.currentframe().f_code.co_name), str(e))


@app.route("/generate-chessboard")
def generate_chessboard():
    try:
        filepath = generate_random_chessboard("http://www.fen-to-image.com/image/32/{}")
        # return "dummy header"
        return send_file(filepath, mimetype="image/png")
    except Exception as e:
        print(str(inspect.currentframe().f_code.co_name), str(e))


@app.route("/generate-chessboards")
def generate_chessboards():
    try:
        random_integer = random.randint(500, 550)
        generate_random_chessboards(
            random_integer, "http://www.fen-to-image.com/image/32/{}"
        )
        return "dummy return"
    except Exception as e:
        print(str(inspect.currentframe().f_code.co_name), str(e))


# this api takes input as request and starts performing the recognition pipeline
@app.route("/api/test", methods=["POST"])
def test():
    try:
        r = request
        # convert string of image data to uint8
        nparr = np.fromstring(r.data, np.uint8)
        # decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        img_file_name = "downloaded.png"
        downloaded_file_path = f"/home/vishalv/code/rpz/src/rpz-web-api/{img_file_name}"
        cv2.imwrite(downloaded_file_path, img)

        downloaded_img = cv2.imread(downloaded_file_path)

        # do some fancy processing here....
        # chessboard_image_path = "./chessboard.png"
        model = models.load_model(NN_MODEL_PATH)

        mock_args = argparse.Namespace()
        mock_args.quiet = False
        mock_args.debug = False
        mock_args.image_path = downloaded_file_path

        print("recognizer")
        print(mock_args)

        response = perform_recognition(mock_args, downloaded_file_path)
        print(response)

        # build a response dict to send back to client
        response = {
            "message": "image received. size={}x{}".format(img.shape[1], img.shape[0]),
            "result": response,
        }
        # encode response using jsonpickle
        response_pickled = jsonpickle.encode(response)

        return Response(
            response=response_pickled, status=200, mimetype="application/json"
        )
    except Exception as e:
        return Response(response=str(e), status=500, mimetype="text/plain")


@app.route("/pgn-from-2fens")
def get_pgn_from_fens():
    move = fendiff(
        "8/3k1P1q/8/8/8/4n3/8/2K5 w - - 0 1", "5N2/3k3q/8/8/8/4n3/8/2K5 b - - 0 1"
    )
    return Response(str(move), status=200, mimetype="text/plain")


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=8002)
