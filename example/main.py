from kivy.app import App
from kivy.core.window import Window

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button 
from kivy.uix.textinput import TextInput

from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.clock import Clock

from kivy.config import Config

import chess
import chess.engine

from functools import partial
import threading
import os
import string

board = chess.Board()
# engine = chess.engine.SimpleEngine.popen_uci("stockfish.exe") # Windows
engine = chess.engine.SimpleEngine.popen_uci("stockfish") # Linux

data_dir = 'data/'
image_dir = data_dir + 'images/'
cp_images = image_dir + 'chess-pieces/'
other_images = image_dir + 'other/'

class Chessboard(GridLayout):
    def gen_image_dict(self, *args, image_dir=cp_images):
        if image_dir[-1] != '/':
            image_dir += '/'
        d = {'p': image_dir + 'BlackPawn.png',
                'r': image_dir + 'BlackRook.png',
                'n': image_dir + 'BlackKnight.png',
                'b': image_dir + 'BlackBishop.png',
                'q': image_dir + 'BlackQueen.png',
                'k': image_dir + 'BlackKing.png',
                'P': image_dir + 'WhitePawn.png',
                'R': image_dir + 'WhiteRook.png',
                'N': image_dir + 'WhiteKnight.png',
                'B': image_dir + 'WhiteBishop.png',
                'Q': image_dir + 'WhiteQueen.png',
                'K': image_dir + 'WhiteKing.png',
            }
        return d
 
    def update_positions(self, *args):
        # Can't call ids directly for some reason so ...
        # Dictionary mapping ids to children (Chess cells)
        ids = {child.id: child for child in self.children}

        # Get the board positions from the fen
        b = board.fen().split()[0].replace('/', '')
        # Replace empty spaces with dots
        for num in range(1, 10):
            b = b.replace(str(num), '.'*num)

        # Generate dictionary that maps pieces to images
        image_dict = self.gen_image_dict()

        # Map Chess cell ids to board positions and set images
        for x in zip(range(64), list(b)): 
            if x[1] != '.':
                image = image_dict[x[1]]
            else:
                image = other_images + 'transparency.png'
            ids[str(x[0])].children[0].source = image
            
    def highlight_chesscell(self, id_list, *args):
        self.update_positions()
        ids = {child.id: child for child in self.children}
        highlight_image = other_images + 'highlight.png'
        for id in id_list:
            ids[str(id)].children[0].source = highlight_image
          
    def on_size(self, *args):
        board_dimensions = sorted([self.width, self.height])[0]

        self.row_force_default = True
        self.col_force_default = True

        self.row_default_height = board_dimensions/self.rows
        self.col_default_width = board_dimensions/self.columns

    def button_down(self, id, *args):
        ids = {child.id: child for child in self.children}

        background_down = 'atlas://data/images/defaulttheme/button_pressed'
        ids[id].background_normal =  background_down

    def button_up(self, id, *args):
        ids = {child.id: child for child in self.children}

        background_normal = 'atlas://data/images/defaulttheme/button'
        ids[id].background_normal =  background_normal
        
    def press_button(self, id, *args, is_engine_move=False, engine_move=''):
        id = str(id)
        self.button_down(id)

        if is_engine_move == False:
            Clock.schedule_once(partial(self.button_up, id), .7)
        else:
            Clock.schedule_once(partial(self.button_up, id), .3)
            board.push(engine_move)
            Clock.schedule_once(self.update_positions)

    def engine_move(self, move, *args):
        ids = {child.id: child for child in self.children}
        starter_pos = move[0] 
        current_pos = move[1]

        self.press_button(starter_pos)

# class ChessboardCentered(BoxLayout):
#     def on_size(self, *args):
#         board_dimensions = sorted([self.width, self.height])[0]
#         self.padding = [(self.width-board_dimensions)/2, 
#             (self.height-board_dimensions)/2, 0, 0]

class ChessCell(Button):
    pass

class Sidebar(FloatLayout):
    pass

class ChessClockContainer(BoxLayout):
    pass

class BlackChessClock(BoxLayout):
    pass

class ChessClockDisplay(TextInput):
    pass

class ChessClockButton(Button):
    pass

class ExitButton(Button):
    def callback(self):
        App.get_running_app().stop()
        print("Exiting...")

class WhiteChessClock(BoxLayout):
    pass

class Movebox(BoxLayout):
    pass

