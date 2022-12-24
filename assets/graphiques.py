from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import numpy as np 
from . import hb_tools as tools 
class DynamicGraph: 
    """
    Parent class used to create dynamic graphs, do not use directly. 
    _domain, _image and _size are variables shared by all child classes but different for each of them 
    which is why their property methods reference self (child object). 
    Child classes should have a regen_values method that sets these vars accordingly for their own class. 
    """
    domain = [] 
    image = [] 
    size = None  

    hbm_res = None 
    ddls_to_display = None    # Used to generate combobox of ddls

    selected_ddl = 0 
    @classmethod
    def update_ddl(cls, new_ddl:int): 
        cls.selected_ddl = np.array([new_ddl])
        cls.update_post(idx_ddl = cls.selected_ddl)
        
    @classmethod
    def update_post(cls, **new_values): 
        for k, v in new_values.items(): 
            cls.post[k] = v 
    post = {               
    'norme': 'inf',
    'quantite': 'x_t',
    'idx_ddl': np.array([selected_ddl]),        # idx of ddl to display, init at 0 
    'colors': {'bleu': '#22a1e9',
               'vert': '#80cc28',
               'orange': '#fa961e',
               'rouge': '#bf2033',
               'magenta': '#ff00ff',
               'noir': '#000000',
               'soft_gray': '#696969',
               'dark_gray': '#6a6a6a'},
    'sep_deci': '.'}
    
    def __init__(self, layout, domain, image): 
        self.figure, self.ax = plt.subplots()
        self.ax.grid(True) 
        plt.tight_layout()                     # Prevents overflowing of axes title into the group boxes 
        self.figure.set_tight_layout(True)     # so that tight_layout is kept on resizes 
        self.canvas = FigureCanvas(self.figure)     # self.canvas is the widget that we will use to show the graph 
        layout.addWidget(self.canvas)   # Adding the graph to a layout container in the ui 
        self.ax.plot(domain, image, animated=False)    # preparing initial values
        self.canvas.draw()              # drawing static background of the graph
        self.background = None          # at init, background is None to let everything setup properly before caching the background 
            
    def blit_plot(self, new_x, new_y, point_like=True):
        if not self.background: # if we are at first update or after resize, cache the background in the new position 
            if point_like: 
                self.artist = self.ax.plot(0,0, 'go', animated=True)[0]  # if here, first run so create point Indexing at 0 to hold the object of the point, plot returns a list 
                self.background = self.canvas.copy_from_bbox(self.ax.bbox) # caching the static image where we will put the point over
            else: 
                self.ax.cla() # clearing axis to get a clean copy of background as cached reference 
                self.ax.grid(True) 
                self.canvas.draw() 
                self.background = self.canvas.copy_from_bbox(self.ax.bbox) # saving the clean axis
                self.artist = self.ax.plot([],[], animated=True)[0]  
        # updating artist data 
        self.artist.set_data(new_x, new_y) 
        # preparing for blit by restoring default region
        self.canvas.restore_region(self.background)
        # adding the new artist to the ax
        self.ax.draw_artist(self.artist) 
        # blitting and flushing the events to make sure everything is done cleanly
        self.canvas.blit(self.ax.bbox)
        self.canvas.flush_events()
        

class Courbe_Frequence(DynamicGraph): 
    """
    Sets up and draws the CRF in the desired layout. 
    regen_values method regenerates class variables (domain, image & size) of the CRF. 
    """
    @classmethod
    def regen_values(cls): 
       cls.domain = cls.hbm_res['crf']['omega']
       cls.size = len(cls.domain)
       cls.image = cls.hbm_res['crf']['norme']['x_t']['inf'][0]

    def __init__(self, layout): 
        self.figure, self.ax = tools.fig_crf_cont(self.hbm_res, self.post)
        plt.tight_layout()                     # Prevents overflowing of axes title into the group boxes 
        self.figure.set_tight_layout(True)     # so that tight_layout is kept on resizes 
        self.canvas = FigureCanvas(self.figure)     # self.canvas is the widget that we will use to show the graph 
        layout.addWidget(self.canvas)   # Adding the graph to a layout container in the ui 
        self.canvas.draw()              # drawing static background of the graph
        self.background = None          # at init, background is None to let everything setup properly before caching the background 

class Evolution_Temporelle(DynamicGraph): 
    """ 
    Sets up Evol temp graph and plots it on it's corresponding layout 
    regen_values method regenerates the domain, image and q_t_nl associated to it, which are then used to plot new functions 
    when blitting on slider update. 
    """
    q_t_nl = None 

    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image)
    
    @classmethod
    def regen_values(cls, sol_idx:int): 
        cls.q_t_nl = cls.hbm_res['crf'][cls.post['quantite']][cls.hbm_res['input']['syst']['ddl_nl']]
        cls.domain = cls.hbm_res['crf']['tau']
        ddl_idx = cls.post['idx_ddl']
        cls.image = cls.q_t_nl[ddl_idx,:,sol_idx].T


class Spectre_Graph(DynamicGraph): 
    domain = np.linspace(-3,3)
    image = list(map(lambda t: np.cos(t), np.linspace(-3,3)))
    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image)