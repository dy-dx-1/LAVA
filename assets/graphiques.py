from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import numpy as np 

class DynamicGraph: 
    """
    Parent class used to create dynamic graphs, do not use directly. 
    _domain, _image and _size are variables shared by all child classes but different for each of them 
    which is why their property methods reference self (child object). 
    Child classes should have a regen_values method that sets these vars accordingly for their own class. 

    Property decorators not really needed for now(2022-11-24), especially as setter methods are handled by child classes, 
    added for clarity and in case we need them later 
    """
    domain = [] 
    image = [] 
    size = None  


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
        cls.domain = hbm_res['crf']['omega']
        cls.size = len(cls.domain)
        cls.image = hbm_res['crf']['norme']['x_t']['inf'][0]

    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image) 

class Evolution_Temporelle(DynamicGraph): 
    domain = [1,2,3,4,5]
    image = [-5,5,0,3,3]
    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image)

class Spectre_Graph(DynamicGraph): 
    domain = np.linspace(-3,3)
    image = list(map(lambda t: np.cos(t), np.linspace(-3,3)))
    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image)