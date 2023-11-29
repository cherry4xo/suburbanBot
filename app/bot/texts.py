import json
from time import strftime, gmtime
from datetime import datetime


def welcome_text(name):
    text = f"Hello again, {name}! I'm telegram bot for checking suburban trains schedule!"
    return text


def first_join(name):
    text = f"I see you first time, {name}..."
    return text


def user_does_not_exist(id):
    text = f"User with {id} id does not exist in my database"
    return text


def get_route_text(start_station, finish_station):
    text = f"{start_station} --> {finish_station}"
    return text

def get_station_text(station, region):
    text = f"{station} ({region})"
    return text


def get_schedule(schedule):
    text = ""
    data = json.loads(schedule)
    for trip in data:
        text = text + f"*From* {trip['from']}\n*To* {trip['to']}\n*Departure time*: {datetime.fromisoformat(trip['departure_time']).time().strftime('%H:%M')}\n*Arrival time*: {datetime.fromisoformat(trip['arrival_time']).time().strftime('%H:%M')}\n*Duration*: {strftime('%H:%M', gmtime(trip['duration']))}\n"
        if trip["departure_platform"] != "":
            text = text + f"*Departure from* {trip['departure_platform']} platform\n"
        if trip["arrival_platform"] != "":
            text = text + f"*Departure from* {trip['arrival_platform']} platform\n"
        text = text + f"*Number of train*: {trip['number']}\n{trip['title']}\n{trip['train_subtype']}\n*Stops*: {trip['stops']}\n\n\n"

    return text


def add_route(start, finish):
    text = f"\n\nRoute {start} --> {finish} added"
    return text


pick_region = "Pick region"
search_start_station = "Type the title of start station"
search_finish_station = "Type the title of finish station"
favorite_routes_response = "Pick favorite route"
back_to_welcome_menu = "Back to start menu"
favorite_routes_button = "Favorite routes"
get_route_schedule = "Check schedule for new route"
cancel_search = "Cancel search"
choose_start_station = "Choose start station"
choose_finish_station = "Choose finish station"
cannot_get_schedule = "Cannot get schedule from API. Try again later"
add_route_to_favorites = "Add route to favorites"
back_to_favorites = "Back to favorites"
remove_from_favorites = "Remove route from favorites"
route_does_not_exist = "This route does not exist in the database"
route_delete_success = "Route deleted from favorites"
refresh_schedule = "Refresh schedule"