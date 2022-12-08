import json
import nltk
from time import time
from parse_recipes import parsing_wiki
from recommend_recipes import recommend_recipes
from indexing import create_inverted_index
from indexing import search_in_inverted_index

# you can specify actions program should make
# r - read and parse recipes from raw wiki data (this can take a while)
# f - read already parsed recipes from .json file
# s - start recipe recommending
# w - save parsed data to json file
# x - exit application
# ci - create inverted index
# si - search index
#USER_INPUT = ['f', 's', 'w', 'f', 's', 'ci', 'si' 'x']
USER_INPUT = ['r', 'ci', 'si', 'x']

# if you have specified 'is' in USER_INPUT, you also need INDEX_SEARCH_INPUT
# which are ingredients and index search will find you all foods containing that ingredient
INDEX_SEARCH_INPUT = ['salmon', 'caramel', 'nori']

# specify ingredients for recommending
RECOMMENDING_USER_INPUT = ['oil', 'potato', 'salt']

# name of file for parsing
# you need to add this file to hadoop with command
# hadoop fs -put /vinf_recipes/1.bz2 /user/root
WIKI_FILE_NAME = '1.bz2'

def welcome():
    print('''\n\n\n
Welcome to our recipe recommendation application. Enter one of these letters for corresponding action:\n
r -> read and parse recipes from raw wiki data (this can take a while)
f -> read already parsed recipes from .json file
s -> start recipe recommending
x -> exit application
w -> save parsed data to json file
ci -> create inverted index
si -> search index\n''')


def main():
    # we need to put file on hadoop first -> with this command in console:
    # where 1 is name of file and second argument is location 
    # hadoop fs -put /vinf_recipes/1.bz2 /user/root

    # then start our program with
    # spark-submit main.py

    nltk.download('wordnet')
    nltk.download('omw-1.4')

    recipes = None
    indexed_recipes = None
    welcome()
    for letter in USER_INPUT:
        print('User input', letter)

        if letter == 'r':
            start = time()
            recipes = parsing_wiki(WIKI_FILE_NAME)
            print("Parsing recipes from raw wiki data completed in time: ", round(time() - start, 2), ' seconds.')
            print(str(len(recipes)) + ' recipes parsed successfully from raw wiki file.\n')

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

        elif letter == 'w':
            if recipes == None:
                print('Firstly, you need to read data! (with option "r" or "f")\n')
                continue
            with open('parsed_recipes.json', 'w') as parsed_recipes:
                parsed_recipes.write(json.dumps(recipes))
                print(str(len(recipes)) + ' recipes saved successfully to json.\n')
        
        elif letter == 'ci':
            if recipes == None:
                print('Firstly, you need to read data! (with option "r" or "f")\n')
                continue
            else:
               indexed_recipes = create_inverted_index(recipes)
               print('Recipes index created success')
        
        elif letter == 'si':
            if indexed_recipes == None:
                print('Firstly, you need create index! (with option "ci")\n')
                continue
            else:
                search_in_inverted_index(indexed_recipes, INDEX_SEARCH_INPUT)

        elif letter == 'x':
            return

        else:
            print('Unknown option!\n')
            continue

if __name__ == '__main__':
    main()