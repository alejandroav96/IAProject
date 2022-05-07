import collections
from exceptions import EmptyBoardException, EndsMismatchException

class Board:
    def __init__(self):
        self.board = collections.deque()

    def left_end(self):
        try:
            return self.board[0].first
        except IndexError:
            raise EmptyBoardException('Cannot retrieve the left end of'
                                      ' the board because it is empty!')

    def right_end(self):
        try:
            return self.board[-1].second
        except IndexError:
            raise EmptyBoardException('Cannot retrieve the right end of'
                                      ' the board because it is empty!')

    def _add_left(self, d):
        if not self:
            self.board.append(d)
        elif d.first == self.left_end():
            self.board.appendleft(d.inverted())
        elif d.second == self.left_end():
            self.board.appendleft(d)
        else:
            raise EndsMismatchException(
                '{} cannot be added to the left of'
                ' the board - values do not match!'.format(d)
            )

    def _add_right(self, d):
        if not self:
            self.board.append(d)
        elif d.first == self.right_end():
            self.board.append(d)
        elif d.second == self.right_end():
            self.board.append(d.inverted())
        else:
            raise EndsMismatchException(
                '{} cannot be added to the right of'
                ' the board - values do not match!'.format(d)
            )

    def add(self, d, left):
        if left:
            self._add_left(d)
        else:
            self._add_right(d)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __len__(self):
        return len(self.board)

    def __str__(self):
        return ''.join(str(d) for d in self.board)

    def __repr__(self):
        return str(self)
