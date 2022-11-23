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
    x_vals and y_vals should be cls variables of the child class. 
    """
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
    _domain = [] 
    _image = [] 
    size = []
    @property
    def domain(self): 
        return self.__class__._domain 
    @domain.setter
    def domain(self, new_domain): 
        self.__class__._domain = new_domain
    @property
    def image(self): 
        return self.__class__._image 
    @image.setter
    def image(self, new_image): 
        self.__class__._image = new_image

    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image) 

class Evolution_Temporelle(DynamicGraph): 
    domain = [1,2,3,4,5]
    image = [-5,5,0,3,3]
    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image)

class Spectre_Graph(DynamicGraph): 
    val_x, val_y = np.linspace(-3,3), list(map(lambda t: np.cos(t), np.linspace(-3,3)))
    def __init__(self, layout): 
        super().__init__(layout, self.val_x, self.val_y)

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

    Courbe_Frequence.domain = hbm_res['crf']['omega']
    Courbe_Frequence.size = len(Courbe_Frequence.domain)
    Courbe_Frequence.image = hbm_res['crf']['norme']['x_t']['inf'][0]
