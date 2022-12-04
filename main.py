import json
import nltk
import re
from time import time
from parse_recipes import parsing_wiki
from recommend_recipes import recommend_recipes

# you can specify actions program should make
# r - read and parse recipes from raw wiki data (this can take a while)
# f - read already parsed recipes from .json file
# s - start recipe recommending
# w - save parsed data to json file
# x - exit application
USER_INPUT = ['r', 's', 'w', 'f', 's', 'x']

# specify ingredients for recommending
RECOMMENDING_USER_INPUT = ['oil', 'potato', 'salt']

#WIKI_FILE_NAME = '3_big.bz2'

def welcome():
    print('''\n\n\n
Welcome to our recipe recommendation application. Enter one of these letters for corresponding action:\n
r -> read and parse recipes from raw wiki data (this can take a while)
f -> read already parsed recipes from .json file
s -> start recipe recommending
x -> exit application
w -> save parsed data to json file\n''')


def main():
    # we need to put file on hadoop first -> with this command in console:
    # where 1 is name of unziped .bz2 file and second argument is location 
    # hadoop fs -put /vinf_recipes/1 /user/root

    # then start our program with
    # spark-submit main.py

    # (OLD LOGIC) to get parsed file to our folder, enter this command to console:
    # hadoop fs -get ./recipes ./parsed_file

    nltk.download('wordnet')
    nltk.download('omw-1.4')

    recipes = None
    welcome()
    for letter in USER_INPUT:
        print('User input', letter)

        if letter == 'r':
            start = time()
            recipes = parsing_wiki()
            print("Parsing recipes from raw wiki data completed in time: ", round(time() - start, 2), ' seconds.')

        elif letter == 'f':
            parsed_recipes = open('parsed_recipes.json')
            recipes = json.load(parsed_recipes)
            print(str(len(recipes)) + ' recipes loaded successfully from parsed json data.\n')

        elif letter == 's':
            if recipes == None:
                print('Firstly, you need to read data! (with option "r" or "f")\n')
                continue
            else:
                recommend_recipes(recipes, RECOMMENDING_USER_INPUT)
                welcome()

        elif letter == 'w':
            if recipes == None:
                print('Firstly, you need to read data! (with option "r" or "f")\n')
                continue
            with open('parsed_recipes.json', 'w') as parsed_recipes:
                parsed_recipes.write(json.dumps(recipes))
                print(str(len(recipes)) + ' recipes saved successfully to json.\n')

        elif letter == 'x':
            return

        else:
            print('Unknown option!\n')
            continue

if __name__ == '__main__':
    main()