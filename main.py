import bz2
from parse_recipes import parse_recipes

def main():
    source_file = bz2.BZ2File('2.bz2', 'r')
    recipe_dict = parse_recipes(source_file)

main()