# Recipes Database
# NO ADDITIONAL IMPORTS!
import sys

sys.setrecursionlimit(20_000)


def replace_item(recipes, old_name, new_name):
    """
    Returns a new recipes list based on the input list, where all mentions of
    the food item given by old_name are replaced with new_name.
    """
    if old_name == 'compound' or old_name == 'atomic':
        return recipes
    
    modified_recipes = []
    for item in recipes:
        if item[0] == 'atomic':
            if item[1] == old_name:
                modified_recipes.append((item[0], new_name, item[2]))
            else:
                modified_recipes.append(item)
        else: 
            modified_item = []
            for food in item:
                if isinstance(food, str):
                    if food == old_name:
                        modified_item.append(new_name)
                    else:
                        modified_item.append(food)

                if isinstance(food, list):
                    appending_list = []
                    for ingredient in food:
                        if ingredient[0] == old_name:
                            appending_list.append((new_name, ingredient[1]))
                        else:
                            appending_list.append(ingredient)
                    modified_item.append(appending_list)
            modified_recipes.append(tuple(modified_item))

    return modified_recipes

def modified_data_structures(recipes):
    '''
    Creating two dictionaries from the existing representation; 
    one mapping atomic ingredients to their cost, 
    the other mapping compound ingredients to a set of tuples,
    with the fundamental ingredient as the first element and 
    the number of that ingredient as the second element
    '''
    atomic_dict = {}
    compound_dict = {}

    for item in recipes:
        if item[0] == 'atomic':
            atomic_dict[item[1]] = item[2]
        else:

            if item[1] not in compound_dict:
                compound_dict[item[1]] = []
                compound_dict[item[1]].append({food for food in item[2]})
            else:
                compound_dict[item[1]].append({food for food in item[2]})
    
    return atomic_dict, compound_dict

def lowest_cost(recipes, food_item, forbidden = []):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """
    if food_item in forbidden:
        return None

    improved_rep = modified_data_structures(recipes)

    def lowest_cost_inversion(dish):

        if dish in improved_rep[0].keys():
            # base case
            return improved_rep[0][dish]
        
        elif dish not in improved_rep[0].keys() and dish not in improved_rep[1].keys():
            return None

        elif dish in forbidden:
            return None
        
        else:
            cost = float('inf')

            for recipe in improved_rep[1][dish]:
                cost_of_dish = 0
                for ingredient in recipe: 
                    if ingredient[0] not in forbidden and lowest_cost_inversion(ingredient[0]) != None:
                        cost_of_dish = cost_of_dish + ingredient[1] * lowest_cost_inversion(ingredient[0])
                    else:
                        cost_of_dish = 0
                        break  
                if cost_of_dish != 0:  
                    cost = min(cost_of_dish, cost)
            if cost != float('inf'):
                return cost 
   
    return lowest_cost_inversion(food_item)

def cheapest_flat_recipe(recipes, food_item, forbidden = []):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing a full recipe for
    the given food item.
    """

    if food_item in forbidden:
        return None

    improved_rep = modified_data_structures(recipes)

    lowest_cost(recipes, food_item, forbidden = [])

    def cheapest_flat_recipe_recursion(dish):
        if dish in improved_rep[0].keys():
            # base case
            return {dish: 1}
        
        elif dish not in improved_rep[0].keys() and dish not in improved_rep[1].keys():
            return None

        elif dish in forbidden:
            return None
        
        else:
            cost = float('inf')

            for recipe in improved_rep[1][dish]:
                cost_of_dish = 0
                full_recipe = {}

                for ingredient in recipe: 
                    if ingredient[0] not in forbidden and cheapest_flat_recipe_recursion(ingredient[0]) != None:

                        ingredient_scaled = scale_dict(cheapest_flat_recipe_recursion(ingredient[0]), ingredient[1])
                        full_recipe = sum_dict(ingredient_scaled, full_recipe)
                        cost_of_dish += total_cost(ingredient_scaled)
                    else:
                        cost_of_dish = 0
                        break 
                
                if cost_of_dish != 0 and cost_of_dish < cost:

                    cost = cost_of_dish
                    cheapest_full_recipe = full_recipe

            if cost != float('inf'):
                return cheapest_full_recipe
    
    def total_cost(dictionary):
        '''
        Given a dictionary mapping atomic food items to quantities, returns the total cost of 
        purchasing all the atomic food items
        '''
        total_cost = 0
        for food in dictionary.keys():
            total_cost += dictionary[food] * improved_rep[0][food]
        
        return total_cost

    return cheapest_flat_recipe_recursion(food_item)

def all_flat_recipes(recipes, food_item, forbidden = []):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.
    """
    if food_item in forbidden:
        return []

    improved_rep = modified_data_structures(recipes)

    def all_flat_recursion(dish):
        recipes_list = []
        if dish in improved_rep[0].keys():
            # base case
            return [{dish: 1}]
        
        elif dish not in improved_rep[0].keys() and dish not in improved_rep[1].keys():
            return []

        elif dish in forbidden:
            return []
        
        else:
            
            for recipe in improved_rep[1][dish]:

                full_recipe_list = [{}]
                for ingredient in recipe: 
                    
                    if ingredient[0] not in forbidden and len(all_flat_recursion(ingredient[0])) != 0:
                        old_full_recipe_list = full_recipe_list[:]

                        for y in old_full_recipe_list:
                            
                            for ingredient_recipe in all_flat_recursion(ingredient[0]):
                                
                                ingredient_scaled = scale_dict(ingredient_recipe, ingredient[1])
                                full_recipe_list.append(sum_dict(ingredient_scaled, y))

                        full_recipe_list = [stuff for stuff in full_recipe_list if stuff not in old_full_recipe_list]   

                    else:
                        full_recipe_list = [{}]
                        break 

                if full_recipe_list != [{}]:
                    recipes_list.extend(full_recipe_list)

            return recipes_list
    
    return all_flat_recursion(food_item)
       
def sum_dict(dict_1, dict_2):
    '''
    Takes two dictionaries dict_1 and dict_2 and returns a new dictionary 
    where each key maps to the sum of the corresponding values in dict_1 and dict_2
    '''
    sum_dict = {}
    for key in dict_1.keys():
        if key in dict_2.keys():
            sum_dict[key] = dict_1[key] + dict_2[key]
        else:
            sum_dict[key] = dict_1[key]
    for key_2 in dict_2.keys():
        if key_2 not in dict_1.keys():
            sum_dict[key_2] = dict_2[key_2]
    
    return sum_dict

def scale_dict(dictionary, scale):
    '''
    Given a dictionary mapping atomic food items to quantities, returns a new dictionary 
    with the same keys but with all values scaled by some amount
    '''
    scale_dict = {}
    for key in dictionary.keys():
        scale_dict[key] = dictionary[key] * scale

    return scale_dict


if __name__ == "__main__":
    # you are free to add additional testing code here!
    pass