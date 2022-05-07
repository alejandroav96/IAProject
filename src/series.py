from domino import Domino
from game import Game, next_player
from exceptions import SeriesOverException, GameInProgressException
class Series:
    def __init__(self, target_score=200, starting_domino=None):
        if starting_domino is None:
            starting_domino = Domino(6, 6)

        self.games = [Game.new(starting_domino=starting_domino)]
        self.scores = [0, 0]
        self.target_score = target_score

    def is_over(self):
        return max(self.scores) >= self.target_score

    def next_game(self):
        if self.is_over():
            raise SeriesOverException(
                'Cannot start a new game - series ended with a score of {} to {}'.format(*self.scores)
            )

        result = self.games[-1].result
        if result is None:
            raise GameInProgressException(
                'Cannot start a new game - the latest one has not finished!'
            )
        if result.points >= 0:
            self.scores[0] += result.points
        else:
            self.scores[1] -= result.points
        if self.is_over():
            return
        if result.won or pow(-1, result.player) * result.points > 0:
            starting_player = result.player
        elif not result.points:
            starting_player = self.games[-1].starting_player
        else:
            starting_player = next_player(result.player)
        self.games.append(Game.new(starting_player=starting_player))
        return self.games[-1]

    def __str__(self):
        string_list = ['Series to {} points:'.format(self.target_score)]
        for i, score in enumerate(self.scores):
            string_list.append('Team {} has {} points.'.format(i, score))

        return '\n'.join(string_list)

    def __repr__(self):
        return str(self)