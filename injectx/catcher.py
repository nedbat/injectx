from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading


# A 1-pixel transparent gif, from https://commons.wikimedia.org/wiki/File:Transparent.gif
ONE_PIXEL = "".join("""
47 49 46 38 39 61 01 00  01 00 80 00 00 00 00 00
ff ff ff 21 f9 04 01 00  00 00 00 2c 00 00 00 00
01 00 01 00 00 02 01 44  00 3b
""".split()).decode("hex")


# Adapted from http://wordaligned.org/articles/drawing-chessboards
def chessboard_bytes(n=8, pixel_width=200, bg='black', fg='white'):
    "Draw an n x n chessboard using PIL."
    from PIL import Image, ImageDraw
    from itertools import cycle
    import cStringIO as StringIO

    def sq_start(i):
        "Return the x/y start coord of the square at column/row i."
        return i * pixel_width // n

    def square(i, j):
        "Return the square corners, suitable for use in PIL drawings"
        return [
            sq_start(i), sq_start(j),
            sq_start(i+1)-1, sq_start(j+1)-1,
        ]

    image = Image.new("RGB", (pixel_width, pixel_width), bg)
    draw_square = ImageDraw.Draw(image).rectangle
    squares = (square(i, j)
               for i_start, j in zip(cycle((0, 1)), range(n))
               for i in range(i_start, n, 2))
    for sq in squares:
        draw_square(sq, fill=fg)

    out = StringIO.StringIO()
    image.save(out, format="PNG")
    return out.getvalue()


class Handler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.bytes = chessboard_bytes(pixel_width=32, bg="red", fg="green")
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_GET(self):
        print("path: %r\n" % (self.path,))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.bytes)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass


def start_catcher():
    port = 8003
    server = ThreadedHTTPServer(('0.0.0.0', port), Handler)
    catcher_thread = threading.Thread(target=server.serve_forever)
    catcher_thread.daemon = True
    catcher_thread.start()
    return port
