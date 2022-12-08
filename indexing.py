def create_inverted_index(recipes):
    indexed_recipes = {}
    for recipe in recipes:
        for ingredient in recipe['ingredients']:
            if ingredient in indexed_recipes:
                indexed_recipes[ingredient].append(recipe['title'])
            else:
                indexed_recipes[ingredient] = [recipe['title']]
    for ingredient in indexed_recipes:
        indexed_recipes[ingredient].sort()
    return indexed_recipes

def search_in_inverted_index(recipes_index, index_search_input):
    for index_input in index_search_input:
        if index_input in recipes_index:
            print('Ingredient', index_input, 'is in these recipes:', recipes_index[index_input])
        else:
            print('We did not find ingredient', index_input, 'in any of our recipes.')
    return