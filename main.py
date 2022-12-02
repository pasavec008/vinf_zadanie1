import json
import nltk
from time import time
from parse_recipes import parse_recipes
from recommend_recipes import recommend_recipes

#pyspark
from pyspark import SparkContext, SparkConf 
from pyspark.sql import SparkSession
from pyspark.sql.types import *

sc = SparkContext('local[8]', 'vinf_recipes')
spark = SparkSession.builder.master('local[8]').appName('vinf_recipes').getOrCreate()

WIKI_FILE_NAME = '3_big.bz2'

def welcome():
    print('''\n\n\n
Welcome to our recipe recommendation application. Enter one of these letters for corresponding action:\n
r -> read and parse recipes from raw wiki data (this can take a while)
f -> read already parsed recipes from .json file
s -> start recipe recommending
x -> exit application
w -> save parsed data to json file\n''')

def parsing_wiki(row):
    print('cau')
    return 'cau'

def main():
    # we need to put file on hadoop first -> with this command in console:
    # hadoop fs -put /vinf_recipes/1

    f = sc.textFile("/1")
    df = spark.createDataFrame(f, StringType()).toDF("text")
    rdd2 = df.rdd.map(lambda row: parsing_wiki(row)).filter(lambda row: row != None)
    rdd2.saveAsTextFile("./recipes2")

    # nltk.download('wordnet')
    # nltk.download('omw-1.4')

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