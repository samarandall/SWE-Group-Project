import requests
BASE_URL = 'http://www.themealdb.com/api/json/v1/1/'

'''
def search_for_recipe_by_name(name):
    FULL_URL = f'{BASE_URL}search.php?s={name}'

    response = requests.get(
        FULL_URL
    )

    data = response.json()
    return data


def search_for_recipe_by_ingredient(ingredient):
    FULL_URL = f'{BASE_URL}filter.php?i={ingredient}'

    response = requests.get(
        FULL_URL
    )

    data = response.json()
    for meal in data['meals']:
        print(meal['strMeal'])
    return data['meals']
'''

def get_random_meal():
    FULL_URL = f'{BASE_URL}random.php'

    response = requests.get(
        FULL_URL
    )

    data = response.json()
    meal = data['meals'][0]
    
    meal_name = meal['strMeal']
    meal_category = meal['strCategory']
    meal_instructions = meal['strInstructions']
    
    meal_ingredients = []
    for i in range(1,21):
        ingredient = meal[f'strIngredient{i}']
        if ingredient:
            meal_ingredients.append(ingredient)

    return (meal_name, meal_category, meal_instructions, meal_ingredients)

#print(get_random_meal())
#print(search_for_recipe_by_ingredient('chicken'))
#print(search_for_recipe_by_name('pasta'))