class ChessGame(BoxLayout):
    selected_square = None

    movebox_moves = 'This is a move'

    black_time = StringProperty()
    white_time = StringProperty()
    time_interval = 0.5

    def __init__(self,**kwargs):
        super(ChessGame, self).__init__(**kwargs)

    def id_to_square(self, id, *args):
        id = int(id)
        row = abs(id//8 - 8)
        column = id % 8
        return (row-1) * 8 + column

    def id_to_san(self, id, *args):
        id = int(id)
        row = abs(id//8 - 8)
        column = list(string.ascii_lowercase)[id % 8]
        return column + str(row)

    def san_to_id(self, san, *args):
        column = san[0]
        row = int(san[1])
        id_row = 64 - (row * 8)
        id_column = list(string.ascii_lowercase).index(column)
        id = id_row + id_column
        return id

    def create_legal_move_dict(self, *args):
        legal_moves = list(board.legal_moves)
        legal_move_dict = {}
        for move in legal_moves:
            move = str(move)
            if move[:2] in legal_move_dict:
                legal_move_dict[move[:2]] = \
                    legal_move_dict[move[:2]] + [move[2:]]
            else:
                legal_move_dict[move[:2]] = [move[2:]]

        return legal_move_dict

    def draw_board(self, *args):
        c_board = None
        for child in self.children:
            # if type(child) == ChessboardCentered:
            if type(child) == Chessboard:
                c_board = child.children[0]
    
       	for num in range(64):
		# button = ChessCell(id=str(num))
            button = ChessCell()
            button.id = str(num)
            c_board.add_widget(button)
			
    def update_board(self, *args):
        self.ids.board.update_positions(board)

    def select_piece(self, id, *args):
        square_num = self.id_to_square(id)
        square_san = self.id_to_san(id)
        piece = board.piece_at(square_num)

        legal_move_dict = self.create_legal_move_dict()
        
        if square_san in legal_move_dict:
            id_list = []
            for move in legal_move_dict[square_san]:
                id_list.append(self.san_to_id(move))
            self.ids.board.highlight_chesscell(id_list)
        self.selected_square = id

    def move_piece(self, id, *args):
        legal_move_dict = self.create_legal_move_dict()
        legal_ids = []
        try:
            for san in legal_move_dict[\
                self.id_to_san(self.selected_square)]:
                legal_ids.append(self.san_to_id(san))
        except KeyError:
            pass
        
        if int(id) in legal_ids:
            original_square = self.id_to_san(self.selected_square)
            current_square = self.id_to_san(id)
            move = chess.Move.from_uci(original_square + current_square)

            board.push(move)
            self.update_board()
            self.selected_square = None

            try:
                self.white_time_counter(cancel=True)
            except NameError:
                pass

            if not self.game_end_check():
                Clock.schedule_once(self.start_engine_move)

        else:
            self.update_board()
            self.select_piece(id)

    def start_engine_move(self, *args):
        wtime = float(self.white_time) * 1000
        btime = float(self.black_time) * 1000
        threading.Thread(target=self.engine_move, \
            kwargs={'wtime': wtime, 'btime': btime}).start()

    def engine_move(self, *args, wtime=60*100, btime=60*100):
        self.black_time_counter(start=True, time=self.black_time)

        # engine.isready()
        # engine.position(board)
        # engine_move = engine.go(wtime=wtime, btime=btime)[0]
        engine_move = engine.play(board, chess.engine.Limit(depth=10)).move
        str_move = str(engine_move)
        move = [self.san_to_id(x) for x in [str_move[:2], str_move[2:]]]

        self.ids.board.press_button(move[0])
        self.select_piece(move[0])
        Clock.schedule_once(partial(self.ids.board.press_button,
            move[1], is_engine_move=True, engine_move=engine_move), 1)

        Clock.schedule_once(partial(self.black_time_counter, cancel=True),1)


        Clock.schedule_once(self.game_end_check, 1)
        
        Clock.schedule_once(partial(self.white_time_counter, \
            start=True, \
            time=self.white_time), 1)

    # def setup_engine(self, *args):
    #     # engine.uci()
    #     pass

    def turn(self, *args):
        return str(board.fen).split()[5]
 
    def chesscell_clicked(self, id, *args):
        print(f'ID: {id}')
        if self.turn() == 'w':

            if id == self.selected_square:
                self.update_board()
            elif self.selected_square == None:
                self.select_piece(id)
            else:
                self.move_piece(id)

    def white_time_counter(self, *args, start=False, time=50, cancel=False):
        if start:
            self.white_time = str(time)
            global w_counter
            w_counter = Clock.schedule_interval(self.white_time_counter,
                self.interval)
        elif cancel:
            w_counter.cancel()
        else:
            self.white_time = str(round(float(self.white_time) \
                - self.interval, 2))

    def black_time_counter(self, *args, start=False, time=50, cancel=False):
        if start:
            self.black_time = str(time)
            global b_counter
            b_counter = Clock.schedule_interval(self.black_time_counter,
                self.interval)
        elif cancel:
            b_counter.cancel()
        else:
            self.black_time = str(round(float(self.black_time) \
                - self.interval, 2))

    def setup_clocks(self, *args, time=60, interval=0.1):
        self.black_time = str(time)
        self.white_time = str(time)
        self.interval = interval

    def end_game(self, reason, *args):
        Clock.schedule_once(partial(self.white_time_counter, cancel=True), 1)
        Clock.schedule_once(partial(self.black_time_counter, cancel=True), 1)

        print(reason)
        if 'white' in reason:
            print('Black won')
        elif 'black' in reason:
            print('White won')
        else:
            if board.result()[-1] == '1':
                print('Black won')
            elif board.result()[0] == '1':
                print('White won')
            else:
                print('Draw')

    def game_end_check(self, *args):
        if board.is_game_over():
            if board.is_checkmate():
                self.end_game('checkmate')
            elif board.is_stalemate():
                self.end_game('stalemate')
            elif board.is_insufficient_material():
                self.end_game('insufficient_material')
            elif board.is_seventy_five_moves():
                self.end_game('seventy five moves')
            elif board.is_fivefold_repetition():
                self.end_game('fivefold_repetition')
            return True

        elif float(self.white_time) < 0:
            self.end_game('white ran out of time')
            return True
        elif float(self.black_time) < 0:
            self.end_game('black ran out of time')
            return True

        return False

class ChessboardApp(App):
    def build(self):
        game = ChessGame()
        game.draw_board()
        game.update_board(board)
        # game.setup_engine()
        game.setup_clocks(time=60, interval=.01)

        # Window.size = (1046, 718)

        # Dimensions of Raspberry Pi 7" touchscreen: 800x480
        Config.set('graphics','width','795')
        Config.set('graphics','height','445')
        Config.set('graphics','position','custom')
        Config.set('graphics','left',0)
        Config.set('graphics','top',0)
        Config.set('graphics', 'resizable', '1')
        Config.write()
        return game

if __name__ == '__main__':
   ChessboardApp().run()
   engine.quit()
