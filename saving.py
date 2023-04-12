import json
import hero


def save(field, players, current_player, cells_on_fire):
    with open('save.json', 'w') as f:
        json.dump([field, [player.__dict__ for player in players], current_player, cells_on_fire], f, default=lambda o: o.__dict__)


def load():
    with open('save.json', 'r') as f:
        data = json.load(f)
    field = data[0]
    players = [hero.Hero.from_json(player) for player in data[1]]
    current_player = data[2]
    cells_on_fire = data[3]
    return field, players, current_player, cells_on_fire
