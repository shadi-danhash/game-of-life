from app.game import GameBase
from app.db.db_interface import create_game, load_game, update_points, toggle_point, get_games

class GameController:
    def __init__(self):
        self.game = None
        self.game_id = None

    def create_new_game(self, game_name:str, data:set=None):
        '''
        Creates a new game with the given name and initial data.
        If data is provided, it initializes the game with that data.

        :param game_name: Name of the game.
        :param data: Initial data for the game (set of tuples).

        :return: GameBase instance representing the game.
        '''
        game_db = create_game(game_name)
        self.game = GameBase(state=set(data) if data else set())
        self.game_id = game_db.id
        if data:
            data = {f'{point[0]} {point[1]}' for point in data}
            update_points(game_id=self.game_id, active_points=data, dead_points=set())
        return self.game
            

    def load_game_state(self, game_id:int):
        '''
        Loads the game state from the database using the game ID.
        :param game_id: ID of the game to load.

        :return: GameBase instance representing the loaded game.
        '''
        game_data = load_game(game_id)
        game_data = {(int(x), int(y)) for x, y in (point.split() for point in game_data)}
        self.game = GameBase(state=game_data)
        self.game_id = game_id
        return self.game
    
    def reset_game(self):
        '''
        Resets the game to its initial state.
        :return: GameBase instance representing the reset game.
        '''
        return self.load_game_state(self.game_id)
        
    def toggle_cell(self, point:tuple, store:bool=True):
        '''
        Toggles the state of a cell at the given point.
        :param point: Tuple representing the coordinates of the cell (x, y).
        :param store: Boolean indicating whether to store the change in the database.
        :return: Boolean indicating the new state of the cell (True for active, False for dead).
        '''
        x, y = point
        point_str = f"{x} {y}"
        if store:
            toggle_point(game_id=self.game_id,point=point_str)
        new_value = self.game.toggle_point(point=point)
        return new_value

    def make_move(self, store:bool=False):
        '''
        Computes the next state of the game.
        :param store: Boolean indicating whether to store the changes in the database(Feature for later!).
        :return: Tuple containing sets of active and dead cells.
        '''

        active, dead = self.game.next()
        if store:
            # Since the active, dead represents only the new changes,
            # storing it will be more efficient
            raise NotImplementedError("Store functionality is not implemented yet.")
        return active, dead

    def get_current_state(self):
        '''
        Returns the current state of the game.
        :return: Set of tuples representing the active cells.
        '''
        return self.game.get_current_state()
    
    def get_all_games(self):
        '''
        Retrieves all games from the database.
        :return: List of dictionaries containing game IDs and names.
        '''
        games = get_games()
        return [{'id': game.id, 'name':game.name} for game in games]
