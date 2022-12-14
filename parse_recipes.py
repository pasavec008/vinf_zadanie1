import re
from nltk.stem import WordNetLemmatizer

#pyspark
from pyspark import SparkContext, SparkConf 
from pyspark.sql import SparkSession
from pyspark.sql.types import *

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
            if variables_dict['ingredients_check'] and variables_dict['salt_check'] and (not re.match(title_blacklist, variables_dict['title'].lower())):
                checks = 1
            variables_dict['ingredients_check'] = 0
            variables_dict['mode'] = 0
            variables_dict['salt_check'] = 0
            if checks:
                return variables_dict['title'] + '#@#@#' + ' '.join(variables_dict['ingredients'])
            return
    return

def parsing_wiki(wiki_file):
    print('Start of parsing')
    # this creates spark cluster, first argument is url and second is name of app
    spark_context = SparkContext('local[*]', 'vinf_recipes')
    # set logs only for errors
    spark_context.setLogLevel('ERROR')

    # this create session, that encapsulate our context
    spark_session = SparkSession.builder.master('local[*]').appName('vinf_recipes').getOrCreate()

    wl = WordNetLemmatizer()
    blacklist = 'main_ingredient|with|usually|the|added|and|other|often|cooking|white|black|food|brewed|also|lot|typically|occasionally|http|www|title|[0-9]'
    title_blacklist = 'user|talk|[0-9]'

    # this returns our file from hadoop as RDD of strings
    rdd_of_strings = spark_context.textFile('./' + wiki_file)
    print('File loaded')

    # create dataframe with spark session
    df = spark_session.createDataFrame(rdd_of_strings, StringType()).toDF('text')
    print('Dataframe created')

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

    parsed_recipes = []

    for recipe_string in rdd2.take(2000):
        cut_string = recipe_string.split('#@#@#')
        title = cut_string[0]
        ingredients_list = cut_string[1].split(' ')
        for index, ingredient_looped in enumerate(ingredients_list):
            ingredients_list[index] = ingredients_list[index]
        recipe_dict = {
            'title': title,
            'ingredients': ingredients_list
        }
        parsed_recipes.append(recipe_dict)
    
    # for i in parsed_recipes:
    #     print(i)
    #rdd2.saveAsTextFile('./recipes23')

    print('End of parsing')
    return parsed_recipes