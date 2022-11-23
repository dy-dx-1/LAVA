from tkinter import filedialog
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot
from main_ui import Ui_MainWindow

import sys 

import graphiques as graphs 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None): 
        super(MainWindow, self).__init__(parent=parent) 
        self.ui = Ui_MainWindow()                           
        self.ui.setupUi(self)                           # Setting up the UI defined by "main_ui.py"
    
        self.setup_courbe_freq()
        self.setup_evol_temp() 
        self.setup_spectre() 

    def resizeEvent(self, event_obj):        # overriding the resizeEvent method of QMainWindow so that we can update our cached backgrounds (for blitting)
        self.courbe_freq.background = None   # indication to recache the background on next update 

    def setup_courbe_freq(self): 
        # Plotting something in courbe de réponse en fréq non linéaire 
        self.courbe_freq = graphs.Courbe_Frequence(self.ui.lay_courbe_freq)
        # Setting bounds of slider solutions with the dom of courbe freq 
        self.ui.slider_solutions.setMaximum(self.courbe_freq.size-1) # max of the x domain (right end of slider) | -1 cause index of size will be out of bounds
        self.ui.slider_solutions.setMinimum(0) 
        
        @pyqtSlot() 
        def update_point(): 
            # updating the plot on the slider value change 
            index_of_point = self.ui.slider_solutions.value() # vals of slider correspond to all the indexes in the domain and image sets
            new_x = self.courbe_freq.domain[index_of_point]           
            new_y = self.courbe_freq.image[index_of_point] 
            self.courbe_freq.update_plot(new_x, new_y)
            
            # updating txt (lineedit) box of idx_sols 
            self.ui.idx_sol_line_edit.setText(str(index_of_point))

        # Connecting update_point to the courbe_freq 
        self.ui.slider_solutions.valueChanged.connect(update_point)

        # Connecting button presses to slider value changes 
        @pyqtSlot() 
        def push_slider(push_value:int):           
            self.ui.slider_solutions.setValue(self.ui.slider_solutions.value()+push_value) 
        self.ui.increment_button.clicked.connect(lambda: push_slider(1))
        self.ui.decrement_button.clicked.connect(lambda: push_slider(-1))

    def setup_evol_temp(self): 
        # plotting something in évol temp 
        self.ev_temp = graphs.Evolution_Temporelle(self.ui.lay_ev_temp)
        
    def setup_spectre(self): 
        # plotting something in spectre 
        self.spectre = graphs.Spectre_Graph(self.ui.lay_spectre_freq) 


def main():
    app = QtWidgets.QApplication(sys.argv) 
    window = MainWindow()
    window.show() 
    sys.exit(app.exec()) 

if __name__ == "__main__": 
    main() 