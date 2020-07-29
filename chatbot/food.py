"""This module contains the dialogue states for the 'food' domain in
the atithi application
"""

import os
import json
from .root import app
from chatbot.middleware.firebaseHelper import firebaseHelper
from chatbot.middleware.restaurantHelper import getRestaurant

firebase = firebaseHelper()

@app.handle(intent='start_flow_food')
def start_flow_food(request, responder):
    # responder.params.target_dialogue_state = "hotel.set_current_loc"
<<<<<<< HEAD
    responder.params.allowed_intents = ['general.set_current_loc','food.search_nearby_food','food.search_food_at_dest']
    responder.reply("Sure, please tell me where you are or just share your location if you want to search restaurants nearby you")
=======
    id = request.params.dynamic_resource['id']
    res = firebase.getHotelPref(id)
    
    if not res:
        responder.params.allowed_intents = ('tourism.food_pref')
        responder.reply("Sure, please first tell us the preferences for the (veg/non-veg/italian/etc)")
    else:
        responder.params.allowed_intents = ('general.set_current_loc','food.search_nearby_food','food.search_food_at_dest')
        responder.reply("Sure, please tell us the the destination name or just share your location if you want to search restaurants nearby you")
>>>>>>> 62ce12b976bd5b19d7663cbe5a897f7d0ecac529

@app.handle(domain='food', intent='search_nearby_food')
def search_nearby_food(request,responder):
    print('f')
    id = request.params.dynamic_resource['id']
<<<<<<< HEAD

    try:
        lat,long = firebase.getCurrLocation(id)
        if lat and long:
            # hotel_msg = hotelList(id,lat,long)
            # print(hotel_msg)
            print('d')
            responder.reply("Yay ..I found some restaurants nearby you🌮\nGo and enjoy some yummy local food there😋:\n")
    except (TypeError,AttributeError):
        print('g')
        responder.params.target_dialogue_state = "search_food_at_curr"
        responder.reply('I know you are hungry. But can you please share your location first so that I can help you in finding restaurants nearby you...🙂')
=======
    res = firebase.getHotelPref(id)
    
    if not res:
        responder.params.allowed_intents = ('tourism.food_pref')
        responder.reply("Sure, please first tell us the preferences for the (veg/non-veg/italian/etc)")
    else:
        try:
            lat,long = firebase.getCurrLocation(id)
            if lat and long:
                res_msg = getRestaurant(id,lat,long)
                responder.reply("here is the list of restaurants nearby you:\n\n"+res_msg)
        except (TypeError,AttributeError):
            print('g')
            responder.params.target_dialogue_state = "search_food_at_curr"
            responder.reply('Please share your location')
>>>>>>> 62ce12b976bd5b19d7663cbe5a897f7d0ecac529


@app.handle(domain='general',intent='set_current_loc')
def search_food_at_curr(request, responder):

    # code for getting nearest_city for the loc
    id = request.params.dynamic_resource['id']
    lat,long = firebase.getCurrLocation(id)
    # end

<<<<<<< HEAD
    # code for getting hotels list
    # hotel_msg = hotelList(id,lat,long)
    # print(hotel_msg)
    responder.reply("Yummy food is waiting for you😋! I found some restaurants at your current location:\n")
=======
    res_msg = getRestaurant(id,lat,long)
    responder.reply("here is the list of restaurants at your current location:\n\n"+res_msg)
>>>>>>> 62ce12b976bd5b19d7663cbe5a897f7d0ecac529


@app.handle(domain='hotel',intent='search_food_at_dest', has_entity='spot_name')
def search_at_dest(request, responder):
    spot_name = request.entities[0]["value"][0]["cname"]
    id = request.params.dynamic_resource['id']
    lat,long = _fetch_spot_from_kb(spot_name)
<<<<<<< HEAD
    print(lat,long)
    # hotel_msg = hotelList(id,lat,long)
    # print(hotel_msg)
    responder.reply("There are some restaurants at your destination😋:\n")
    
=======
    if not res:
        responder.params.allowed_intents = ('tourism.food_pref')
        responder.reply("Sure, please first tell us the preferences for the (veg/non-veg/italian/etc)")
    else:
        res_msg = getRestaurant(id,lat,long)
        # print(hotel_msg)
        responder.reply("here is the list of restaurants at your destination\n\n"+res_msg)
    
>>>>>>> 62ce12b976bd5b19d7663cbe5a897f7d0ecac529
