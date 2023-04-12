import copy
from field import field


class Position:
    def __init__(self, x=None, y=None, default=True):
        if default:
            self.x = 0
            self.y = 0
            for i in range(len(field)):
                start_is_found = False
                for j in range(len(field[0])):
                    if field[i][j][1] == 'S':
                        self.x = j
                        self.y = i
                        start_is_found = True
                        break
                if start_is_found:
                    break
        else:
            self.x = x
            self.y = y

    def __eq__(self, other):
        return other and self.x == other.x and self.y == other.y

    def __str__(self):
        return f'({self.x}, {self.y})'


class Hero:

    def __init__(self):
        self.name = 'Player'
        self.pos = Position()
        self.last_pos = copy.copy(self.pos)
        self.penultimate_pos = None

        self.bandages = 3
        self.xp = 5

        self.have_key = False
        self.is_scared = False

    def set_name(self, name):
        self.name = name

    def got_hit(self):
        self.xp -= 1

    def heal(self):
        self.bandages -= 1
        self.xp += 1

    def can_heal(self):
        return self.bandages > 0

    def pick_up_key(self):
        field[self.pos.y][self.pos.x][1] = '-'
        self.have_key = True

    def can_pick_up_key(self):
        return field[self.pos.y][self.pos.x][1] == 'K'

    def move(self, direction):
        if not self.is_on_orange():
            self.penultimate_pos = copy.copy(self.last_pos)
            self.last_pos = copy.copy(self.pos)
        if direction == 'U':
            self.pos.y -= 1
        elif direction == 'R':
            self.pos.x += 1
        elif direction == 'D':
            self.pos.y += 1
        elif direction == 'L':
            self.pos.x -= 1
        if self.is_on_heart():
            if self.xp < 5:
                self.xp = 5
        if not self.is_on_orange():
            if self.pos == self.penultimate_pos:
                self.is_scared = True
        else:
            self.last_pos = copy.copy(self.penultimate_pos)
            self.penultimate_pos = None

    def can_move(self, direction):
        if direction == 'U' and self.pos.y > 0:
            return field[self.pos.y-1][self.pos.x][1] != '#'
        if direction == 'R' and self.pos.x + 1 < len(field[0]):
            return field[self.pos.y][self.pos.x+1][1] != '#'
        if direction == 'D' and self.pos.y + 1 < len(field):
            return field[self.pos.y+1][self.pos.x][1] != '#'
        if direction == 'L' and self.pos.x > 0:
            return field[self.pos.y][self.pos.x-1][1] != '#'
        return False

    def is_on_fire(self):
        return field[self.pos.y][self.pos.x][0] == 'F'

    def is_on_heart(self):
        return field[self.pos.y][self.pos.x][1] == 'H'

    def is_on_key(self):
        return field[self.pos.y][self.pos.x][1] == 'K'

    def is_on_finish(self):
        return field[self.pos.y][self.pos.x][1] == 'F'

    def is_on_orange(self):
        return field[self.pos.y][self.pos.x][0] == 'O'

    def is_dead(self):
        return self.xp <= 0

    def will(self):
        if self.have_key:
            field[self.pos.y][self.pos.x][1] = 'K'

    @staticmethod
    def from_json(data):
        player = Hero()
        player.name = data['name']
        if data['pos'] is None:
            player.pos = None
        else:
            player.pos = Position(**data['pos'], default=False)
        if data['last_pos'] is None:
            player.last_pos = None
        else:
            player.last_pos = Position(**data['last_pos'], default=False)
        if data['penultimate_pos'] is None:
            player.last_pos = None
        else:
            player.last_pos = Position(**data['penultimate_pos'], default=False)
        player.bandages = data['bandages']
        player.xp = data['xp']
        player.have_key = data['have_key']
        player.is_scared = data['is_scared']
        return player
