#! /home/pi/.venv/chessbot/bin/python
import kivy
kivy.require('2.0.0')

from kivy.config import Config
Config.set('graphics','width','800')
Config.set('graphics','height','478')
Config.set('graphics','position','custom')
Config.set('graphics','left',0)
Config.set('graphics','top',0)
Config.write()

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x,velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class PongGame(Widget):
    pass

class PongApp(App):

    def build(self):
        return PongGame()

if __name__ == '__main__':
    PongApp().run()