from app.db.models import db, Game, Point

def initialize_db():
    db.connect()
    db.create_tables([Game, Point])

def create_game(game_name: str):
    game = Game.create(name=game_name)    
    return game

def get_games():
    games = Game.select()
    return games

def load_game(game_id: int):
    points = Point.select().where(Point.game == game_id)
    return [f"{point.point}" for point in points]

def toggle_point(game_id: int, point: str):
    try:
        point_record = Point.get(Point.game == game_id, Point.point == point)
        point_record.delete_instance()
        return False  # Point was removed
    except Point.DoesNotExist:
        Point.create(game=game_id, point=point)
        return True  # Point was added


def update_points(game_id: int, active_points:list[str], dead_points:list[str]):
    for point in dead_points:
        Point.delete().where(Point.game == game_id, Point.point == point).execute()

    for point in active_points:
        Point.create(game=game_id, point=point)
    
def close_db():
    if not db.is_closed():
        db.close()
    