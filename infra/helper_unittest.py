from helpers import Formatting

import unittest


class CheckFormatting(unittest.TestCase):
    def setUp(self):
        self.md_format = Formatting()
    
    def test_empty_case(self):
        self.assertEqual(self.md_format.remove_markdown(""), "")

    def test_remove_links(self):
        self.assertEqual(self.md_format.remove_markdown("this is a [link](https://www.google.com)."), "this is a link.")
    
    def test_remove_heading_and_lists(self):
        self.assertEqual(self.md_format.remove_markdown("##Heading 1\n###Heading 2\n- List1 \n- List 2"), "Heading 1\nHeading 2\n\nList1 \nList 2")

    def test_image(self):
        self.assertEqual(self.md_format.remove_markdown("![alt text](image.jpg)"), "")

    def test_code(self):
        self.assertEqual(self.md_format.remove_markdown("`code`"), "code")
