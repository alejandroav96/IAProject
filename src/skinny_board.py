from exceptions import EmptyBoardException, EndsMismatchException
from domino import Domino


class SkinnyBoard:
    def __init__(self, left=None, right=None, length=0):
        self._left = left
        self._right = right
        self._length = length

    @classmethod
    def from_board(cls, board):
        if len(board):
            left = board.left_end()
            right = board.right_end()
        else:
            left = None
            right = None

        return cls(left, right, len(board))

    def left_end(self):
        if not self:
            raise EmptyBoardException('Cannot retrieve the left end of'
                                      ' the board because it is empty!')

        return self._left

    def right_end(self):
        if not self:
            raise EmptyBoardException('Cannot retrieve the right end of'
                                      ' the board because it is empty!')

        return self._right

    def _add_left(self, d):
        if not self:
            self._left = d.first
            self._right = d.second
        elif d.second == self.left_end():
            self._left = d.first
        elif d.first == self.left_end():
            self._left = d.second
        else:
            raise EndsMismatchException(
                '{} cannot be added to the left of'
                ' the board - values do not match!'.format(d)
            )

        self._length += 1

    def _add_right(self, d):
        if not self:
            self._left = d.first
            self._right = d.second
        elif d.first == self.right_end():
            self._right = d.second
        elif d.second == self.right_end():
            self._right = d.first
        else:
            raise EndsMismatchException(
                '{} cannot be added to the right of'
                ' the board - values do not match!'.format(d)
            )

        self._length += 1

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
        return self._length

    def __str__(self):
        if not self:
            return ''
        elif self._length == 1:
            return str(Domino(self._left, self._right))
        else:
            left_domino = Domino(self._left, '?')
            right_domino = Domino('?', self._right)
            middle_dominoes = [Domino('?', '?')] * (self._length - 2)
            all_dominoes = [left_domino] + middle_dominoes + [right_domino]
            return ''.join(str(d) for d in all_dominoes)

    def __repr__(self):
        return str(self)
