'''This file gets data from themealdb'''

import requests
BASE_URL = 'http://www.themealdb.com/api/json/v1/1/'

def get_meal(meal_id) -> tuple:
    '''This method fetches a specific meal from themealdb'''
    FULL_URL = f'{BASE_URL}lookup.php?i={meal_id}'

    response = requests.get(
        FULL_URL,
        timeout=50
    )
    data = response.json()
    meal = data['meals'][0]

    meal_name = meal['strMeal']
    meal_category = meal['strCategory']
    meal_instructions = meal['strInstructions']
    meal_id = meal['idMeal']
    meal_img = meal['strMealThumb']

    meal_ingredients = []
    for i in range(1,21):
        ingredient = meal[f'strIngredient{i}']
        measurement = meal[f"strMeasure{i}"]
        if ingredient:
            meal_ingredients.append((ingredient,measurement))

    return (meal_name, meal_category, meal_instructions, meal_ingredients, meal_id, meal_img)

def get_random_meal()-> tuple:
    '''This method fetches a random meal from themealdb'''
    FULL_URL = f'{BASE_URL}random.php'

    response = requests.get(
        FULL_URL,
        timeout=50
    )

    data = response.json()
    meal = data['meals'][0]

    meal_name = meal['strMeal']
    meal_category = meal['strCategory']
    meal_instructions = meal['strInstructions']
    meal_id = meal['idMeal']
    meal_img = meal['strMealThumb']

    meal_ingredients = []
    for i in range(1,21):
        ingredient = meal[f'strIngredient{i}']
        measurement = meal[f"strMeasure{i}"]
        if ingredient:
            meal_ingredients.append((ingredient,measurement))
    return (meal_name, meal_category, meal_instructions, meal_ingredients, meal_id, meal_img)

def get_meal_name(meal_id):
    '''This method fetches a specific meal name from themealdb'''
    FULL_URL = f'{BASE_URL}lookup.php?i={meal_id}'
    response = requests.get(
        FULL_URL,
        timeout=50
    )
    data = response.json()
    meal = data['meals'][0]
    meal_name = meal['strMeal']
    return meal_name

#get_random_meal()
