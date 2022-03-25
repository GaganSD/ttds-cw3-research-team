from helpers import Formatting

import unittest


class CheckFormatting(unittest.TestCase):
    def setUp(self):
        self.md_format = Formatting()
    
    def test_md_empty_case(self):
        self.assertEqual(self.md_format.remove_markdown(""), "")

    def test_md_remove_links(self):
        self.assertEqual(self.md_format.remove_markdown("this is a [link](https://www.google.com)."), "this is a link.")
    
    def test_md_remove_heading_and_lists(self):
        self.assertEqual(self.md_format.remove_markdown("##Heading 1\n###Heading 2\n- List1 \n- List 2"), "Heading 1\nHeading 2\n\nList1 \nList 2")

    def test_md_image(self):
        self.assertEqual(self.md_format.remove_markdown("![alt text](image.jpg)"), "")

    def test_md_code(self):
        self.assertEqual(self.md_format.remove_markdown("`code`"), "code")

    def test_latex_empty_case(self):
        self.assertEqual(self.md_format.remove_latex(""), "")

    def test_latex_remove_links(self):
        self.assertEqual(self.md_format.remove_latex("\href{http://www.example.com}{Link to Example}."), "this is a link.")
    
    def test_latex_remove_heading_and_lists(self):
        self.assertEqual(self.md_format.remove_latex("##Heading 1\n###Heading 2\n- List1 \n- List 2"), "Heading 1\nHeading 2\n\nList1 \nList 2")

    def test_latex_image(self):
        self.assertEqual(self.md_format.remove_latex("![alt text](image.jpg)"), "")

    def test_latex_code(self):
        self.assertEqual(self.md_format.remove_latex("`code`"), "code")
