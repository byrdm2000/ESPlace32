import unittest
import server
import sqlite3


class TestPlotPixel(unittest.TestCase):
    def test_new_plot(self):
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


if __name__ == '__main__':
    unittest.main()
