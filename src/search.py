import copy
import operator

def identity(game):
    return

def make_moves(game, player=identity):
    if game.result is not None:
        return
    player(game)
    for move in game.valid_moves[:-1]:
        new_game = copy.deepcopy(game)
        new_game.make_move(*move)
        yield move, new_game
    move = game.valid_moves[-1]
    game.make_move(*move)
    yield move, game


def alphabeta(game, alpha_beta=(-float('inf'), float('inf')),
              player=identity):
    if game.result is not None:
        return [], game.result.points

    if game.turn % 2:
        # minimizando
        best_value = float('inf')
        op = operator.lt
        def update(ab, v): return (ab[0], min(ab[1], v))
    else:
        # maximizando
        best_value = -float('inf')
        op = operator.gt
        def update(ab, v): return (max(ab[0], v), ab[1])

    # recursividad
    for move, new_game in make_moves(game, player):
        moves, value = alphabeta(new_game, alpha_beta, player)
        if op(value, best_value):
            best_value = value
            best_moves = moves
            best_moves.insert(0, move)
            alpha_beta = update(alpha_beta, best_value)
            if alpha_beta[1] <= alpha_beta[0]:
                # alpha-beta apagado
                break

    return best_moves, best_value
