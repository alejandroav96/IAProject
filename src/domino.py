import collections

# utilizando el estandar singleton
DominoBase = collections.namedtuple('DominoBase', ['first', 'second'])

class Domino(DominoBase):
    def inverted(self):
        return Domino(self.second, self.first)

    def __str__(self):
        return '[{}|{}]'.format(self.first, self.second)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return sorted((self.first, self.second)) == \
            sorted((other.first, other.second))

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(tuple(sorted((self.first, self.second))))

    def __contains__(self, key):
        return key == self.first or key == self.second
