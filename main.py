### GUI windows 
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import pyqtSlot, Qt
from tkinter import filedialog

### Backend (assets module) 
from assets.ui_structure import Ui_MainWindow
import assets.graphiques as graphs 
import assets.file_handling as fhand

### File handling 
import os 
import sys 
import pickle 

### TODO
# debugger 
# ajouter informations générales du système (nom, temps de calcul) /////////////////////
# error handling file open ////////////////////////////////////////////////
# format overflow of axis into group box/////////// NOTE: TIGHTLAYOUT CAUSES LAG ON RESIZE!!! 
# ajouter informations x* ////////////////////////////////
# ajouter informations sur paramètresHBM/////////////////////////// 
# Formatter évolution temporelle ////////////////// NOTE: labels sur axe des x? patch gris doivent être dynamiques? -> adapter si oui 
# Ajouter efforts/////////////// NOTE: y lim set par la fonction donnée weird, voir la fonction dans hb_tools 
# Update index on enter /////////////////////////////////////
# Ajouter navbar matplotlib pour CRF ///////////////////// --> NOTE: remove buttons? 
# Couleurs du slider, voir dans crf couleur spécifiée dans scatter  ////////////////////////////////////////
# raccourcis clavier & menu (échap pour exit, 1, 2 ,3 pour widgets )
# infos @init of window //////////////////////////////
# reformat so that everything is clear /////////////

