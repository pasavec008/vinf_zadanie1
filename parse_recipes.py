import re
from nltk.stem import WordNetLemmatizer

MAX_NUMBER_OF_LINES = 10000000

def set_title(decoded_line):
    title = re.search('(?<=<title>).*(?=</title>)', decoded_line).group(0)
    mode = 1
    checks = [0, 0]
    done = 0
    recipe_dict = {
        'title': title,
        'ingredients': []
    }
    return recipe_dict, mode, checks, done

def get_ingredients_from_plainlist(wl, source_file, recipe_dict, blacklist):
    for line in source_file:
        decoded_line = line.decode('utf-8')
        if not re.search('\*', decoded_line):
            return
        [recipe_dict['ingredients'].append(wl.lemmatize(ingredient).lower()) for ingredient in re.findall("(?!{})\\b\w+[\w\-']+\w".format(blacklist), decoded_line.lower())]

def is_recipe(wl, source_file, decoded_line, checks, recipe_dict, recipes):
    blacklist = 'main_ingredient|with|usually|the|added|and|other|often|cooking|white|black|food|brewed'
    if re.search('User', recipe_dict['title']):
        return 0
    if re.search('main_ingredient', decoded_line):
        recipe_dict['ingredients'] = list(dict.fromkeys([wl.lemmatize(ingredient).lower() for ingredient in re.findall("(?!{})\\b\w+[\w\-']+\w".format(blacklist), decoded_line.lower())]))
        
        #recipe without ingredients
        if(not recipe_dict['ingredients']):
            return 0
        if(recipe_dict['ingredients'][0].lower() == 'plainlist'):
            recipe_dict['ingredients'].pop(0)
            get_ingredients_from_plainlist(wl, source_file, recipe_dict, blacklist)
        #delete duplicates
        recipe_dict['ingredients'] = list(dict.fromkeys(recipe_dict['ingredients']))
        recipe_dict['ingredients'].sort()
        checks[0] = 1
    if re.search('salt', decoded_line):
        checks[1] = 1
    if not 0 in checks:
        print(recipe_dict)
        recipes.append(recipe_dict)
        return 1
    return 0
    
def parse_recipes(source_file):
    recipes = []
    mode = 0
    wl = WordNetLemmatizer()
    for line in source_file:
        decoded_line = line.decode('utf-8')
        #finding title
        if mode == 0 and re.search('<title>', decoded_line):
            recipe_dict, mode, checks, done = set_title(decoded_line)
            continue
        
        #finding text start
        if mode == 1 and re.search('<text', decoded_line):
            mode = 2
            continue

        #finding end of text or printing
        if mode == 2:
            if re.search('</text>', decoded_line):
                mode = 0
            elif not done:
                done = is_recipe(wl, source_file, decoded_line, checks, recipe_dict, recipes)

        # if index > MAX_NUMBER_OF_LINES:
        #     return
    print(recipes)
    return recipes