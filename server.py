from flask import Flask
import sqlite3

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

