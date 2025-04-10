import socketio
from fastapi import FastAPI
import uvicorn
from collections import defaultdict
from app.controller import GameController
from app.db.db_interface import initialize_db, close_db

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
sio_app = socketio.ASGIApp(sio, other_asgi_app=app)

game_controllers = defaultdict(lambda: GameController(None))

def check_locked_game(game_id):
    """
    Check if the game is locked.
    :param game_id: The id of the game to check.
    :return: True if the game is locked, False otherwise.
    """
    for game in game_controllers.values():
        if game.game_id == game_id:
            return True
    return False

def validate_point(data):
    """
    Validate the point.
    :param data: The data dictionary.
    :return: str: The error message if invalid, None if valid.
    """
    if "point" not in data:
        return "Point not provided."
    try:
        point = tuple(data["point"])
    except KeyError:
        return "Point is not a valid tuple."
    x, y = point
    if not isinstance(point, tuple) or len(point) != 2:
        return "Point must be a tuple of two integers."
    if  not isinstance(x, int) or not isinstance(y, int):
        return "Point coordinates must be integers."

def validate_name(data):
    """
    Validate the name.
    :param name: The data dictionary.
    :return: str: The error message if invalid, None if valid.
    """
    if "name" not in data:
        return "Name not provided."
    name = data["name"]
    if not isinstance(name, str):
        return "Name must be a string."
    if len(name)==0:
        return "Name must not be empty."
    

@sio.event
async def connect(sid, environ):
    game_controllers[sid] = GameController()

@sio.event
async def disconnect(sid):
    game_controllers.pop(sid)

@sio.event
async def new_game(sid, data):
    message = validate_name(data)
    if message:
        await sio.emit("error", {"message": message}, to=sid)
        return
    game_name = data["name"]
    board_actives_initial = set()
    if 'board_actives' in data:
        board_actives_initial = {tuple(item) for item in data["board_actives"]}
    game = game_controllers[sid].create_new_game(game_name=game_name, data=board_actives_initial)
    board_actives = game.get_current_state()
    await sio.emit("game_created", {"board_actives": list(board_actives)}, to=sid)

@sio.event
async def load_game(sid, data):
    game_id = data["game_id"]
    if check_locked_game(game_id):
        await sio.emit("game_locked", {"message": "Game is already in use."}, to=sid)
        return
    game_controller = game_controllers[sid]
    _ = game_controller.load_game_state(game_id)
    board_actives = game_controller.get_current_state()
    await sio.emit("game_loaded", {"board_actives": list(board_actives)}, to=sid)

@sio.event
async def get_all_games(sid, data):
    GameController = game_controllers[sid]
    games = GameController.get_all_games()
    await sio.emit("all_games_fetched", {"games": games}, to=sid)

@sio.event
async def toggle_point(sid, data):
    message = validate_point(data)
    if message:
        await sio.emit("error", {"message": message}, to=sid)
        return
    point = tuple(data["point"])
    game_controller = game_controllers[sid]
    state = game_controller.toggle_cell(point)
    board_actives = game_controller.get_current_state()
    await sio.emit("point_toggeled", {"state": state, "board_actives": list(board_actives)}, to=sid)

@sio.event
async def play_move(sid, data):
    game_controller = game_controllers[sid]
    _, _ = game_controller.make_move()
    board_actives = game_controller.get_current_state()
    await sio.emit("played_move", {"board_actives": list(board_actives)}, to=sid)

@sio.event
async def stop(sid, data):
    game_controller = game_controllers[sid]
    _ = game_controllers[sid].reset_game()
    board_actives = game_controller.get_current_state()
    await sio.emit("play_stopped", {"board_actives": list(board_actives)}, to=sid)


if __name__ == "__main__":
    initialize_db()
    uvicorn.run(sio_app, host="0.0.0.0", port=8000)
    close_db()
    