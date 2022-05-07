import collections.abc
from exceptions import NoSuchDominoException


def contains_value(hand, value):
    for d in hand:
        if value in d:
            return True

    return False


class Hand(collections.abc.Sequence):
    def __init__(self, dominoes):
        self._dominoes = list(dominoes)

    def play(self, d):
        try:
            i = self._dominoes.index(d)
        except ValueError:
            raise NoSuchDominoException('Cannot make move -'
                                        ' {} is not in hand!'.format(d))

        self._dominoes.pop(i)
        return i

    def draw(self, d, i=None):
        if i is None:
            self._dominoes.append(d)
        else:
            self._dominoes.insert(i, d)

    def __getitem__(self, i):
        return self._dominoes[i]

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __len__(self):
        return len(self._dominoes)

    def __str__(self):
        return ''.join(str(d) for d in self._dominoes)

    def __repr__(self):
        return str(self)
