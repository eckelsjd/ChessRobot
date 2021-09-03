import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button 
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.properties import StringProperty,ListProperty,ObjectProperty

import chess
import chess.engine
import chess_robot

import string

# Class to maintain chess board, control robot/camera, hold chess engine
class EnginePlayer():
    def __init__(self):
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish") # TODO: fix hard code of engine
        self.robot = chess_robot.ChessRobot('B')
        # self.robot.set_play_as()
    
    def chesscell_clicked(self,id):
        print(f'Id = {id}')
        is_legal_move = True
        return is_legal_move

    def kill_yourself(self):
        # shutdown serial and reset game board
        self.board.reset()
        # self.robot.close()
        # if (self.engine is not None):
        #     self.engine.quit() 

    def move(self):
        best_move = self.engine.play(self.board, chess.engine.Limit(depth=10)).move
        # robot make the move here
        uci = best_move.uci()
        first_square = uci[0:2].upper()
        second_square = uci[2:4].upper()

        capture = self.board.is_capture(best_move)
        kingside = self.board.is_kingside_castling(best_move)
        queenside = self.board.is_queenside_castling(best_move)
        en_passant = self.board.is_en_passant(best_move)

        if (capture):
            captured_piece = self.board.piece_at(chess.parse_square(second_square.lower())).symbol()
            self.robot.set_fen(self.board.fen())
            self.robot.capture(first_square,second_square,captured_piece)

        elif (kingside):
            self.robot.kingside()

        elif (queenside):
            self.robot.queenside()

        elif (en_passant):
            self.robot.en_passant()

        else:
            # normal move
            self.robot.move(first_square,second_square)
        
        return best_move

class ChessCell(Button):
    pass

class MainScreen(Screen):
    pass

