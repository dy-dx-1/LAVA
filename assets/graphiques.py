from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import numpy as np 
from cycler import cycler 
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


    def __init__(self, layout, domain, image): 
        self.figure, self.ax = plt.subplots()
        self.ax.grid(True) 
        self.canvas = FigureCanvas(self.figure)     # self.canvas is the widget that we will use to show the graph 
        layout.addWidget(self.canvas)   # Adding the graph to a layout container in the ui 
        self.ax.plot(domain, image, animated=False)    # preparing initial values
        self.canvas.draw()              # drawing static background of the graph
        self.background = None          # at init, background is None to let everything setup properly before caching the background 
            
    def update_plot(self, new_x, new_y, point_like=True):
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
        
    def clear(self): 
        self.figure.clear() 

class Courbe_Frequence(DynamicGraph): 
    """
    Sets up and draws the CRF in the desired layout. 
    regen_values method regenerates class variables (domain, image & size) of the CRF. 
    Also holds the ddls of the system in a generator 
    """
    ddls_to_display = None  
    @classmethod
    def regen_values(cls, hbm_res): 
        cls.domain = hbm_res['crf']['omega']
        cls.size = len(cls.domain)
        cls.image = hbm_res['crf']['norme']['x_t']['inf'][0]

    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image) 

class Evolution_Temporelle(DynamicGraph): 
    q_t_nl = None 
    hbm_res = None              # internal ref to hbm_res, used to update on slider values 
    post = None 
    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image)

    @classmethod 
    def regen_references(cls, new_hbm_res:dict, new_post:dict): 
        cls.hbm_res = new_hbm_res
        cls.post = new_post

    @classmethod
    def regen_values(cls, sol_idx:int): 
        cls.q_t_nl = cls.hbm_res['crf'][cls.post['quantite']][cls.hbm_res['input']['syst']['ddl_nl']]
        cls.domain = cls.hbm_res['crf']['tau']
        ddl_idx = cls.post['idx_ddl']
        cls.image = cls.q_t_nl[ddl_idx,:,sol_idx].T

    def fig_effort_nl(self, hbm_res:dict, post:dict, sol_idx:int, module:str='crf', dep_unit:str='m'):
        """
        Permet de visualiser l'effort nl effectif vs reconstruit dans la base de Fourier
        """
        ddl_idx = post['idx_ddl']
        ddl_nl_labels = [str(k)+' : $'+v+'$' for k, v in hbm_res['input']['syst']['ddl_visu'].items() if k in ddl_idx]
        
        self.figure.suptitle('Déplacements et efforts nl')

        colors_list = ['b', 'c', 'r', 'orange', 'm', 'g', 'k', 'y', 'gray']
        custom_cycler = (cycler(color=colors_list[:ddl_idx.shape[0]]) +
                        cycler(lw=[1]*ddl_idx.shape[0]))

        self.ax.set_xlim(self.domain[0],self.domain[-1])

        # déplacements
        self.ax.set_prop_cycle(custom_cycler)
        try:
            lineObjects = self.ax.plot(self.domain,self.image.T,lw=1.5)
        except IndexError :
            lineObjects = self.ax.plot(self.domain,self.q_t_nl[hbm_res['input']['syst']['mask_front'],:,sol_idx].T)
        self.ax.set_xlim(self.domain[0],self.domain[-1])

        # autoscaling en y
        self.ax.relim()
        self.ax.autoscale_view(tight=True)

        # TODO à revoir
        if hbm_res['input']['syst']['profil_contact'] is not None:
            if hbm_res['input']['syst']['profil_contact'] == 'cst' and post['quantite'] == 'x_t':
                self.ax.hlines(hbm_res['input']['syst']['d_t'][ddl_idx],xmin=self.domain[0],max=self.domain[-1],linestyle='dashed',alpha = 0.5)
                for n in hbm_res['input']['syst']['mask_front']:
                    self.ax.fill_between(self.domain,max(1.1*self.q_t_nl[hbm_res['input']['syst']['mask_front'],:,sol_idx].min(),(2*hbm_res['input']['syst']['d_t']).min()),hbm_res['input']['syst']['d_t'][n],color='gray',zorder=-1,alpha=0.75)
                self.ax.set_ylim(top=max(1.1*self.q_t_nl[hbm_res['input']['syst']['mask_front'],:,sol_idx].max(),1.1*hbm_res['input']['syst']['d_t'].max()),
                                bottom=min((1.1*self.q_t_nl[hbm_res['input']['syst']['mask_front'],:,sol_idx]).min(),(1.1*hbm_res['input']['syst']['d_t']).min()))
            else:
                self.ax.set_prop_cycle(custom_cycler)
                if hbm_res['input']['syst']['usure']:
                    d_t_carter = (hbm_res[module]['usure']['d_t_cont'][...,sol_idx] - hbm_res[module]['usure']['alpha_t_cont'][...,sol_idx])+ hbm_res['input']['syst']['ep_abr']
                    self.ax.plot(hbm_res[module]['usure']['theta'],d_t_carter.T,linestyle='dashed',alpha=0.5,lw=0.75)
                    self.ax.plot(hbm_res[module]['usure']['theta'],hbm_res[module]['usure']['d_t_cont'][ddl_idx//hbm_res['input']['syst']['ddl_noeud'],:,sol_idx].T,linestyle='dashed',alpha=0.5,lw=0.75)
                else:
                    self.ax.plot(self.domain,hbm_res[module]['d_t_cont'][...,sol_idx].T,linestyle='dashed',alpha=0.5,lw=0.75)

                if hbm_res['input']['syst']['usure']:
                    for n in ddl_idx//hbm_res['input']['syst']['ddl_noeud']:
                        self.ax.fill_between(hbm_res[module]['usure']['theta'],1.1*d_t_carter.max(),d_t_carter[n,:],color='gray',zorder=-1,alpha=0.75)
                        self.ax.fill_between(hbm_res[module]['usure']['theta'],d_t_carter[n,:],hbm_res[module]['usure']['d_t_cont'][n,:,sol_idx],color='gray',zorder=-1,alpha=0.075)
                else:
                    for n in ddl_idx//hbm_res['input']['syst']['ddl_noeud']:
                        self.ax.fill_between(self.domain,1.1*hbm_res[module]['d_t_cont'][n,:,sol_idx].max(),hbm_res[module]['d_t_cont'][n,:,sol_idx],color = 'gray',zorder=-1,alpha=0.75)

                if hbm_res['input']['syst']['usure']:
                    self.ax.set_ylim(top=max(1.1*self.image.max(),1.1*hbm_res[module]['usure']['d_t_cont'][...,sol_idx].max()))
                else:
                    self.ax.set_ylim(top=max(1.1*self.image.max(),1.1*hbm_res[module]['d_t_cont'][hbm_res['input']['syst']['mask_front'],:,sol_idx].max()))

        self.ax.set_prop_cycle(custom_cycler)
        self.ax.legend(iter(lineObjects),ddl_nl_labels,loc='center left', bbox_to_anchor=(1, 0.5),fontsize=10)
        self.ax.set_ylabel(r'$x$(t) [' + dep_unit + ']')



class Spectre_Graph(DynamicGraph): 
    domain = np.linspace(-3,3)
    image = list(map(lambda t: np.cos(t), np.linspace(-3,3)))
    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image)
