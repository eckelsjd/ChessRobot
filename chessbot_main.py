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

# Class to maintain chess board, control robot/camera, hold chess engine
class EnginePlayer():
    def __init__(self):
        self.board = chess.Board()
        # self.engine = chess.engine.SimpleEngine.popen_uci("stockfish") # TODO: fix hard code of engine
        self.robot = ''
    
    def chesscell_clicked(self,id):
        print(f'Id = {id}')
        is_legal_move = True
        return is_legal_move

    def kill_yourself(self):
        # shutdown serial and close game board
        pass

class ChessCell(Button):
    pass

class MainScreen(Screen):
    pass

class PlayEngineScreen(Screen):
    chessboard = ObjectProperty(None) # create reference to chessboard widget

    def __init__(self,**kwargs):
        super(PlayEngineScreen,self).__init__(**kwargs)
        self.chesscell_ids = {}
        self.engine_player = EnginePlayer()
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
        
    def initialize_chessboard(self):
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
        is_legal_move = self.engine_player.chesscell_clicked(id)

        return is_legal_move

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
    
    def close(self):
        self.chessboard.clear_widgets()
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
            is_legal_move = self.play_engine_screen.chesscell_clicked(id)

            if id == self.selected_square:
                self.update_board()
            elif self.selected_square == None:
                self.select_piece(id)
            else:
                self.move_piece(id)

        # change indication of whose move it is
        if (is_legal_move):
            if(self.white_play_color == self.curr_play_color):
                self.white_play_color = self.bg_color
                self.black_play_color = self.curr_play_color
            else:
                self.white_play_color = self.curr_play_color
                self.black_play_color = self.bg_color


if __name__ == '__main__':
    ChessbotApp().run()