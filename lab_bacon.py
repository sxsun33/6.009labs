#!/usr/bin/env python3

import pickle

# NO ADDITIONAL IMPORTS ALLOWED!


def transform_data(raw_data):

    transformed_without_film = {}
    transformed_with_film = {}
    for data in raw_data:
        if data[0] == data[1]:
            continue
        else:
            if data[2] not in transformed_with_film.keys():
                transformed_with_film[data[2]]= {data[0], data[1]}
            else:
                transformed_with_film[data[2]].add(data[0])
                transformed_with_film[data[2]].add(data[1])

            if data[0] not in transformed_without_film.keys():
                transformed_without_film[data[0]] = set()
                transformed_without_film[data[0]].add(data[1])
                
            if data[1] not in transformed_without_film.keys():
                transformed_without_film[data[1]] = set()
                transformed_without_film[data[1]].add(data[0])
            
            transformed_without_film[data[0]].add(data[1])
            transformed_without_film[data[1]].add(data[0])

    return (transformed_without_film, transformed_with_film)


def acted_together(transformed_data, actor_id_1, actor_id_2):
    if actor_id_1 == actor_id_2:
        return True
    else: 
        actor_dict = transformed_data[0]
        if actor_id_2 in actor_dict[actor_id_1]:
            return True
        else:
            return False         

def actors_with_bacon_number(transformed_data, n):
    actor_dict = transformed_data[0]
    
    if n == 0: return {4724}
    
    else:
        if n > len([i for i in actor_dict.keys()]): return set()

        actors_set_complete = {4724} #list of actors that have bacon number < n
        actors_set_current = {4724} #list of actors with current bacon number of the loop

        for bacon_num in range(n):

            actors_set_current_loop = {i for i in actors_set_current}

            for actor_id in actors_set_current_loop:

                for id in actor_dict[actor_id]:
                        
                    if id not in actors_set_complete:
                        actors_set_current.add(id)
                        actors_set_complete.add(id)
                        
                actors_set_current.remove(actor_id)   

        return actors_set_current
    #find all the actors that have a bacon number of 1, then find all the actors that have acted with those bacon = 1 but not in bacon = 1 actor list, and so on


def bacon_path(transformed_data, actor_id):
    return actor_to_actor_path(transformed_data, 4724, actor_id)

def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    return actor_path(transformed_data, actor_id_1, lambda x : x == actor_id_2)

def actor_path(transformed_data, actor_id_1, goal_test_function):
    if goal_test_function(actor_id_1):
        return [actor_id_1]
    queue = [(actor_id_1,[actor_id_1])]
    examined = set()
    data = transformed_data[0]

    while len(queue)>0:
        actor, path = queue.pop(0)
        examined.add(actor)
        for child in data[actor]:
            if goal_test_function(child):
                return path + [child]
            else:
                if child not in examined:
                    examined.add(child)
                    queue.append((child, path + [child]))
    return None

def actors_connecting_films(transformed_data, film1, film2):
    length_of_previous_path = float('inf')
    for actor in transformed_data[1][film1]: 
        
        if len(actor_path(transformed_data, actor, lambda p: p in transformed_data[1][film2])) < length_of_previous_path:
            path = actor_path(transformed_data, actor, lambda p: p in transformed_data[1][film2])
            length_of_previous_path = len(path)
    
    return path


'''
    actor_dict = transformed_data[0]
    actors_set = {i for i in actor_dict.keys()}
    if actor_id_2 == actor_id_1:
        return [actor_id_1]
    elif actor_id_1 not in actors_set or actor_id_2 not in actors_set:
        return None
    else:
        actor_parent = {actor_id_1}
        actor_parent_dict = {}
        
        while actor_id_2 not in actor_parent:
           
            actor_parent_loop = {i for i in actor_parent}

            for parent in actor_parent_loop:

                for actor in actor_dict[parent]:

                    if actor not in actor_parent_dict.keys():
                        actor_parent_dict[actor] = parent
                        actor_parent.add(actor)

                    if actor == actor_id_2:
                        break    

                actor_parent.remove(parent) 

        current_parent = actor_id_2
        path = [actor_id_2]
        #movie_path = []
        
        while current_parent != actor_id_1:
            path = [actor_parent_dict[current_parent]] + path

            #movie_path = list(transformed_data[1][(current_parent, actor_parent_dict[current_parent])]) + movie_path

            current_parent = actor_parent_dict[current_parent]
    
        return path #, movie_path'''

if __name__ == "__main__":
    with open("resources/names.pickle", "rb") as f:
        names = pickle.load(f)
    actor_id = names['Aznil Hj Nawawi']
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    names_flipped = {}
    for name, id in names.items():
         names_flipped[id] = name

    with open("resources/movies.pickle", "rb") as g:
        movies = pickle.load(g)

    movies_flipped = {}
    for movie, id_ in movies.items():
         movies_flipped[id_] = movie

    with open("resources/large.pickle", "rb") as h:
        tinydb = pickle.load(h)
        transformed_data = transform_data(tinydb)
    actor_id_1 = names['Ellen Page']
    actor_id_2 = names['Sven Batinic']

    path = actor_to_actor_path(transformed_data, actor_id_1, actor_id_2)[1]
    # ids = actors_with_bacon_number(transformed_data, 6) Lew Cody to Tom Hulce
    movie_path = []

    for movie in path:
        movie_path.append(movies_flipped[movie])
    
    print(movie_path)

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    #print(acted_together(transformed_data, actor_id_1, actor_id_2))
