from aiohttp import web
import aiohttp
import json
import requests
import argparse
import cairosvg

import tensorflow as tf
from tensorflow.keras import models
import numpy as np

from recognize import perform_recognition
from generate_tiles import generate_tiles_from_random_chessboard
from generate_chessboards import generate_random_chessboards, generate_random_chessboard
from server import Service

from constants import TILES_DIR, NN_MODEL_PATH, FEN_CHARS, USE_GRAYSCALE, DETECT_CORNERS

service = Service()


# board.svg?fen=5r1k/1b4pp/3pB1N1/p2Pq2Q/PpP5/6PK/8/8&lastMove=f4g6&check=h8&arrows=Ge6g8,Bh7&squares=a3,c3
async def render_svg(request):
    svg_data = service.make_svg(request)
    print(type(svg_data))
    return aiohttp.web.Response(text=svg_data, content_type="image/svg+xml")


# board.png?fen=5r1k/1b4pp/3pB1N1/p2Pq2Q/PpP5/6PK/8/8&lastMove=f4g6&check=h8&arrows=Ge6g8,Bh7&squares=a3,c3
async def render_png(request):
    svg_data = service.make_svg(request)
    png_data = cairosvg.svg2png(bytestring=svg_data)
    with open("output.png", "wb") as file:
        file.write(png_data)

    return aiohttp.web.Response(body=png_data, content_type="image/png")


async def recognize_chessboard(request):
    chessboard_image_path = "./chessboard.png"
    model = models.load_model(NN_MODEL_PATH)

    mock_args = argparse.Namespace()
    mock_args.quiet = False
    mock_args.debug = False
    mock_args.image_path = chessboard_image_path

    print("recognizer")
    print(mock_args)

    response = perform_recognition(mock_args, chessboard_image_path)
    return web.Response(text=response)


async def generate_tiles_from_chessboards(request):
    zip_file_path = generate_tiles_from_random_chessboard()

    response = web.FileResponse(zip_file_path)
    response.headers["Content-Disposition"] = 'attachment: filename="example.zip'
    return response


async def generate_chessboard(request):
    filepath = generate_random_chessboard("http://www.fen-to-image.com/image/32/{}")
    return web.FileResponse(filepath, headers={"Content-Type": "image/png"})
    

app = web.Application()
app.router.add_get("/recognize", recognize_chessboard)
app.router.add_get("/generate-chessboard", generate_chessboard)
app.router.add_get(
    "/generate-tiles-from-random-chessboard", generate_tiles_from_chessboards
)
app.router.add_get("/board.svg", render_svg)
app.router.add_get("/board.png", render_png)

web.run_app(app)
