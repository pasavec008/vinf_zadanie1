import bz2
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
from parse_recipes import parse_recipes
from recommend_recipes import recommend_recipes

def main():
    source_file = bz2.BZ2File('3_big.bz2', 'r')
    recipes = parse_recipes(source_file)
    recommend_recipes(recipes)


main()