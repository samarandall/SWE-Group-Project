import requests
BASE_URL = 'http://www.themealdb.com/api/json/v1/1/'

def get_meal(meal_id) -> tuple:
    FULL_URL = f'{BASE_URL}lookup.php?i={meal_id}'

    response = requests.get(
        FULL_URL
    )
    data = response.json()
    meal = data['meals'][0]

    meal_name = meal['strMeal']
    meal_category = meal['strCategory']
    meal_instructions = meal['strInstructions']
    meal_id = meal['idMeal']

    meal_ingredients = []
    for i in range(1,21):
        ingredient = meal[f'strIngredient{i}']
        if ingredient:
            meal_ingredients.append(ingredient)

    return (meal_name, meal_category, meal_instructions, meal_ingredients, meal_id)

def get_random_meal()-> tuple:
    FULL_URL = f'{BASE_URL}random.php'

    response = requests.get(
        FULL_URL
    )

    data = response.json()
    meal = data['meals'][0]

    meal_name = meal['strMeal']
    meal_category = meal['strCategory']
    meal_instructions = meal['strInstructions']
    meal_id = meal['idMeal']

    meal_ingredients = []
    for i in range(1,21):
        ingredient = meal[f'strIngredient{i}']
        if ingredient:
            meal_ingredients.append(ingredient)

    return (meal_name, meal_category, meal_instructions, meal_ingredients, meal_id)

def get_meal_name(meal_id):
    FULL_URL = f'{BASE_URL}lookup.php?i={meal_id}'
    response = requests.get(
        FULL_URL
    )
    data = response.json()
    meal = data['meals'][0]
    meal_name = meal['strMeal']
    
    return meal_name

#print(get_random_meal())
