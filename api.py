import requests
BASE_URL = 'http://www.themealdb.com/api/json/v1/1/'

def search_for_recipe_by_name(name):
    FULL_URL = f'{BASE_URL}search.php?s={name}'
    
    response = requests.get(
        FULL_URL
    )
    
    data = response.json()
    print(data)
    
    
def search_for_recipe_by_category(category):
    FULL_URL = f'{BASE_URL}filter.php?c={category}'
    
    response = requests.get(
        FULL_URL
    )
    
    data = response.json()
    print(data)
    
def get_random_meal():
    FULL_URL = f'{BASE_URL}random.php'
    
    response = requests.get(
        FULL_URL
    )
    
    data = response.json()
    
    print(data)
    

#get_random_meal()
#search_for_recipe_by_category('chicken')
#search_for_recipe_by_name('pasta')