def initial_setup(): 
    """
    Runs at the beginning of the program and collects the necessary information to generate the graphs. 
    Information is updated and stored in the graphs classes as class attributes that will be accessed through the GUI. 
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
    graphs.Efforts.regen_values(0)
    
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None): 
        super(MainWindow, self).__init__(parent=parent) 
        # Linking to the ref ui 
        self.ui = Ui_MainWindow()                           
        self.ui.setupUi(self)               # Setting up the UI defined by our ui reference file 
        # Displaying system infos 
        self.ui.label_infos_sys.setText(fhand.get_sys_info(input_file, graphs.DynamicGraph.hbm_res))  
        self.ui.gb_infos_sys.setMinimumWidth(int(len(self.ui.label_infos_sys.text())*6.6)) # Making sure that we always display all of the text, 6.6 is just a multiplier i found to work well experimentally (letters -> pixels) 
        # Displaying infos sur x @0 
        self.ui.label_infos_x.setText(f"Index solution = {0}  ;  ω = {round(graphs.Courbe_Frequence.domain[0], 4)}rad⋅s⁻¹  ;  ‖x\u20D7‖ = {round(graphs.Courbe_Frequence.image[0], 6)}m") 
        # Displaying paramètres hbm 
        self.ui.label_params_hbm.setText(fhand.get_hbm_params(graphs.DynamicGraph.hbm_res))        
        # Filling ddl combobox with possible ddls & adding change ddl functionality ( setup_new_ddl() )
        for ddl_text in graphs.DynamicGraph.ddls_to_display: self.ui.select_chx_ddl.addItem(ddl_text)     
        self.ui.select_chx_ddl.activated.connect(lambda: self.setup_new_ddl(self.ui.select_chx_ddl.currentText()))  
        # Allowing slider to be updated on enter press after changing value of idx lineedit 
        self.ui.idx_sol_line_edit.returnPressed.connect(self.on_idx_enter)   
        # Coloring the slider 
        self.ui.slider_solutions.setStyleSheet(fhand.generate_slider_stylesheet(graphs.DynamicGraph.hbm_res))
        self.setup_courbe_freq()
        self.setup_evol_temp() 
        self.setup_efforts() 

    def keyPressEvent(self, event):
        """ 
        Links different actions to keypresses. 
        Using match case for clarity instead of if/elif. 
        """
        key = event.key() 
        match key: 
            case Qt.Key.Key_Escape: 
                self.close() 
            case Qt.Key.Key_Plus:
                self.ui.slider_solutions.setValue(self.ui.slider_solutions.value()+1) 
            case Qt.Key.Key_Minus: 
                self.ui.slider_solutions.setValue(self.ui.slider_solutions.value()-1)
            
    def resizeEvent(self, event):       
        """ 
        Overrides the resizeEvent method of QMainWindow so that we can update our cached background for blitting 
        """
        #TODO: fix reset of ev temp on resize --> set background to something else? 
        # self.on_slider_update()   #--> lol this kinda works but buggy and laggy 
        self.courbe_freq.background = None   # indication to recache the background on next update 
        self.ev_temp.background = None 
        self.efforts.background = None 
        QtWidgets.QMainWindow.resizeEvent(self, event) 
    
    @pyqtSlot()
    def on_idx_enter(self): 
        """
        Updates the slider position and the graphs when someone presses enter in the idx line edit. 
        """
        new_val = self.ui.idx_sol_line_edit.text() 
        if new_val == '': new_val = 0 # at init '' is default value 
        self.ui.slider_solutions.setValue(int(float(new_val))) # float -> int called to avoid invalid literal  

    @pyqtSlot() 
    def on_slider_update(self): 
        """ 
        Updates the graphs and related display info for a new index value. 
        """
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

        # updating efforts 
        self.efforts.regen_values(index_of_point) 
        self.efforts.blit_plot(self.efforts.domain, self.efforts.image, point_like=False)

        # updating informations sur x* 
        self.ui.label_infos_x.setText(f"Index solution = {index_of_point}  ;  ω = {round(new_x, 4)}rad⋅s⁻¹  ;  ‖x\u20D7‖ = {round(new_y, 6)}m") 

    def setup_courbe_freq(self): 
        """
        Sets up the CRF along with the slider and actions associated with it. 
        """
        # Plotting something in courbe de réponse en fréq non linéaire 
        self.courbe_freq = graphs.Courbe_Frequence(self.ui.lay_courbe_freq, self.ui.layout_toolbar)
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
        """
        Formats the y axis of evol temp and initialises it. If ddl has been changed, it must be fully updated before calling this
        as it calls q_t_nl and post['idx_ddl'] to construct the images.  
        """
        # plotting something in évol temp 
        self.ev_temp = graphs.Evolution_Temporelle(self.ui.lay_ev_temp)
        # generator comprehension finds the max of all the local maximums for each image associated to a particular idx on the slider
        abs_max = max((max(self.ev_temp.q_t_nl[self.ev_temp.post['idx_ddl'],:,idx][0]) for idx in range(self.ui.slider_solutions.maximum())))
        abs_min = min((min(self.ev_temp.q_t_nl[self.ev_temp.post['idx_ddl'],:,idx][0]) for idx in range(self.ui.slider_solutions.maximum())))
        self.ev_temp.ax.set_ylim(abs_min, abs_max)

    def setup_efforts(self): 
        # plotting something in  efforts 
        self.efforts = graphs.Efforts(self.ui.lay_efforts) 
    
    def setup_new_ddl(self, ddl:str): 
        """
        Updates the GUI to display information related to a new selected ddl 
        Runs when user selects a new ddl with ddl combobox 
        """
        ddl = int(ddl[0])  # TODO: use other way than currentText()? maybe just index   
        # Updating ddl for all the graphs               
        graphs.DynamicGraph.update_ddl(new_ddl=ddl) 

        # Closing matplotlib figures ("Figures created through the pyplot interface (`matplotlib.pyplot.figure`) are retained until explicitly closed and may consume too much memory.")
        self.courbe_freq.close() 
        self.ev_temp.close() 
        self.efforts.close() 

        # Removing toolbar and graphs 
        self.ui.layout_toolbar.removeWidget(self.courbe_freq.toolbar)
        self.ui.lay_courbe_freq.removeWidget(self.courbe_freq.canvas)
        self.ui.lay_ev_temp.removeWidget(self.ev_temp.canvas) 
        self.ui.lay_efforts.removeWidget(self.efforts.canvas) 

        # Initializing new ones with new ddl 
        graphs.Courbe_Frequence.regen_values()
        graphs.Evolution_Temporelle.regen_values(self.ui.slider_solutions.value()) 
        graphs.Efforts.regen_values(self.ui.slider_solutions.value())
        self.courbe_freq = graphs.Courbe_Frequence(self.ui.lay_courbe_freq, self.ui.layout_toolbar)
        self.setup_evol_temp()
        self.efforts = graphs.Efforts(self.ui.lay_efforts) 

def main():
    initial_setup() 
    app = QtWidgets.QApplication(sys.argv) 
    window = MainWindow()
    window.show() 
    window.activateWindow() 
    sys.exit(app.exec()) 

if __name__ == "__main__": 
    main() 