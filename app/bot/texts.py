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


pick_region = "Pick region"
search_start_station = "Type the title of start station"
search_finish_station = "Type the title of finish station"
favorite_routes_response = "Pick favorite route"
back_to_welcome_menu = "Back to start menu"
favorite_routes_button = "Favorite routes"
get_route_schedule = "Check schedule for new route"
