from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

DISCO_LENGTH = 2 #seconds

class CalcMainLayout(BoxLayout):

class CalcApp(App):
    def __init__(self, *args, **kwargs):
        super(CalcApp, self).__init__(*args, **kwargs)
    
    def build(self):
        return CalcMainLayout()
    
    def key_press(self, value):
        pass

    def press_ln(self):
        pass
    
    def clear(self):
        pass
    
    def calculate(self):
        pass
    
    def bksp(self):
        pass

 
if __name__=="__main__":
    CalcApp().run()
