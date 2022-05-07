import copy
from domino import Domino
from board import Board
from hand import Hand, contains_value
from result import Result
from exceptions import NoSuchPlayerException, NoSuchDominoException, GameOverException, EndsMismatchException
from skinny_board import SkinnyBoard
import itertools
import random


def _randomized_hands():
    all_dominoes = [Domino(i, j) for i in range(7) for j in range(i, 7)]
    random.shuffle(all_dominoes)
    return [Hand(all_dominoes[0:7]), Hand(all_dominoes[7:14]),
            Hand(all_dominoes[14:21]), Hand(all_dominoes[21:28])]


def _validate_player(player):
    valid_players = range(4)
    if player not in valid_players:
        valid_players = ', '.join(str(p) for p in valid_players)
        raise NoSuchPlayerException('{} is not a valid player. Valid players'
                                    ' are: {}'.format(player, valid_players))


def _domino_hand(d, hands):
    for i, hand in enumerate(hands):
        if d in hand:
            return i

    raise NoSuchDominoException('{} is not in any hand!'.format(d))


def _remaining_points(hands):
    points = []
    for hand in hands:
        points.append(sum(d.first + d.second for d in hand))

    return points


def _validate_hands(hands, missing):
    for h, m in zip(hands, missing):
        for value in m:
            if contains_value(h, value):
                return False
    return True


def _all_possible_partitionings(elements, sizes):
    try:
        size = sizes[0]
    except IndexError:
        yield ()
        return
    sizes = sizes[1:]

    for partition in itertools.combinations(elements, size):
        for other_partitions in _all_possible_partitionings(elements.difference(partition), sizes):
            yield (partition,) + other_partitions


def next_player(player):
    return (player + 1) % 4


class Game:
    def __init__(self, board, hands, moves, turn,
                 valid_moves, starting_player, result):
        self.board = board
        self.hands = hands
        self.moves = moves
        self.turn = turn
        self.valid_moves = valid_moves
        self.starting_player = starting_player
        self.result = result

    @classmethod
    def new(cls, starting_domino=None, starting_player=0):
        board = Board()

        hands = _randomized_hands()

        moves = []

        result = None

        if starting_domino is None:
            _validate_player(starting_player)
            valid_moves = tuple((d, True) for d in hands[starting_player])
            game = cls(board, hands, moves, starting_player,
                       valid_moves, starting_player, result)
        else:
            starting_player = _domino_hand(starting_domino, hands)
            valid_moves = ((starting_domino, True),)
            game = cls(board, hands, moves, starting_player,
                       valid_moves, starting_player, result)
            game.make_move(*valid_moves[0])

        return game

    def skinny_board(self):
        self.board = SkinnyBoard.from_board(self.board)

    def _update_valid_moves(self):
        left_end = self.board.left_end()
        right_end = self.board.right_end()

        moves = []
        for d in self.hands[self.turn]:
            if left_end in d:
                moves.append((d, True))
            if right_end in d and left_end != right_end:
                moves.append((d, False))

        self.valid_moves = tuple(moves)

    def make_move(self, d, left):
        if self.result is not None:
            raise GameOverException(
                'Cannot make a move - the game is over!')

        i = self.hands[self.turn].play(d)

        try:
            self.board.add(d, left)
        except EndsMismatchException as error:
            self.hands[self.turn].draw(d, i)
            raise error

        self.moves.append((d, left))

        if not self.hands[self.turn]:
            self.valid_moves = ()
            self.result = Result(
                self.turn, True, pow(-1, self.turn) *
                sum(_remaining_points(self.hands))
            )
            return self.result

        passes = []
        stuck = True
        for _ in self.hands:
            self.turn = next_player(self.turn)
            self._update_valid_moves()
            if self.valid_moves:
                self.moves.extend(passes)
                stuck = False
                break
            else:
                passes.append(None)

        if stuck:
            player_points = _remaining_points(self.hands)
            team_points = [player_points[0] + player_points[2],
                           player_points[1] + player_points[3]]

            if team_points[0] < team_points[1]:
                self.result = Result(
                    self.turn, False, sum(team_points))
            elif team_points[0] == team_points[1]:
                self.result = Result(self.turn, False, 0)
            else:
                self.result = Result(
                    self.turn, False, -sum(team_points))

            return self.result

    def missing_values(self):
        missing = [set() for _ in self.hands]

        board = SkinnyBoard()
        player = self.starting_player
        for move in self.moves:
            if move is None:
                missing[player].update([board.left_end(), board.right_end()])
            else:
                board.add(*move)
            player = next_player(player)
        return missing

    def random_possible_hands(self):
        missing = self.missing_values()
        other_dominoes = [d for p, h in enumerate(
            self.hands) for d in h if p != self.turn]

        while True:
            shuffled_dominoes = (d for d in random.sample(
                other_dominoes, len(other_dominoes)))
            hands = []
            for player, hand in enumerate(self.hands):
                if player != self.turn:
                    hand = [next(shuffled_dominoes) for _ in hand]
                hands.append(Hand(hand))
            if _validate_hands(hands, missing):
                return hands

    def all_possible_hands(self):
        missing = self.missing_values()
        other_dominoes = {d for p, h in enumerate(
            self.hands) for d in h if p != self.turn}
        other_hand_lengths = [len(h) for p, h in enumerate(
            self.hands) if p != self.turn]
        for possible_hands in _all_possible_partitionings(other_dominoes, other_hand_lengths):
            possible_hands = (h for h in possible_hands)
            hands = []
            for player, hand in enumerate(self.hands):
                if player != self.turn:
                    hand = next(possible_hands)
                hands.append(Hand(hand))
            if _validate_hands(hands, missing):
                yield hands

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __deepcopy__(self, _):
        if isinstance(self.board, SkinnyBoard):
            if self.board:
                board = SkinnyBoard(self.board.left_end(),
                                             self.board.right_end(),
                                             len(self.board))
            else:
                board = SkinnyBoard()
        else:
            board = copy.deepcopy(self.board)
        hands = [Hand(hand) for hand in self.hands]
        moves = list(self.moves)
        valid_moves = self.valid_moves
        result = self.result
        turn = self.turn
        starting_player = self.starting_player
        return type(self)(board, hands, moves, turn,
                          valid_moves, starting_player, result)

    def __str__(self):
        string_list = ['Board: {}'.format(self.board)]

        for i, hand in enumerate(self.hands):
            string_list.append("Player {}'s hand: {}".format(i, hand))

        if self.result is None:
            string_list.append("Player {}'s turn".format(self.turn))
        else:
            if self.result.won:
                string_list.append(
                    'Player {} won and scored {} points!'.format(self.result.player,
                                                                 abs(self.result.points))
                )
            else:
                if not self.result.points:
                    string_list.append(
                        'Player {} stuck the game and tied (0 points)!'.format(
                            self.result.player)
                    )
                elif pow(-1, self.result.player) * self.result.points > 0:
                    string_list.append(
                        'Player {} stuck the game and scored {} points!'.format(self.result.player,
                                                                                abs(self.result.points))
                    )
                else:
                    string_list.append(
                        'Player {} stuck the game and scored'
                        ' {} points for the opposing team!'.format(self.result.player,
                                                                   abs(self.result.points))
                    )

        return '\n'.join(string_list)

    def __repr__(self):
        return str(self)
