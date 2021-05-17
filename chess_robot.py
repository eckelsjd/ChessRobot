import serial
import time

class ChessRobot:
    def __init__(self,play_as):
        # Connect to Arduino over serial COM6 with baud = 9600
        self.play_as_color = play_as # or 'W'
        self.controller = serial.Serial('/dev/ttyACM0',9600)
        self.controller.flush()

        if (play_as == 'B'):
            self.capture_file = '@' # ASCII 64
            self.capture_rank = 9
        elif (play_as == 'W'):
            self.capture_file = 'I' # ASCII 73
            self.capture_rank = 0

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

    def capture(self,start,dest,captured_piece):
        self.toggle_enable()
        self.send_command(f'GO {dest}')
        self.send_command('pickup')

        if (self.play_as_color == 'B'):

            if (captured_piece == 'Q'):
                # Queen
                capture_square = f'A{self.capture_rank}'

            elif (captured_piece == 'B'):
                # Bishop
                capture_file = 'B' if (self.get_num_of('B') == 2) else 'C'
                capture_square = f'{capture_file}{self.capture_rank}'

            elif (captured_piece == 'K'):
                # Knight
                capture_file = 'D' if (self.get_num_of('K') == 2) else 'E'
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

            elif (captured_piece == 'K'):
                # Knight
                capture_file = 'E' if (self.get_num_of('K') == 2) else 'D'
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


    # return the number of enemy pieces remaining on the board of a certain type
    def get_num_of(self,piece):
        if (piece == 'P'):
            # GET FROM FEN notation: Pawn
            return 8
        else:
            return 2

    def close(self):
        self.controller.close()