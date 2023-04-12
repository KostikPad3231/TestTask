import logging
from hero import Hero
from field import field
import random
import saving
import os.path

movement_keys = {
    'w': 'U',
    'a': 'L',
    's': 'D',
    'd': 'R'
}
action_keys = ('f', 'v', 'q', 'z', 'p')


class Game:

    def __init__(self):
        self.logger = logging.getLogger('game')
        # format_ = '%(asctime)s - %(message)s'
        format_ = '%(message)s'
        self.logger.setLevel('INFO')
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(format_))
        sh.setLevel('INFO')
        self.logger.addHandler(sh)

        open_save = False
        file_exists = os.path.exists('save.json')
        if file_exists:
            ans = input('There is a save of the last game. Do you want to download it? (y/n): ')
            while ans not in ('y', 'n'):
                ans = input('There is a save of the last game. Do you want to download it? (y/n): ')
            if ans == 'y':
                open_save = True
            else:
                os.remove('save.json')
        if open_save:
            current_player, cells_on_fire = self.open_save()
            self.main_loop(current_player, cells_on_fire)
        else:
            self.player_count = int(input('Enter the number of players: '))
            self.players = [Hero() for _ in range(self.player_count)]
            self.start()
            self.main_loop()

    def open_save(self):
        saved_field, players, current_player, cells_on_fire = saving.load()
        for i in range(len(field)):
            field[i] = saved_field[i]
        self.players = players
        return current_player, cells_on_fire

    def start(self):

        for i in range(self.player_count):
            while True:
                name = input(f'Enter name of {i + 1} player: ')
                is_unique = True
                for j in range(i - 1):
                    if name == self.players[j].name:
                        is_unique = False
                        break
                if is_unique:
                    break
                else:
                    print('You should enter unique name!')
            self.players[i].set_name(name)

        self.print_actions()

    def main_loop(self, current_player=0, cells_on_fire=None):
        game_is_over = False
        while not game_is_over and len(self.players) != 0:
            if cells_on_fire is None:
                cells_on_fire = self.generate_fire()
            self.logger.info(f'Cells with fire at these coordinates: {cells_on_fire}')
            for i in range(current_player, len(self.players)):
                current_player = 0
                player = self.players[i]
                if player.is_dead():
                    self.remove_player_if_is_dead(player)
                    continue

                action = self.next_action(player)

                if action == 'z':
                    game_is_over = True
                    break

                if action == 'p':
                    saving.save(field, self.players, i, cells_on_fire)
                    game_is_over = True
                    break

                if action in movement_keys:
                    if player.can_move(movement_keys[action]):
                        player.move(movement_keys[action])

                        if not player.is_scared:
                            self.logger.info(f'{player.name} moved, '
                                             f'direction: {movement_keys[action]}, '
                                             f'current position: {player.pos}, '
                                             f'here are players: '
                                             f'{" ".join([p.name for p in self.get_other_players(player)])}, '
                                             f'got healing: {player.is_on_heart()}, '
                                             f'is in a cell with a key: {player.is_on_key()}')
                            if player.is_on_finish() and player.have_key:
                                game_is_over = True
                                self.logger.info(f'Hero {player.name} won!')
                                break
                            elif player.is_on_finish() and not player.have_key:
                                self.logger.info(f'Hero {player.name} reached the finish line without a key and lost')
                                self.players.remove(player)
                                continue
                            self.burn_player_if_is_on_fire(player)
                        else:
                            player.will()
                            self.logger.info(f'Hero {player.name} got scared and lost')
                            self.players.remove(player)
                            continue
                    else:
                        player.got_hit()
                        self.logger.info(f'Hero {player.name} hit the wall and lost 1xp, '
                                         f'has {player.xp}xp')
                        continue
                elif action == 'f':
                    self.burn_player_if_is_on_fire(player)

                    player.pick_up_key()
                    self.logger.info(f'{player.name} picked up the key')
                elif action == 'v':
                    self.burn_player_if_is_on_fire(player)

                    self.logger.info(f'{player.name} hit')
                    for other_player in self.get_other_players(player):
                        other_player.got_hit()
                        self.logger.info(f'{other_player.name} got hit, '
                                         f'has {other_player.xp}xp')
                elif action == 'q' and player.can_heal():
                    player.heal()
                    self.logger.info(f'{player.name} used bandage, '
                                     f'has {player.xp}xp')

                self.remove_player_if_is_dead(player)
        self.logger.info('Thank you for the play!')

    def remove_player_if_is_dead(self, player):
        if player.is_dead():
            player.will()
            self.logger.info(f'{player.name} died, {player.name} loses')
            self.players.remove(player)

    def burn_player_if_is_on_fire(self, player):
        if player.is_on_fire():
            player.got_hit()
            self.logger.info(f'Hero {player.name} burned out and lost 1xp, '
                             f'has {player.xp}xp')

    def get_other_players(self, player):
        return [other_player for other_player in self.players
                if player.pos.x == other_player.pos.x and player.pos.y == other_player.pos.y
                and player.name != other_player.name]

    def generate_fire(self):
        for y in range(len(field)):
            for x in range(len(field[0])):
                if field[y][x][0] == 'F':
                    field[y][x][0] = ''
        cell_candidates = tuple((y, x) for y in range(len(field)) for x in range(len(field[0]))
                                if (field[y][x][1] == '-' or field[y][x][1] == 'K') and field[y][x][0] == '')
        cells = random.sample(cell_candidates, k=4)
        for y, x in cells:
            field[y][x][0] = 'F'
        return cells

    def print_actions(self):
        self.logger.info('Movement is controlled by these keys:')
        self.logger.info('w - to move up, a - to move to the left, s - to move down, d - to move to the right, '
                         'f - to raise the heart, v - to strike, q - to use bandage, '
                         f'p - to save, z - completely turn off the game for everyone')

    def next_action(self, player):
        self.logger.info(f'{player.name}\'s turn: ')
        action = input()
        generate_action = False
        if action == 'q' and not player.can_heal():
            self.logger.info(f'{player.name} has no bandages')
            generate_action = True
        elif action == 'f' and not player.is_on_key():
            self.logger.info('There is no key in this cell')
            generate_action = True
        while action not in movement_keys and action not in action_keys or generate_action:
            generate_action = False
            self.print_actions()
            self.logger.info(f'{player.name}\'s turn: ')
            action = input()
            if action == 'q' and not player.can_heal():
                self.logger.info(f'{player.name} has no bandages')
                generate_action = True
            elif action == 'f' and not player.is_on_key():
                self.logger.info('There is no key in this cell')
                generate_action = True
        return action


game = Game()
