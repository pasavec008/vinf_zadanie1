import unittest
from indexing import *

class TestStringMethods(unittest.TestCase):
    def test_create_inverted_index(self):
        test_array_dict = [{
            'title': 'chips',
            'ingredients': ['salt']
        }]
        indexed_recipes = create_inverted_index(test_array_dict)
        self.assertEqual(indexed_recipes['salt'][0], 'chips')

    def test_search_in_inverted_index(self):
        recipes_index = {
            'salt': 'chips'
        }
        self.assertTrue(search_in_inverted_index(recipes_index, ['salt']))