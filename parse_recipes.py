import re

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

def is_recipe(decoded_line, checks, recipe_dict, recipes):
    if 'User' in recipe_dict['title']:
        return 0
    if 'main_ingredient' in decoded_line:
        recipe_dict['ingredients'] = list(dict.fromkeys([ingredient.lower() for ingredient in re.findall("(?!main_ingredient)\\b\w+[\w -']+\w", decoded_line)]))
        checks[0] = 1
    if 'salt' in decoded_line:
        checks[1] = 1
    if not 0 in checks:
        print(recipe_dict)
        recipes.append(recipe_dict)
        return 1
    return 0
    
def parse_recipes(source_file):
    recipes = []
    mode = 0
    for index, line in enumerate(source_file):
        decoded_line = line.decode('utf-8')

        #finding title
        if mode == 0 and '<title>' in decoded_line:
            recipe_dict, mode, checks, done = set_title(decoded_line)
            continue
        
        #finding text start
        if mode == 1 and '<text' in decoded_line :
            mode = 2
            continue

        #finding end of text or printing
        if mode == 2:
            if '</text>' in decoded_line:
                mode = 0
            elif not done:
                done = is_recipe(decoded_line, checks, recipe_dict, recipes)

        # if index > MAX_NUMBER_OF_LINES:
        #     return