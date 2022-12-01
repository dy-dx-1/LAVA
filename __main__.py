from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot
import sys 

from assets.ui_structure import Ui_MainWindow
import assets.graphiques as graphs 

import pickle 
import os 
from tkinter import filedialog
import numpy as np 
def initial_setup(): 
    input_file = "" 
    while input_file == "":     # TODO: add better way, else this will make inf loop when someone launchs program by accident
        input_file = filedialog.askopenfilename(
            title= "Select an hbm_res file", 
            filetypes=[('hbm_res', '*.pkl')], 
            initialdir=fr"{os.getcwd()}/input") 

    # TODO: implement error handling 
    with open(input_file, "rb") as file: 
        hbm_res = pickle.load(file)
    
    # Extracting ddl options, we will add them to combobox on GUI init 
    ddls_dict = hbm_res['input']['syst']['ddl_visu']
    ddl_idx = ddls_dict.keys() #############################################TODO: 'if k in ddl_idx' necessary?? 
    ddl_nl_labels = (fr"{k} : ${v}$" for k, v in hbm_res['input']['syst']['ddl_visu'].items() if k in ddl_idx)
    graphs.Courbe_Frequence.ddls_to_display = ddl_nl_labels

    post = {
    'norme': 'inf',
    'quantite': 'x_t',
    'idx_ddl': np.array([0]), # idx des ddls à afficher
    'colors': {'bleu': '#22a1e9',
               'vert': '#80cc28',
               'orange': '#fa961e',
               'rouge': '#bf2033',
               'magenta': '#ff00ff',
               'noir': '#000000',
               'soft_gray': '#696969',
               'dark_gray': '#6a6a6a'},
    'sep_deci': '.'}

    # Generating values for different curves with hbm_res 
    graphs.Courbe_Frequence.regen_values(hbm_res)
    graphs.Evolution_Temporelle.regen_references(hbm_res, post) 
    graphs.Evolution_Temporelle.regen_values(0) # slider inits at 0

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None): 
        super(MainWindow, self).__init__(parent=parent) 
        self.ui = Ui_MainWindow()                           
        self.ui.setupUi(self)                           # Setting up the UI defined by our ui reference file 
        for ddl_text in graphs.Courbe_Frequence.ddls_to_display: self.ui.select_chx_ddl.addItem(ddl_text)
    
        self.setup_courbe_freq()
        self.setup_evol_temp() 
        self.setup_spectre() 

    def resizeEvent(self, event_obj):        # overriding the resizeEvent method of QMainWindow so that we can update our cached backgrounds (for blitting)
        self.courbe_freq.background = None   # indication to recache the background on next update 
        self.ev_temp.background = None 

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

            # updating evolution temporelle 
            self.ev_temp.regen_values(index_of_point)
            self.ev_temp.update_plot(self.ev_temp.domain, self.ev_temp.image, point_like=False)

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
    initial_setup() 
    app = QtWidgets.QApplication(sys.argv) 
    window = MainWindow()
    window.show() 
    window.activateWindow() 
    sys.exit(app.exec()) 

if __name__ == "__main__": 
    main() 