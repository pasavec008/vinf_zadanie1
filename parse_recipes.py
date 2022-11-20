import re
import json
import bz2
import multiprocessing as mp
from nltk.stem import WordNetLemmatizer

from time import time

def set_title(decoded_line):
    title = re.search('(?<=<title>).*(?=</title>)', decoded_line).group(0)
    mode = 1
    recipe_dict = {
        'title': title,
        'raw_text': '',
        'ingredients': []
    }
    return recipe_dict, mode

def delete_duplicates(raw_recipe_dict):
    raw_recipe_dict['ingredients'] = list(dict.fromkeys(raw_recipe_dict['ingredients']))
    raw_recipe_dict['ingredients'].sort()

def is_recipe(raw_recipe_dict, wl):
    blacklist = 'main_ingredient|with|usually|the|added|and|other|often|cooking|white|black|food|brewed|also|lot|typically|occasionally|http|www|title|[0-9]'
    title_blacklist = 'user|talk|[0-9]'
    if re.search(title_blacklist, raw_recipe_dict['title'].lower()):
        return 0
    checks = [0, 0]
    plainlist_case = 0
    for i in raw_recipe_dict['raw_text'].splitlines():
        if plainlist_case:
            if not re.search('\*', i):
                plainlist_case = 0
                delete_duplicates(raw_recipe_dict)
                checks[0] = 1
            else:
                [raw_recipe_dict['ingredients'].append(wl.lemmatize(ingredient).lower()) for ingredient in re.findall("(?!{})\\b\w+[\w\-']+\w".format(blacklist), i.lower())]
            continue
        if re.search('main_ingredient', i):
            raw_recipe_dict['ingredients'] = list(dict.fromkeys([wl.lemmatize(ingredient).lower() for ingredient in re.findall("(?!{})\\b\w+[\w\-']+\w".format(blacklist), i.lower())]))
            
            #recipe without ingredients
            if(not raw_recipe_dict['ingredients']):
                return 0
            if(raw_recipe_dict['ingredients'][0].lower() == 'plainlist'):
                plainlist_case = 1
                raw_recipe_dict['ingredients'].pop(0)
                continue
            delete_duplicates(raw_recipe_dict)
            checks[0] = 1
        if re.search('salt', i):
            checks[1] = 1
        if not 0 in checks:
            #print(recipe_dict)
            del raw_recipe_dict['raw_text']
            return raw_recipe_dict
    return 0

def parse_selected_recipes(recipes_to_parse, parsed_recipes, raw_read_done):
    print('p2 parse')
    wl = WordNetLemmatizer()
    while not raw_read_done[0]:
        while recipes_to_parse:
            print('p2 ', recipes_to_parse)
            parsed_maybe_recipe = is_recipe(recipes_to_parse.pop(), wl)
            if parsed_maybe_recipe:
                parsed_recipes.append(parsed_maybe_recipe)
    return

def read_raw(wiki_file_name, recipes_to_parse, raw_read_done):
    source_file = bz2.BZ2File(wiki_file_name, 'r')
    mode = 0
    for line in source_file:
        decoded_line = line.decode('utf-8')
        #finding title
        if mode == 0 and re.search('<title>', decoded_line):
            recipe_dict_raw, mode = set_title(decoded_line)
            continue
        
        #finding text start
        if mode == 1 and re.search('<text', decoded_line):
            mode = 2
            continue

        #finding end of text or printing
        if mode == 2:
            if re.search('</text>', decoded_line):
                mode = 0
                recipes_to_parse.append(recipe_dict_raw)
                print('p1 ', recipes_to_parse)
            else:
                recipe_dict_raw['raw_text'] += decoded_line
                #done = is_recipe(wl, source_file, decoded_line, checks, recipe_dict, recipes)
    
    raw_read_done[0] = True

    # print(str(len(recipes)) + ' recipes loaded successfully from raw wiki data.')

    # with open('parsed_recipes.json', 'w') as parsed_recipes:
    #     parsed_recipes.write(json.dumps(recipes))

def parse_recipes(wiki_file_name):
    # TODO: we need shared array recipes_to_parse and raw_read_done
    #mp.set_start_method('spawn')
    recipes_to_parse = []
    parsed_recipes = []
    raw_read_done = [False]
    # start = time()
    # read_raw(source_file, recipes_to_parse)
    # parse_selected_recipes(recipes_to_parse, parsed_recipes)
    # print("Linear time: ", round(time() - start, 2), ' seconds.')
    # return parsed_recipes

    start = time()
    # creating process
    p1 = mp.Process(target = read_raw, args=(wiki_file_name, recipes_to_parse, raw_read_done))
    p2 = mp.Process(target = parse_selected_recipes, args=(recipes_to_parse, parsed_recipes, raw_read_done))
 
    print('ahoj')
    # starting process 1
    p1.start()
    # starting process 2
    p2.start()
    print('cau')
 
    # wait until process 1 is completely executed
    p1.join()
    print('nazdar')
    # wait until process 2 is completely executed
    p2.join()
 
    print('Number of parsed: ', len(parsed_recipes))
    # both processes completely executed
    print("Parallel time: ", round(time() - start, 2), ' seconds.')

    return parsed_recipes