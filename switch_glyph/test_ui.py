import unittest
import layer
import bokeh.models


class TestUI(unittest.TestCase):
    def setUp(self):
        self.ui = layer.UI()

    def test_add_remove_buttons(self):
        self.assertIsInstance(
                self.ui.layout, bokeh.layouts.Column)

    def test_layout_has_one_row(self):
        result = self.ui.layout.children[0]
        expect = bokeh.layouts.Row
        self.assertIsInstance(result, expect)

    def test_layout_has_add_button(self):
        row = self.ui.layout.children[-1]
        labels = []
        for child in row.children:
            if isinstance(child, bokeh.models.Button):
                labels.append(child.label)
        self.assertIn("Add", labels)

    def test_layout_has_remove_button(self):
        row = self.ui.layout.children[-1]
        labels = []
        for child in row.children:
            if isinstance(child, bokeh.models.Button):
                labels.append(child.label)
        self.assertIn("Remove", labels)

    def test_on_add_adds_a_button_to_the_layout(self):
        ui = layer.UI()
        ui.on_add()
        self.assertEqual(len(ui.layout.children), 2)

    def test_on_remove_reduces_buttons_by_one(self):
        ui = layer.UI()
        ui.on_add()
        ui.on_remove()
        self.assertEqual(len(ui.layout.children), 1)
