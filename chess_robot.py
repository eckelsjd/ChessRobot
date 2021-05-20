import serial
import time

class ChessRobot:
    def __init__(self,play_as):
        # Connect to Arduino over serial COM6 with baud = 9600
        self.play_as_color = play_as # or 'W'
        self.fen = '' # FEN game notation for current position

        # self.controller = serial.Serial('/dev/ttyACM0',9600)
        self.controller = serial.Serial('COM6',9600)
        self.controller.flush()

        if (play_as == 'B'):
            self.capture_file = '@' # ASCII 64
            self.capture_rank = 9
        elif (play_as == 'W'):
            self.capture_file = 'I' # ASCII 73
            self.capture_rank = 0

    # Send blocking call to Arduino
    def send_command(self,cmd):
        # self.controller.write(bytes(f'{cmd}\n','utf-8'))
        self.controller.write(bytes(f'{cmd}\n','utf-8'))
        time.sleep(0.05)
        line = self.controller.readline().decode('utf-8').rstrip() # block until response
        print(line)

    def toggle_enable(self):
        self.send_command('ENABLE')

    def set_play_as(self):
        # play as 'W' for white or 'B' for black
        self.send_command(f'PLAYAS {self.play_as_color}')

    def set_fen(self,current_fen):
        self.fen = current_fen

    def home(self):
        self.toggle_enable()
        self.send_command('HOME')
        self.toggle_enable()

    def move(self,start,dest):
        self.toggle_enable()
        self.send_command(f'GO {start}')
        self.send_command('pickup')
        self.send_command(f'GO {dest}')
        self.send_command('putdown')
        self.toggle_enable()

    def kingside(self):
        if (self.play_as_color == 'B'): # black kingside
            self.move('E8','G8') # move king first
            self.move('H8','F8') # move rook
        else: # white kingside
            self.move('E1','G1')
            self.move('H1','F1')

    def queenside(self):
        if (self.play_as_color == 'B'): # black queenside
            self.move('E8','C8') # move king first
            self.move('A8','D8')
        else: # white queenside
            self.move('E1','C1')
            self.move('A1','D1')

    def capture(self,start,dest,captured_piece):
        self.toggle_enable()
        self.send_command(f'GO {dest}')
        self.send_command('pickup')
        captured_piece = captured_piece.upper()

        if (self.play_as_color == 'B'):

            if (captured_piece == 'Q'):
                # Queen
                capture_square = f'A{self.capture_rank}'

            elif (captured_piece == 'B'):
                # Bishop
                capture_file = 'B' if (self.get_num_of('B') == 2) else 'C'
                capture_square = f'{capture_file}{self.capture_rank}'

            elif (captured_piece == 'N'):
                # Knight
                capture_file = 'D' if (self.get_num_of('N') == 2) else 'E'
                capture_square = f'{capture_file}{self.capture_rank}'

            elif (captured_piece == 'R'):
                # Rook
                capture_file = 'F' if (self.get_num_of('R') == 2) else 'G'
                capture_square = f'{capture_file}{self.capture_rank}'

            elif (captured_piece == 'P'):
                # Pawn
                capture_rank = self.get_num_of('P')
                capture_square = f'{self.capture_file}{capture_rank}'

        elif (self.play_as_color == 'W'):

            if (captured_piece == 'Q'):
                # Queen
                capture_square = f'H{self.capture_rank}'

            elif (captured_piece == 'B'):
                # Bishop
                capture_file = 'G' if (self.get_num_of('B') == 2) else 'F'
                capture_square = f'{capture_file}{self.capture_rank}'

            elif (captured_piece == 'N'):
                # Knight
                capture_file = 'E' if (self.get_num_of('N') == 2) else 'D'
                capture_square = f'{capture_file}{self.capture_rank}'

            elif (captured_piece == 'R'):
                # Rook
                capture_file = 'C' if (self.get_num_of('R') == 2) else 'B'
                capture_square = f'{capture_file}{self.capture_rank}'

            elif (captured_piece == 'P'):
                # Pawn
                capture_rank = 9 - self.get_num_of('P')
                capture_square = f'{self.capture_file}{capture_rank}'

        self.send_command(f'GO {capture_square}')
        self.send_command('putdown')
        self.send_command(f'GO {start}')
        self.send_command('pickup')
        self.send_command(f'GO {dest}')
        self.send_command('putdown')
        self.toggle_enable()

    def en_passant(self):
        pass

    # return the number of enemy pieces remaining on the board of a certain type
    def get_num_of(self,piece):
        if (self.play_as_color == 'B'):
            piece = piece.upper() # look for captured white pieces (capital in FEN)
        else:
            piece = piece.lower() # look for captured black pieces
        
        positions = self.fen.split()[0]
        return positions.count(piece)

    def close(self):
        self.controller.close()