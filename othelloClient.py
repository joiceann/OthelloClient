import socketio as socket
import random
import math
import copy

# REFERENCIA
# http://dhconnelly.com/paip-python/docs/paip/othello.html#section-14
# https://inventwithpython.com/chapter15.html



socketIO = socket.Client()
url='localhost:4000'
userName = 'joiceann'
tournament_id = '12'
N: int = 8


def validarMovimientos(board, jugadorID, x, y):
    global N
    index = x * N + y
    voltear = []
    index_voltear = []
    around = [ [1, -1], [0, -1], [0, 1], [1, 1], [1, 0],  [-1, 0], [-1, -1],[-1, 1]]

    if board[index] != 0 or not posicion_valida(x, y):
        return False, voltear, None
    testboard = copy.deepcopy(board)
    testboard[index] = jugadorID

    oponent_turn_id = 1
    if jugadorID == 1:
        oponent_turn_id = 2


    for xtemp, ytemp in around:
        i, j = x, y
        i += xtemp
        j += ytemp

        if posicion_valida(i, j) and testboard[i*8+j] == oponent_turn_id:
            i += xtemp
            j += ytemp
            if not posicion_valida(i, j):
                continue
            while testboard[i*8+j] == oponent_turn_id:
                i += xtemp
                j += ytemp

                if not posicion_valida(i, j):
                    break
            if not posicion_valida(i, j):
                continue
            if testboard[i*8+j] == jugadorID:
                while True:
                    i -= xtemp
                    j -= ytemp

                    if i == x and j == y:
                        break
                    voltear.append([i, j])

    if len(voltear) > 0:
        for i in voltear:
            index = i[0] * N + i[1]
            testboard[index] = jugadorID
            index_voltear.append(index)
        return True, index_voltear, testboard
    else:
        return False, index_voltear,testboard

def movimientos(board, playerTurnID):
    posiblesmov = []
    resultado = []
    for x in range(8):
        for y in range(8):
            valido, voltear, new_board = validarMovimientos(board, playerTurnID, x, y)
            if valido:
                resultado.append(new_board)
                posiblesmov.append(x * 8 + y)
    return posiblesmov, resultado


#verifica que la posicion se encuentre dentro del arreglo
def posicion_valida(x, y):
    if -1 < x < 8 and -1 < y < 8:
        return True
    else:
        return False

#Tomada de protocolo Samuel
def human_board(board):
    global N
    tileRep = ['_', 'X', 'O']
    result = '    A  B  C  D  E  F  G  H'
    for i in range(len(board)):
        if i % N == 0:
            result += '\n\n ' + str(int(math.floor(i / N)) + 1) + ' '
        result += ' ' + tileRep[board[i]] + ' '
    return result

#toamada protocolo Samuel
def ix(row, col):
    return row * 8 + col
#------------------------CLIENTESOCKET----------------------------------------------
@socketIO.on('connect')
def on_connect():
    print('Conectado')
    socketIO.emit('signin', {
        'user_name': userName,
        'tournament_id': tournament_id,
        'user_role': 'player'
     })


@socketIO.on('ready')
def on_ready(data):
    jugada = movimientos(data['board'], data['player_turn_id'])
    la_juagada = jugada[0][random.randint(0, len(jugada[0])-1)]
    print(human_board(data['board']))
    print("\nRequesting move...")
    socketIO.emit('play', {
        "player_turn_id":data['player_turn_id'],
        "tournament_id":tournament_id,
        "game_id":data['game_id'],
        "movement": la_juagada
    })


@socketIO.on('finish')
def on_finish(data):
    print("Juego terminado")

    socketIO.emit('player_ready', {
        "tournament_id":tournament_id,
        "game_id":data['game_id'],
        "player_turn_id":data['player_turn_id']
    })

socketIO.connect('http://localhost:4000')
