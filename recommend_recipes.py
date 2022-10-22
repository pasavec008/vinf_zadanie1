from nltk.stem import WordNetLemmatizer

def recommend_recipes(recipes):
    wl = WordNetLemmatizer()
    wanted_ingredients = input('\n\n\n\n\nEnter your food ingredients separated by spaces:\n').split(' ')
    for i, ingredient in enumerate(wanted_ingredients):
        wanted_ingredients[i] = wl.lemmatize(ingredient).lower()
    wanted_ingredients.sort()

    print(wanted_ingredients)

    print('\n')

    recipes_score_index = []
    for index, recipe in enumerate(recipes):
        number_of_matches = len(list(set(recipe['ingredients']).intersection(wanted_ingredients)))
        number_of_recipe_ingredients = -len(recipe['ingredients'])
        if number_of_matches:
            recipes_score_index.append([number_of_matches, number_of_recipe_ingredients, index])
    #sort by most matches
    recipes_score_index.sort(reverse=True)

    #print top 3
    how_many_top = 3 if len(recipes_score_index) > 3 else len(recipes_score_index)
    for i in range(how_many_top):
        print('Recipe name: ', recipes[recipes_score_index[i][2]]['title'])
        print('Ingredients: ', recipes[recipes_score_index[i][2]]['ingredients'])
        print('Number of matched ingredients: ', recipes_score_index[i][0], '/', -recipes_score_index[i][1], '\n')
        
    #print(wanted)
    return