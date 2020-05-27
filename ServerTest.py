import unittest
import server
import sqlite3
from PIL import Image

server.db = "test.db"

def reinit_db():
    '''
    Reinitializes test db between cases
    :return: None, modifies db direclty
    '''
    conn = sqlite3.connect(server.db)
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS pixels;''')
    c.execute('''CREATE TABLE IF NOT EXISTS pixels (user text, x int, y int, r int, g int, b int);''')
    conn.commit()
    conn.close()


class TestPlotPixel(unittest.TestCase):
    '''
    Testing strategy:

    Partition on pixel:
        Pixel does not exist in db
        Pixel exists in db
    '''

    def test_new_plot(self):
        # Covers pixel does not exist in db
        reinit_db()
        server.plot_pixel("test", 0, 0, 255, 255, 255)

        # Fetch pixel from db
        db = sqlite3.connect(server.db)
        c = db.cursor()
        pixel = c.execute(
            '''SELECT r, g, b FROM pixels WHERE (user = 'test' AND x = 0 AND y = 0);''').fetchone()
        db.commit()
        db.close()

        # Check pixel values
        self.assertIsNotNone(pixel, "Expected pixel to be added to database at position (0, 0)")
        r, g, b = pixel
        self.assertEqual(r, 255, "Expected R value of pixel to be 255, was " + str(r))
        self.assertEqual(g, 255, "Expected R value of pixel to be 255, was " + str(g))
        self.assertEqual(b, 255, "Expected R value of pixel to be 255, was " + str(b))

    def test_existing_plot(self):
        # Covers pixel exists in db
        reinit_db()
        server.plot_pixel("test", 0, 0, 255, 255, 255)
        server.plot_pixel("test", 0, 0, 0, 0, 0)

        # Fetch pixel from db
        db = sqlite3.connect(server.db)
        c = db.cursor()
        pixel = c.execute(
            '''SELECT r, g, b FROM pixels WHERE (user = 'test' AND x = 0 AND y = 0);''').fetchone()
        db.commit()
        db.close()

        # Check pixel values
        self.assertIsNotNone(pixel, "Expected pixel to be added to database at position (0, 0)")
        r, g, b = pixel
        self.assertEqual(r, 0, "Expected R value of pixel to be 0, was " + str(r))
        self.assertEqual(g, 0, "Expected R value of pixel to be 0, was " + str(g))
        self.assertEqual(b, 0, "Expected R value of pixel to be 0, was " + str(b))


class TestRenderImage(unittest.TestCase):
    '''
    Testing strategy:

    Partitions on image:
        Image has 0 pixels
        Image has 1 pixel
        Image has >1 pixels
    '''

    def test_0_pixel_image(self):
        # Covers image has 0 pixels
        reinit_db()
        im = server.render_image()
        self.assertEqual(im.size, (0, 0), "expected 0x0 image")

    def test_pixel_image(self):
        # Covers image has 1 pixel
        reinit_db()
        server.plot_pixel("test", 0, 0, 255, 255, 255)
        im = server.render_image()
        self.assertEqual(im.size, (1, 1), "expected 1x1 image")
        self.assertEqual(im.getpixel((0, 0)), (255, 255, 255), "expected image to consist of a white pixel")

    def test_checkerboard_image(self):
        # Covers image has >1 pixel
        reinit_db()
        server.plot_pixel("test", 0, 0, 255, 255, 255)
        server.plot_pixel("test", 0, 1, 0, 0, 0)
        server.plot_pixel("test", 1, 0, 0, 0, 0)
        server.plot_pixel("test", 1, 1, 255, 255, 255)
        im = server.render_image()
        self.assertEqual(im.size, (2, 2), "expected 2x2 image")
        self.assertEqual(im.getpixel((0, 0)), (255, 255, 255), "expected image to consist of a white pixel at (0,0)")
        self.assertEqual(im.getpixel((0, 1)), (0, 0, 0), "expected image to consist of a black pixel at (0,1)")
        self.assertEqual(im.getpixel((1, 0)), (0, 0, 0), "expected image to consist of a black pixel at (1,0)")
        self.assertEqual(im.getpixel((1, 1)), (255, 255, 255), "expected image to consist of a white pixel at (1,1)")


if __name__ == '__main__':
    unittest.main()