class PlayEngineScreen(Screen):
    chessboard = ObjectProperty(None) # create reference to chessboard widget

    def __init__(self,**kwargs):
        super(PlayEngineScreen,self).__init__(**kwargs)
        self.chesscell_ids = {}
        image_dir = 'data/images/chess-pieces/'
        self.piece_image_dict = {'p': image_dir + 'BlackPawn.png',
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
        self.selected_square = None
        self.engine_player = None
        
    def initialize_chessboard(self):
        # Open chess engine
        self.engine_player = EnginePlayer()

        white_color = [216/255, 209/255, 191/255, 1]
        black_color = [0/255, 111/255, 68/255, 1]
        # create chessboard
        for num in range(64):
            # ids start from top left corner -> bottom right corner
            if (num % 8 == 0):
                row = num // 8 # row 0 is first
                if (row % 2 == 0):
                    switch_color = True # start even rows on white
                else:
                    switch_color = False # start odd rows on black

            curr_color = white_color if switch_color else black_color
            switch_color = not switch_color
            chess_cell = ChessCell()
            chess_cell.id = str(num)
            chess_cell.background_color = curr_color
            self.chessboard.add_widget(chess_cell)

        self.chesscell_ids = {child.id: child for child in self.chessboard.children}
        self.update_positions()

    def chesscell_clicked(self,id):
        # is_legal_move = self.engine_player.chesscell_clicked(id)

        if id == self.selected_square:
            self.update_positions()
            was_move_made = False
        elif self.selected_square == None:
            self.select_piece(id)
            was_move_made = False
        else:
            was_move_made = self.move_piece(id)

        return was_move_made
    
    def select_piece(self, id):
        square_num = self.id_to_square(id)
        square_san = self.id_to_san(id)
        piece = self.engine_player.board.piece_at(square_num)

        legal_move_dict = self.create_legal_move_dict()
        
        if square_san in legal_move_dict:
            id_list = []
            for move in legal_move_dict[square_san]:
                id_list.append(self.san_to_id(move))
            self.highlight_chesscell(id_list)
        self.selected_square = id
    
    def move_piece(self, id):
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

            self.engine_player.board.push(move)
            self.update_positions()
            self.selected_square = None
            was_move_made = True

            # if not self.game_end_check():
            #     Clock.schedule_once(self.start_engine_move)

        else:
            self.update_positions()
            self.select_piece(id)
            was_move_made = False
        
        return was_move_made
    
    def id_to_square(self, id):
        id = int(id)
        row = abs(id//8 - 8)
        column = id % 8
        return (row-1) * 8 + column

    def id_to_san(self, id):
        id = int(id)
        row = abs(id//8 - 8)
        column = list(string.ascii_lowercase)[id % 8]
        return column + str(row)

    def san_to_id(self, san):
        column = san[0]
        row = int(san[1])
        id_row = 64 - (row * 8)
        id_column = list(string.ascii_lowercase).index(column)
        id = id_row + id_column
        return id

    # TODO: shape this up
    def create_legal_move_dict(self):
        legal_moves = list(self.engine_player.board.legal_moves)
        legal_move_dict = {}
        for move in legal_moves:
            move = str(move)
            if move[:2] in legal_move_dict:
                legal_move_dict[move[:2]] = \
                    legal_move_dict[move[:2]] + [move[2:]]
            else:
                legal_move_dict[move[:2]] = [move[2:]]

        return legal_move_dict

    def highlight_chesscell(self, id_list):
        self.update_positions()
        highlight_image = 'data/images/other/highlight.png'
        for id in id_list:
            self.chesscell_ids[str(id)].children[0].source = highlight_image

    def update_positions(self):
        # Get the board positions from the fen
        b = self.engine_player.board.fen().split()[0].replace('/', '')
        # Replace empty spaces with dots
        for num in range(1, 10):
            b = b.replace(str(num), '.'*num)

        # Map Chess cell ids to board positions and set images
        for x in zip(range(64), list(b)): 
            if x[1] != '.':
                image = self.piece_image_dict[x[1]]
            else:
                image = 'data/images/other/transparency.png'
            self.chesscell_ids[str(x[0])].children[0].source = image

    def engine_move(self):
        best_move = self.engine_player.move()
        self.engine_player.board.push(best_move)
        self.update_positions()
        return
    
    def close(self):
        self.chessboard.clear_widgets()
        if self.engine_player is not None:
            self.engine_player.kill_yourself()
        
class ChessbotApp(App):

    score = StringProperty('Score: +0.00 cp') # TODO:Update this automatically
    bg_color = ListProperty([177/255,154/255,122/255,1]) # khaki brown
    curr_play_color = ListProperty([102/255,255/255,0/255,0.7]) # bright green
    black_play_color = ListProperty([177/255,154/255,122/255,1])
    white_play_color = ListProperty([177/255,154/255,122/255,1])
    game_moves_string = StringProperty('1) e4 e5 2) N4...') # TODO: Update this automatically

    def __init__(self,**kwargs):
        super(ChessbotApp, self).__init__(**kwargs)
        self.play_engine_screen = None
        
    def build(self):
        # Dimensions of Raspberry Pi 7" touchscreen: 800x480
        Config.set('graphics','width','795')
        Config.set('graphics','height','445')
        Config.set('graphics','position','custom')
        Config.set('graphics','left',0)
        Config.set('graphics','top',0)
        Config.set('graphics', 'resizable', '1')
        Config.write()

        # Return a screenmanager as the root of the app
        manager = ScreenManager()
        manager.transition = SwapTransition()
        return  manager
    
    def close(self):
        if self.play_engine_screen is not None:
            self.play_engine_screen.close()
        App.get_running_app().stop()
        print("Exiting...")
    
    # set up to play against engine on play_engine screen
    def handle_play_engine(self):
        self.root.current = 'play_engine' # self.root is the screen manager
        self.play_engine_screen = self.root.ids.play_engine
        self.play_engine_screen.initialize_chessboard()
        
        # TODO: fix this hardcode
        self.white_play_color = self.curr_play_color
        self.black_play_color = self.bg_color

    def quit_game(self):
        # return to main menu
        self.root.current = 'main' 

        # delete chessboard and engine player
        self.play_engine_screen.close()
    
    def turn(self):
        if (self.white_play_color == self.curr_play_color):
            return 'w'
        else:
            return 'b'
        
    def handle_chesscell_clicked(self,id):

        if self.turn() == 'w':
            move_was_made = self.play_engine_screen.chesscell_clicked(id)

            # change indication of whose move it is
            if (move_was_made):
                if(self.turn() == 'w'):
                    self.white_play_color = self.bg_color
                    self.black_play_color = self.curr_play_color
                else:
                    self.white_play_color = self.curr_play_color
                    self.black_play_color = self.bg_color
                
                # Start engine move
                self.play_engine_screen.engine_move()

                # Engine is done when this returns; update turn display
                self.white_play_color = self.curr_play_color
                self.black_play_color = self.bg_color

        else:
            pass # ignore input when it is engine's turn


if __name__ == '__main__':
    ChessbotApp().run()