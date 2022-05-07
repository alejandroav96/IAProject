#! /usr/bin/env python

import subprocess
from players import random, omniscient
from series import Series
from exceptions import EndsMismatchException

PLAYER_SETTINGS = [
    ('Humano', None),
    ('AI: random', random),
    ('AI: omniscient', omniscient())
]


def validated_input(prompt, validate_and_transform, error_message):
    while True:
        user_input = input(prompt).strip()
        validated_user_input = validate_and_transform(user_input)

        if validated_user_input is not None:
            return validated_user_input

        print(error_message)


def validate_and_transform_target_score(target_score):
    try:
        target_score = int(target_score)
    except ValueError:
        return None

    if target_score <= 0:
        return None

    return target_score


def validate_and_transform_nonnegative_index(sequence):
    def _validate_and_transform_nonnegative_index(i):
        if i not in (str(j) for j in range(len(sequence))):
            return None

        return int(i)

    return _validate_and_transform_nonnegative_index


def validate_and_transform_end(end):
    end = end.lower()
    try:
        return {'l': True, 'r': False}[end]
    except KeyError:
        return None


input('¡Bienvenido!'
      ' presione enter para continuar')
subprocess.call(['tput', 'reset'])

target_score = validated_input('Hasta cuantos puntos te gustaría jugar:',
                               validate_and_transform_target_score,
                               'Introduzca un número entero positivo.')
series = Series(target_score=target_score)
game = series.games[0]

print('Configuración de los jugadores:')
for i, (name, _) in enumerate(PLAYER_SETTINGS):
    print('{}) {}'.format(i, name))

player_settings = []
valid_inputs = list(range(len(PLAYER_SETTINGS)))
for player in range(len(game.hands)):
    player_settings.append(
        PLAYER_SETTINGS[
            validated_input('Seleccione la configuración para el jugador {}: '.format(player),
                            validate_and_transform_nonnegative_index(
                                PLAYER_SETTINGS),
                            'Por favor seleccione un valor entre: {}'.format(valid_inputs))
        ]
    )

while game is not None:
    input('Presione enter para iniciar el juego {}.'.format(len(series.games) - 1))
    subprocess.call(['tput', 'reset'])

    if len(series.games) == 1:
        print('El jugador {} tenía el [6|6] e hizo el primer movimiento.'.format(
            game.starting_player))

    while game.result is None:
        print('Tablero:')
        print(game.board)
        for player, hand in enumerate(game.hands):
            print('El jugador {} tiene {} fichas de dominó en su mano.'.format(
                player, len(hand)))

        input("Ahora es el turno del jugador {}. Presione enter"
              " para continuar.".format(game.turn))
        subprocess.call(['tput', 'reset'])

        print('Tablero:')
        print(game.board)
        turn = game.turn

        player_setting_name, player_setting = player_settings[game.turn]

        if player_setting is None:
            print("Mano del jugador {}:".format(game.turn))
            hand = game.hands[game.turn]
            for i, d in enumerate(hand):
                print('{}) {}'.format(i, d))

            while True:
                valid_inputs = list(range(len(hand)))
                d = hand[validated_input('Elige a qué dominó te gustaría jugar:',
                                         validate_and_transform_nonnegative_index(
                                             hand),
                                         'Por favor ingrese un valor en: {}'.format(valid_inputs))]

                if game.board:
                    end = validated_input('Elija en qué extremo del tablero'
                                          ' me gustaría jugar en (l o r):',
                                          validate_and_transform_end,
                                          'Introduzca un valor en: [l, r]')
                else:
                    end = True

                try:
                    game.make_move(d, end)
                    break
                except EndsMismatchException:
                    print('El dominó seleccionado no se puede jugar en el'
                          ' extremo seleccionado del tablero. Inténtalo de nuevo.')
        else:
            player_setting(game)

            print('El jugador {} ({}) eligió jugar {} en el extremo {} del tablero.'.format(
                game.turn,
                player_setting_name,
                game.valid_moves[0][0],
                'left' if game.valid_moves[0][1] else 'right'
            ))
            game.make_move(*game.valid_moves[0])

        input("Presione enter para finalizar el turno del jugador {}.".format(turn))
        subprocess.call(['tput', 'reset'])

    print('Fin del juego!')
    print(game)

    game = series.next_game()
    print('El estado actual de la serie:')
    print(series)

winning_team, _ = max(enumerate(series.scores), key=lambda i_score: i_score[1])
print('Equipo {} ganador!'.format(winning_team))
