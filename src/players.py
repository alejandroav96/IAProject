import collections
import copy
import random as rand
from search import alphabeta


def identity(game):
    return


class counter:
    def __init__(self, player=identity, name=None):
        self.count = 0
        self._player = player
        if name is None:
            self.__name__ = type(self).__name__
        else:
            self.__name__ = name

    def __call__(self, game):
        self.count += 1
        return self._player(game)


def random(game):
    game.valid_moves = tuple(
        sorted(game.valid_moves, key=lambda _: rand.random()))


def reverse(game):
    game.valid_moves = tuple(reversed(game.valid_moves))


def bota_gorda(game):
    game.valid_moves = tuple(
        sorted(game.valid_moves, key=lambda m: -(m[0].first + m[0].second)))


def double(game):
    game.valid_moves = tuple(
        sorted(game.valid_moves, key=lambda m: m[0].first != m[0].second))


class omniscient:
    def __init__(self, start_move=0, player=identity, name=None):
        self._start_move = start_move
        self._player = player
        if name is None:
            self.__name__ = type(self).__name__
        else:
            self.__name__ = name

    def __call__(self, game):
        if len(game.moves) < self._start_move or len(game.valid_moves) == 1:
            return
        game_copy = copy.deepcopy(game)
        game_copy.skinny_board()
        moves, _ = alphabeta(game_copy, player=self._player)
        game.valid_moves = (
            moves[0],) + tuple(m for m in game.valid_moves if m != moves[0])


class probabilistic_alphabeta:
    def __init__(self, start_move=0, sample_size=float('inf'), player=identity, name=None):
        self._start_move = start_move
        self._sample_size = sample_size
        self._player = player
        if name is None:
            self.__name__ = type(self).__name__
        else:
            self.__name__ = name

    def __call__(self, game):
        if len(game.moves) < self._start_move or len(game.valid_moves) == 1:
            return

        if self._sample_size == float('inf'):
            hands = game.all_possible_hands()
        else:
            hands = (game.random_possible_hands()
                     for _ in range(self._sample_size))

        counter = collections.Counter()
        for h in hands:
            game_copy = copy.deepcopy(game)
            game_copy.hands = h
            game_copy.skinny_board()
            counter.update([
                alphabeta(game_copy, player=self._player)[0][0]
            ])
        game.valid_moves = tuple(
            sorted(game.valid_moves, key=lambda m: -counter[m]))
