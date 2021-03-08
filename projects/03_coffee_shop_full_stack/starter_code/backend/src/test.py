# Holds code to manually add drinks before connecting to the website
def add_drink(title, recipe):
    drink = Drink(title=title, recipe=recipe)
    print(drink)
    drink.insert()

# recipe_1 = [{'color': 'Blue', 'parts': 1, 'name': 'Absinthe'}, {'color': 'Orange', 'parts': 1, 'name': 'Moo'}]
# recipe_2 = [{'color': 'Green', 'parts': 1, 'name': 'Vermooth'}, {'color': 'Yellow', 'parts': 1, 'name': 'Lemon'}]

# add_drink(title='Shalily Sunset', recipe=json.dumps(recipe_2))