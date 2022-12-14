from nltk.stem import WordNetLemmatizer

def recommend_recipes(recipes, user_input):
    wl = WordNetLemmatizer()

    wanted_ingredients = user_input
    for i, ingredient in enumerate(wanted_ingredients):
        wanted_ingredients[i] = wl.lemmatize(ingredient).lower()
    wanted_ingredients.sort()

    recipes_score_index = []
    for index, recipe in enumerate(recipes):
        number_of_matches = len(list(set(recipe['ingredients']).intersection(wanted_ingredients)))
        number_of_recipe_ingredients = -len(recipe['ingredients'])
        if number_of_matches:
            recipes_score_index.append([number_of_matches, number_of_recipe_ingredients, index])
    #sort by most matches
    recipes_score_index.sort(reverse=True)

    #print top recipes
    how_many_top = 3 if len(recipes_score_index) >= 3 else len(recipes_score_index)
    print('Your {} recommended recipes:\n'.format(how_many_top))
    for i in range(how_many_top):
        print('Recipe name: ', recipes[recipes_score_index[i][2]]['title'])
        print('Ingredients: ', recipes[recipes_score_index[i][2]]['ingredients'])
        print('Number of matched ingredients: ', recipes_score_index[i][0], '/', -recipes_score_index[i][1], '\n')

    return