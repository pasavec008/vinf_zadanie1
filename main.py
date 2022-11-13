import bz2
import json
import nltk
from time import time
nltk.download('wordnet')
nltk.download('omw-1.4')
from parse_recipes import parse_recipes
from recommend_recipes import recommend_recipes

WIKI_FILE = '3_big.bz2'

def welcome():
    print('''\n\n\n
Welcome to our recipe recommendation application. Enter one of these letters for corresponding action:\n
r -> read and parse recipes from raw wiki data (this can take a while)
f -> read already parsed recipes from .json file
s -> start recipe recommending
x -> exit application\n''')

def main():
    recipes = None
    welcome()
    while (True):
        user_input = input('Enter letter: ').lower()

        if user_input == 'r':
            start = time()
            source_file = bz2.BZ2File(WIKI_FILE, 'r')
            recipes = parse_recipes(source_file)
            print("Parsing recipes from raw wiki data completed in time: ", round(time() - start, 2), ' seconds.')

        elif user_input == 'f':
            parsed_recipes = open('parsed_recipes.json')
            recipes = json.load(parsed_recipes)
            print(str(len(recipes)) + ' recipes loaded successfully from parsed json data.\n')

        elif user_input == 's':
            if recipes == None:
                print('Firstly, you need to read data! (with option "r" or "f")\n')
                continue
            else:
                recommend_recipes(recipes)
                welcome()

        elif user_input == 'x':
            return

        else:
            print('Unknown option!\n')
            continue

main()