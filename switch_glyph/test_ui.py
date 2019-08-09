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
        self.assert_is_row(self.ui.layout.children[0])

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

    def test_on_add_inserts_row_before_add_remove_row(self):
        ui = layer.UI()
        add_remove_id = ui.layout.children[0].id
        ui.on_add()
        self.assertEqual(len(ui.layout.children), 2)
        self.assertEqual(ui.layout.children[-1].id, add_remove_id)

    def test_on_add_inserts_row(self):
        self.ui.on_add()
        self.assert_is_row(self.ui.layout.children[0])

    def test_on_remove_reduces_buttons_by_one(self):
        expect = self.ui.layout.children[0].id
        self.ui.on_add()
        self.ui.on_remove()
        self.assertEqual(self.ui.layout.children[-1].id, expect)

    def assert_is_row(self, child):
        self.assertIsInstance(child, bokeh.layouts.Row)
