import json
import nltk
import re
from time import time
from parse_recipes import parse_recipes
from recommend_recipes import recommend_recipes
from nltk.stem import WordNetLemmatizer

#pyspark
from pyspark import SparkContext, SparkConf 
from pyspark.sql import SparkSession
from pyspark.sql.types import *

# this creates spark cluster, first argument is url and second is name of app
spark_context = SparkContext('local[8]', 'vinf_recipes')

# this create session, that encapsulate our context
spark_session = SparkSession.builder.master('local[8]').appName('vinf_recipes').getOrCreate()

WIKI_FILE_NAME = '3_big.bz2'

def welcome():
    print('''\n\n\n
Welcome to our recipe recommendation application. Enter one of these letters for corresponding action:\n
r -> read and parse recipes from raw wiki data (this can take a while)
f -> read already parsed recipes from .json file
s -> start recipe recommending
x -> exit application
w -> save parsed data to json file\n''')

def set_title(decoded_line):
    title = re.search('(?<=<title>).*(?=</title>)', decoded_line).group(0)
    mode = 1
    return title, mode

def parse_one_row(wl, row, variables_dict, blacklist, title_blacklist):
    row_text = row.__getitem__('text')
    #print(variables_dict['mode'] == 0, 'page' in row_text, type(row_text), ' aaaaaa ', row_text)
    #finding title
    if variables_dict['mode'] == 0 and '<title>' in row_text:
        variables_dict['title'], variables_dict['mode'] = set_title(row_text)
        return
    
    #finding text start
    elif variables_dict['mode'] == 1 and '<text' in row_text:
        variables_dict['mode'] = 2
        return

    #finding end of text or printing
    elif variables_dict['mode'] == 2:
        if (not variables_dict['salt_check']) and 'salt' in row_text:
            variables_dict['salt_check'] = 1
        if variables_dict['plainlist']:
            if not '*' in row_text:
                variables_dict['plainlist'] = 0
                variables_dict['ingredients'] = list(dict.fromkeys([wl.lemmatize(ingredient).lower() for ingredient in re.findall("(?!{})\\b\w+[\w\-']+\w".format(blacklist), variables_dict['ingredients'].lower())]))
                return
            variables_dict['ingredients'] += ' ' + row_text
            return
        elif 'main_ingredient' in row_text:
            variables_dict['ingredients'] = ''
            variables_dict['ingredients_check'] = 1
            if 'plainlist' in row_text.lower():
                variables_dict['plainlist'] = 1
                return
            else:
                variables_dict['ingredients'] = list(dict.fromkeys([wl.lemmatize(ingredient).lower() for ingredient in re.findall("(?!{})\\b\w+[\w\-']+\w".format(blacklist), row_text.lower())]))
                return 
        elif '</text>' in row_text:
            checks = 0
            if variables_dict['ingredients_check'] and variables_dict['salt_check'] and (not re.search(title_blacklist, variables_dict['title'].lower())):
                checks = 1
            variables_dict['ingredients_check'] = 0
            variables_dict['mode'] = 0
            variables_dict['salt_check'] = 0
            if checks:
                return variables_dict['title'] + ' #@#@# ' + ' '.join(variables_dict['ingredients'])
            return

    return

def parsing_wiki():
    print('Start of parsing')

    wl = WordNetLemmatizer()
    blacklist = 'main_ingredient|with|usually|the|added|and|other|often|cooking|white|black|food|brewed|also|lot|typically|occasionally|http|www|title|[0-9]'
    title_blacklist = 'user|talk|[0-9]'

    # this returns our file from hadoop as RDD of strings
    rdd_of_strings = spark_context.textFile('./1')
    print('File okay')

    # create dataframe with spark session
    df = spark_session.createDataFrame(rdd_of_strings, StringType()).toDF('text')
    print('Dataframe okay')

    # set variables we will use to dictionary
    variables_dict = {
        'mode': 0,
        'ingredients_check': 0,
        'plainlist': 0,
        'title': '',
        'ingredients': '',
        'salt_check': 0
    }

    rdd2 = df.rdd.map(lambda row: parse_one_row(wl, row, variables_dict, blacklist, title_blacklist)).filter(lambda row: row != None)

    # for k in rdd2.take(50):
    #     print(k)
    rdd2.saveAsTextFile('./recipes23')

    print('End of parsing')
    return

def main():
    nltk.download('wordnet')
    nltk.download('omw-1.4')

    welcome()

    # we need to put file on hadoop first -> with this command in console:
    # where 1 is name of unziped .bz2 file and second argument is location 
    # hadoop fs -put /vinf_recipes/1 /user/root

    # to get parsed file to our folder, enter this command to console:
    # hadoop fs -get ./recipes8 ./parsed_file

    #input('cauko')
    parsing_wiki()

    #rdd2.saveAsTextFile("./recipes2")

    

    # recipes = None
    # welcome()
    # while (True):
    #     user_input = input('Enter letter: ').lower()

    #     if user_input == 'r':
    #         start = time()
    #         recipes = parse_recipes(WIKI_FILE_NAME)
    #         print("Parsing recipes from raw wiki data completed in time: ", round(time() - start, 2), ' seconds.')

    #     elif user_input == 'f':
    #         parsed_recipes = open('parsed_recipes.json')
    #         recipes = json.load(parsed_recipes)
    #         print(str(len(recipes)) + ' recipes loaded successfully from parsed json data.\n')

    #     elif user_input == 's':
    #         if recipes == None:
    #             print('Firstly, you need to read data! (with option "r" or "f")\n')
    #             continue
    #         else:
    #             recommend_recipes(recipes)
    #             welcome()

    #     elif user_input == 'w':
    #         if recipes == None:
    #             print('Firstly, you need to read data! (with option "r" or "f")\n')
    #             continue
    #         with open('parsed_recipes.json', 'w') as parsed_recipes:
    #             parsed_recipes.write(json.dumps(recipes))
    #             print(str(len(recipes)) + ' recipes saved successfully to json.\n')

    #     elif user_input == 'x':
    #         return

    #     else:
    #         print('Unknown option!\n')
    #         continue

if __name__ == '__main__':
    main()