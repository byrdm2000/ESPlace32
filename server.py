from flask import Flask, request
from PIL import Image
import numpy as np
import sqlite3
import base64
from io import BytesIO

app = Flask(__name__)
db = "place.db"


def plot_pixel(user, x_pos, y_pos, r, g, b):
    """
    Plots a pixel onto the image at given position with given color values
    :param user: String of username to associate with pixel
    :param x_pos: X position of pixel to plot. Must be a non-negative integer.
    :param y_pos: Y position of pixel to plot. Must be a non-negative integer.
    :param r: Red color value for pixel, an integer between 0 and 255 inclusive
    :param g: Green color value for pixel, an integer between 0 and 255 inclusive
    :param b: Blue color value for pixel, an integer between 0 and 255 inclusive
    :return: None, modifies database directly
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pixels (user text, x int, y int, r int, g int, b int);''')

    # Check if pixel exists
    pixel = c.execute('''SELECT * FROM pixels WHERE (x = ? AND y = ?);''', (x_pos, y_pos)).fetchone()
    if pixel is None:
        # Add new pixel
        c.execute('''INSERT INTO pixels VALUES (?, ?, ?, ?, ?, ?);''', (user, x_pos, y_pos, r, g, b))
    else:
        # Update pixel
        c.execute('''UPDATE pixels SET user = ?, r = ?, g = ?, b = ? WHERE (x = ? AND y = ?);''',
                  (user, r, g, b, x_pos, y_pos))
    conn.commit()
    conn.close()


def render_image():
    """
    Renders a Pillow Image object from pixels plotted in db
    :return: Image object with pixel values as stored in db, white if not stored
    """
    # Get image size
    conn = sqlite3.connect(db)
    c = conn.cursor()
    max_x = c.execute('''SELECT x FROM pixels ORDER BY x DESC;''').fetchone()
    max_y = c.execute('''SELECT y FROM pixels ORDER BY y DESC;''').fetchone()

    if max_x is None or max_y is None:
        size = (0, 0)
        return Image.new('RGB', size)
    else:
        size = (max_x[0] + 1, max_y[0] + 1)

    # Get pixels
    pixels = c.execute('''SELECT x, y, r, g, b FROM pixels;''').fetchall()
    size_x, size_y = size
    pixel_array = np.array([[(0, 0, 0)]*size_y]*size_x, np.uint8)
    for x, y, r, g, b in pixels:
        pixel_array[x][y] = (r, g, b)

    # Close and render
    conn.commit()
    conn.close()
    return Image.fromarray(pixel_array)

@app.route('/', methods = ['GET', 'POST'])
def request_handler():
    if request.method == 'POST':
        form = request.get('form')
        user = form.get('user')
        pixel_x = form.get('x')
        pixel_y = form.get('y')
        pixel_r = form.get('r')
        pixel_g = form.get('g')
        pixel_b = form.get('b')
        if user is None or pixel_x is None or pixel_y is None or pixel_r is None or pixel_g is None or pixel_b is None:
            return "Missing params"
        else:
            plot_pixel(user, int(pixel_x), int(pixel_y), int(pixel_r), int(pixel_g), int(pixel_b))
            return "Plotted pixel successfully"
    elif request.method == 'GET':
        buffered_image = BytesIO()
        im = render_image()
        im.save(buffered_image, format='PNG')
        im_b64 = base64.b64encode(buffered_image.getvalue())
        print(im_b64)
        # TODO: fix this
        return '<img src="data:image/png;base64,' + str(im_b64) + '"/>'

