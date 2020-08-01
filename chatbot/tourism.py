# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'tourism' domain in
the atithi application
"""
import os
import json
from .root import app
from chatbot.middleware.firebaseHelper import firebaseHelper

firebase = firebaseHelper()

@app.handle(intent='start_tour')
def start_tour(request, responder):
    id = request.params.dynamic_resource['id']
    res = firebase.changeStatus(1,id)
    responder.params.target_dialogue_state = "select_tourism"
    responder.reply("What type of Adventure would you like to go on.\n1. Nature⛰\n2. Camping🏕\n3. Family👨‍👩‍👧‍👧")
    

@app.handle(intent='select_tourism')
def select_tourism(request, responder):
    tourism_type = request.entities[0]["text"]
    spot_list = _fetch_spot_from_kb(tourism_type.lower())
    for i in range(len(spot_list[1])):
        spot_list[1][i] = spot_list[1][i].lower()
    responder.frame["spot_list"] = spot_list[1]
    if len(spot_list[0]) > 1:
        responder.params.target_dialogue_state = "select_destination_from_choice"
        reply = "Here are some good options for " + tourism_type +" tourism: "+spot_list[0] + "Select the spot name to travel.~You can always ask a like 'Tell me about spot name' to know more😀"
    else:
        responder.params.target_dialogue_state = "select_tourism"
        reply = "Sorry..Could not understand.~Please try again😕" + "\nWhat type of Adventure would you like to go on.\n1. Nature\n2. Camping\n3. Family"
    responder.reply(reply)


@app.handle(intent = 'select_destination', has_entity='spot_name')
def select_destination_from_choice(request, responder):
    id = request.params.dynamic_resource['id']
    try:
        if request.entities[0]["text"] in responder.frame["spot_list"]:
            data = request.entities[0]["text"]

            res = firebase.setDest(data,id)
            lat, long = firebase.getCurrLocation(id)

            if lat and long:
                responder.params.allowed_intents = ('general.set_current_loc','tourism.set_source','tourism.resume')
                loc = firebase.getCurrLocationName(id)
                msg = "Your current location is "+loc['city']+" and is set as source.~Please tell us the source location or share the new source location if you want to change it, otherwise resume."
                responder.reply("Your destination has been set to:" + data + "\n\n"+msg+"~👍")

            else:
                
                responder.params.allowed_intents = ['general.set_current_loc','tourism.set_source']
                msg = "Please tell us the source location or share your location"
                responder.reply("Your destination has been set to:" + request.entities[0]["text"] + "\n"+msg+"~👍")
                # return

        elif request.entities[0]["text"]:
            data = request.entities[0]["text"]

            res = firebase.setDest(data,id)
            lat, long = firebase.getCurrLocation(id)

            if lat and long:
                responder.params.allowed_intents = ('general.set_current_loc','tourism.set_source','tourism.resume')
                loc = firebase.getCurrLocationName(id)
                msg = "Your current location is "+loc['city']+" and is set as source.\n\nPlease tell us the source location or share the new source location if you want to change it, otherwise resume."
                responder.reply("The selected adventure spot is not under the chosen class,😕~Continuing.....~Your destination has been set to:" + data + "\n\n"+msg)

            else:
                
                responder.params.allowed_intents = ['general.set_current_loc','tourism.set_source']
                msg = "Please tell us the source location or share the location"
                responder.reply("The selected adventure spot is not under the chosen class,😕~Continuing.....\nYour destination has been set to:" + request.entities[0]["text"] + "\n"+msg)

        else:
            responder.reply("Oops!😕...We don't find any such spot in our data.~Try some other spot.")
    except IndexError:
        responder.params.target_dialogue_state = "start_tour"
        responder.reply("Sorry😕~I didn't unnderstand, say 'start' to start planning of tour.")
    except KeyError:
        responder.params.target_dialogue_state = "start_tour"
        responder.reply("Sorry😕~I didn't unnderstand, say start to start planning of tour.")
    return

@app.handle(domain='tourism',intent='resume')
def resume(request,responder):
    responder.params.target_dialogue_state = 'food_pref'
    responder.reply("Before we personalize your journey, we would like to ask some preferences😀.\nPlease tell us any preferences about your food (veg/non-veg/italian/etc)")

@app.handle(domain='general', intent='set_curr_loc')
def set_curr_loc(request,responder):
    responder.params.target_dialogue_state = 'food_pref'
    responder.reply("Before we personalize your journey, we would like to ask some preferences😀.\nPlease tell us any preferences about your food (veg/non-veg/italian/etc)")

@app.handle(intent='set_source', has_entity='city_name')
def set_source(request, responder):
    data = request.entities[0]["text"]
    id = request.params.dynamic_resource['id']
    res = firebase.setSource(data,id)
    responder.params.target_dialogue_state = 'food_pref'
    # responder.params.allowed_intents = ['tourism.food_pref']
    responder.reply("Before we personalize your journey, we would like to ask some preferences😀.\nPlease tell us any preferences about your food (veg/non-veg/italian/etc)")

@app.handle(intent='food_pref', has_entity='cuisines')
def food_pref(request, responder):
    id = request.params.dynamic_resource['id']
    data=""
    for item in request.entities:
        data += item['value'][0]["cname"]+" "
    res = firebase.setFoodPref(data,id)
    responder.params.target_dialogue_state = 'hotel_pref'
    # responder.params.allowed_intents = ['tourism.hotel_pref']
    responder.reply("That's great😀!~Now do you have any preferences for hotels i.e Number of rooms ac/non-ac/etc.")

@app.handle(intent='hotel_pref')
def hotel_pref(request,responder):
    id = request.params.dynamic_resource['id']
    data={}
    for item in request.entities:
        data[item["type"]]=item["value"][0]["cname"]

    res = firebase.setHotelPref(data,id)
    responder.reply("Don't worry😀, I will take care of your comfort throughout the journey~I will remember these preferences along the journey.~Whenever You are hungry or want to have some rest you are free to ask for my help.~I will help you in searching restaurants and hotels😀")



def _fetch_city_from_kb(tourism_type):
    city = app.question_answerer.get(index='city_data')
    city_list = "\n"
    city_array = []
    j = 1
    for i in range(len(city)):
        if tourism_type in city[i]["tourism_type"]:
            city_list += str(j)+": "+city[i]["city_name"] + "\n"
            j = j+1
            city_array.append(city[i]["city_name"])
    return [city_list,city_array]


def _fetch_spot_from_kb(tourism_type):
    spot = app.question_answerer.get(index='spot_data',size=57)
    spot_list = "\n"
    spot_array = []
    j = 1
    for i in range(len(spot)):
        if tourism_type in spot[i]["type"]:
            spot_list += str(j)+": "+spot[i]["spot_name"] + "\n"
            j = j+1
            spot_array.append(spot[i]["spot_name"].lower())
    return [spot_list,spot_array]

def _fetch_all_spot_from_kb():
    spot = app.question_answerer.get(index='spot_data',size=57)
    spot_array = []
    for i in range(len(spot)):
        spot_array.append(spot[i]["spot_name"].lower())
    return [spot_array]
