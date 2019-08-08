import unittest
import main


class TestEditor(unittest.TestCase):
    def setUp(self):
        self.editor = main.Editor()
        self.setting = main.Setting()

    def test_editor_given_setting_changes_line_color(self):
        self.editor.active = True
        self.editor.setting = self.setting
        self.editor.on_change("line_color")(None, None, "blue")
        result = self.setting.line_color
        expect = "blue"
        self.assertEqual(expect, result)

    def test_render(self):
        self.editor.render(main.Setting(line_color="blue"))
        result = self.editor.dropdowns["line_color"].label
        expect = "blue"
        self.assertEqual(expect, result)
