from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import numpy as np 
import pickle 
import os 
from tkinter import filedialog

class DynamicGraph: 
    """
    Parent class used to create dynamic graphs, do not use directly. 
    _domain, _image and _size are variables shared by all child classes but different for each of them 
    which is why their property methods reference self (child object). 
    Child classes should have a regen_values method that sets these vars accordingly for their own class. 

    Property decorators not really needed for now(2022-11-24), especially as setter methods are handled by child classes, 
    added for clarity and in case we need them later 
    """
    _domain = [] 
    _image = [] 
    _size = []

    @property 
    def domain(self): 
        return self._domain 
    @property
    def image(self): 
        return self._image
    @property
    def size(self):
        return self._size 

    def __init__(self, layout, domain, image): 
        self.figure, self.ax = plt.subplots()
        self.ax.grid(True) 
        self.canvas = FigureCanvas(self.figure)     # self.canvas is the widget that we will use to show the graph 
        layout.addWidget(self.canvas)   # Adding the graph to a layout container in the ui 
        self.ax.plot(domain, image, animated=False)    # preparing initial values
        self.canvas.draw()              # drawing static background of the graph
        self.background = None          # at init, background is None to let everything setup properly before caching the background 
            

    def update_plot(self, new_x, new_y):
        if not self.background: # if we are at first update or after resize, cache the background in the new position 
            self.point = self.ax.plot(0,0, 'go', animated=True)[0]  
            # if here, first run so create point Indexing at 0 to hold the object of the point, plot returns a list 
            self.background = self.canvas.copy_from_bbox(self.ax.bbox) 
        # updating point's location 
        self.point.set_data(new_x, new_y) 
        # preparing for blit by restoring default region
        self.canvas.restore_region(self.background)
        # adding the new point to the ax
        self.ax.draw_artist(self.point) 
        # blitting and flushing the events to make sure everything is done cleanly
        self.canvas.blit(self.ax.bbox)
        self.canvas.flush_events()
        
    def clear(self): 
        self.figure.clear() 

class Courbe_Frequence(DynamicGraph): 
    """
    Sets up and draws the CRF in the desired layout. 
    regen_values method regenerates class variables (domain, image & size) of the CRF. 
    """
    @classmethod
    def regen_values(cls, hbm_res): 
        cls._domain = hbm_res['crf']['omega']
        cls._size = len(cls._domain)
        cls._image = hbm_res['crf']['norme']['x_t']['inf'][0]

    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image) 

class Evolution_Temporelle(DynamicGraph): 
    _domain = [1,2,3,4,5]
    _image = [-5,5,0,3,3]
    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image)

class Spectre_Graph(DynamicGraph): 
    _domain = np.linspace(-3,3)
    _image = list(map(lambda t: np.cos(t), np.linspace(-3,3)))
    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image)

if __name__ != "__main__":
    input_file = "" 
    while input_file == "":     # TODO: add better way, else this will make inf loop when someone launchs program by accident
        input_file = filedialog.askopenfilename(
            title= "Select an hbm_res file", 
            filetypes=[('hbm_res', '*.pkl')], 
            initialdir=fr"{os.getcwd()}/input") 

    # TODO: implement error handling 
    with open(input_file, "rb") as file: 
        hbm_res = pickle.load(file)

    Courbe_Frequence.regen_values(hbm_res)
