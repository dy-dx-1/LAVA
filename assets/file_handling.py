import pickle 
import os 
from tkinter import filedialog
from . import graphiques as graphs
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

    graphs.Courbe_Frequence.regen_values(hbm_res)

if __name__ != "__main__": 
    # If we are running this file as an import, it means we just opened the main program 
    # on initial open, run setup to ask for initial file and generate values 
    initial_setup() 