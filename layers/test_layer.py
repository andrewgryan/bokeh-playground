import unittest
import main


class TestEditor(unittest.TestCase):
    def test_editor(self):
        editor = main.Editor()
        editor.on_change("line_color")(None, None, "red")
