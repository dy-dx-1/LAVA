from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot
import sys 

from assets.ui_structure import Ui_MainWindow
import assets.graphiques as graphs 
import assets.file_handling as fhand

import pickle 
import os 
from tkinter import filedialog

# debugger 
# ajouter informations générales du système (nom, temps de calcul) /////////////////////
# error handling file open ////////////////////////////////////////////////
# format overflow of axis into group box/////////// NOTE: TIGHTLAYOUT CAUSES LAG ON RESIZE!!! 
# ajouter informations x* ////////////////////////////////
# ajouter informations sur paramètresHBM 
# Formatter évolution temporelle 
# Ajouter efforts + format 
# Update index on enter 
# Ajouter navbar matplotlib pour CRF 
# Couleurs du slider, voir dans crf couleur spécifiée dans scatter  
# raccourcis clavier & menu (échap pour exit, 1, 2 ,3 pour widgets )

    
 
def initial_setup(): 
    """
    Runs at the beginning of the program and collects the necessary information to generate the graphs. 
    """
    global input_file # holds the name of the input file being analyzed. constant for all of the program when analyzing a particular file
    input_file = filedialog.askopenfilename(
        title= "Select an hbm_res file", 
        filetypes=[('hbm_res', '*.pkl')], 
        initialdir=fr"{os.getcwd()}/input") 

    try: 
        with open(input_file, "rb") as file: 
            hbm_res = pickle.load(file)
    except FileNotFoundError: 
        print(f"""Aucun fichier n'a été trouvé avec le nom: "{input_file}".""")
        print("---Fermeture du programme.---") 
        sys.exit(1) 
    
    # Extracting ddl options, we will add them to combobox on GUI init 
    graphs.DynamicGraph.ddls_to_display = (fr"{k} : {v}" for k, v in hbm_res['input']['syst']['ddl_visu'].items())

    graphs.DynamicGraph.hbm_res = hbm_res
    # Generating values for different curves with hbm_res 
    graphs.Courbe_Frequence.regen_values()
    graphs.Evolution_Temporelle.regen_values(0) # slider inits at 0
    
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None): 
        super(MainWindow, self).__init__(parent=parent) 
        self.ui = Ui_MainWindow()                           
        self.ui.setupUi(self)                           # Setting up the UI defined by our ui reference file 
        self.ui.label_infos_sys.setText(fhand.get_sys_info(input_file, graphs.DynamicGraph.hbm_res)) 
        for ddl_text in graphs.DynamicGraph.ddls_to_display: self.ui.select_chx_ddl.addItem(ddl_text)   # Adding ddls to combobox  
        self.ui.select_chx_ddl.activated.connect(lambda: self.setup_new_ddl(self.ui.select_chx_ddl.currentText()))      

        self.setup_courbe_freq()
        self.setup_evol_temp() 
        self.setup_spectre() 
        self.on_slider_update()  # running it at init so that the infos are displayed on first view and not after 1rst update of slider 

    def resizeEvent(self, event_obj):       
        """ 
        Overrides the resizeEvent method of QMainWindow so that we can update our cached background for blitting 
        """
        self.courbe_freq.background = None   # indication to recache the background on next update 
        self.ev_temp.background = None 

    @pyqtSlot() 
    def on_slider_update(self): 
        # updating the plot on the slider value change 
        index_of_point = self.ui.slider_solutions.value() # vals of slider correspond to all the indexes in the domain and image sets
        new_x = self.courbe_freq.domain[index_of_point]           
        new_y = self.courbe_freq.image[index_of_point] 
        self.courbe_freq.blit_plot(new_x, new_y, point_like=True)
        
        # updating txt (lineedit) box of idx_sols 
        self.ui.idx_sol_line_edit.setText(str(index_of_point))

        # updating evolution temporelle 
        self.ev_temp.regen_values(index_of_point)
        self.ev_temp.blit_plot(self.ev_temp.domain, self.ev_temp.image, point_like=False)      

        # updating informations sur x* 
        self.ui.label_infos_x.setText(f"Index solution = {index_of_point}  ;  ω = {round(new_x, 4)}rad⋅s⁻¹  ;  ‖x\u20D7‖ = {round(new_y, 6)}m") 

    def setup_courbe_freq(self): 
        """
        Sets up the CRF along with the slider and actions associated with it. 
        """
        # Plotting something in courbe de réponse en fréq non linéaire 
        self.courbe_freq = graphs.Courbe_Frequence(self.ui.lay_courbe_freq, self.ui.layout_infos_choix)
        # Setting bounds of slider solutions with the dom of courbe freq 
        self.ui.slider_solutions.setMaximum(self.courbe_freq.size-1) # max of the x domain (right end of slider) | -1 cause index of size will be out of bounds
        self.ui.slider_solutions.setMinimum(0) 

        self.ui.slider_solutions.valueChanged.connect(self.on_slider_update)
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
    
    def setup_new_ddl(self, ddl:str): 
        """
        Updates the GUI to display information related to a new selected ddl 
        Runs when user selects a new ddl with ddl combobox 
        """
        ddl = int(ddl[0])  # TODO: use other way than currentText()? maybe just index                 
        graphs.DynamicGraph.update_ddl(new_ddl=ddl) 
        self.ui.lay_courbe_freq.removeWidget(self.courbe_freq.canvas)
        self.courbe_freq = graphs.Courbe_Frequence(self.ui.lay_courbe_freq)

def main():
    initial_setup() 
    app = QtWidgets.QApplication(sys.argv) 
    window = MainWindow()
    window.show() 
    window.activateWindow() 
    sys.exit(app.exec()) 

if __name__ == "__main__": 
    main() 