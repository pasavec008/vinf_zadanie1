import re
import bz2
from multiprocessing import Process, Queue, Value
from nltk.stem import WordNetLemmatizer

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

def parse_selected_recipes(recipes_to_parse, parsed_recipes_queue, raw_read_done):
    wl = WordNetLemmatizer()
    while not raw_read_done.value:
        parsed_maybe_recipe = is_recipe(recipes_to_parse.get(), wl)
        if parsed_maybe_recipe:
            parsed_recipes_queue.put(parsed_maybe_recipe)
    #print('done')
    parsed_recipes_queue.put(0)
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
                recipes_to_parse.put(recipe_dict_raw)
            else:
                recipe_dict_raw['raw_text'] += decoded_line
    raw_read_done.value = 1

def parse_recipes(wiki_file_name):
    #create queues for shared "arrays"
    recipes_to_parse = Queue()
    parsed_recipes_queue = Queue()
    parsed_recipes = []
    raw_read_done = Value('i', 0)

    # creating processes
    p1 = Process(target = read_raw, args=(wiki_file_name, recipes_to_parse, raw_read_done))
    p2 = Process(target = parse_selected_recipes, args=(recipes_to_parse, parsed_recipes_queue, raw_read_done))
 
    # starting processes
    p1.start()
    p2.start()
 
    #after this while, all processes should be completely executed
    while 1:
        new_recipe = parsed_recipes_queue.get()
        if not new_recipe:
            break
        parsed_recipes.append(new_recipe)
 
    return parsed_recipes