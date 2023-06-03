"""An HTTP service that renders chess board images"""

import argparse
import asyncio
import aiohttp.web
import chess
import chess.svg
import cairosvg
import json
import os
import re
import cv2


def load_theme(name):
    with open(os.path.join(os.path.dirname(__file__), f"{name}.json")) as f:
        return json.load(f)


THEMES = {name: load_theme(name) for name in ["wikipedia", "lichess-blue", "lichess-brown"]}


class Service:
    def make_svg(self, request):
        try:
            board = chess.Board(request.query["fen"])
        except KeyError:
            raise aiohttp.web.HTTPBadRequest(reason="fen required")
        except ValueError:
            raise aiohttp.web.HTTPBadRequest(reason="invalid fen")

        try:
            size = min(max(int(request.query.get("size", 360)), 16), 1024)
        except ValueError:
            raise aiohttp.web.HTTPBadRequest(reason="size is not a number")

        try:
            uci = request.query.get("lastMove") or request.query["lastmove"]
            lastmove = chess.Move.from_uci(uci)
        except KeyError:
            lastmove = None
        except ValueError:
            raise aiohttp.web.HTTPBadRequest(reason="lastMove is not a valid uci move")

        try:
            check = chess.parse_square(request.query["check"])
        except KeyError:
            check = None
        except ValueError:
            raise aiohttp.web.HTTPBadRequest(reason="check is not a valid square name")

        try:
            arrows = [chess.svg.Arrow.from_pgn(s.strip()) for s in request.query.get("arrows", "").split(",") if s.strip()]
        except ValueError:
            raise aiohttp.web.HTTPBadRequest(reason="invalid arrow")

        try:
            squares = chess.SquareSet(chess.parse_square(s.strip()) for s in request.query.get("squares", "").split(",") if s.strip())
        except ValueError:
            raise aiohttp.web.HTTPBadRequest(reason="invalid squares")

        flipped = request.query.get("orientation", "white") == "black"

        coordinates = request.query.get("coordinates", "0") in ["", "1", "true", "True", "yes"]

        try:
            colors = THEMES[request.query.get("colors", "lichess-brown")]
        except KeyError:
            raise aiohttp.web.HTTPBadRequest(reason="theme colors not found")

        return chess.svg.board(board,
                               coordinates=coordinates,
                               flipped=flipped,
                               lastmove=lastmove,
                               check=check,
                               arrows=arrows,
                               squares=squares,
                               size=size,
                               colors=colors)

    async def render_svg(self, request):
        svg_data = self.make_svg(request)
        print(type(svg_data))
        return aiohttp.web.Response(text=svg_data, content_type="image/svg+xml")

    async def render_png(self, request):
        svg_data = self.make_svg(request)
        png_data = cairosvg.svg2png(bytestring=svg_data)
        with open('output.png', 'wb') as file:
            file.write(png_data)

        return aiohttp.web.Response(body=png_data, content_type="image/png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", "-p", type=int, default=8080, help="web server port")
    parser.add_argument("--bind", default="127.0.0.1", help="bind address (default: 127.0.0.1)")
    args = parser.parse_args()

    app = aiohttp.web.Application()
    service = Service()
    app.router.add_get("/board.png", service.render_png)
    app.router.add_get("/board.svg", service.render_svg)

    aiohttp.web.run_app(app, port=args.port, host=args.bind, access_log=None)
