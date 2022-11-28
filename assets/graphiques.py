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



def fig_effort_nl(hbm_res, post, sol_idx, module='crf', dep_unit='m', fnl_unit='N'):
    """
    Permet de visualiser l'effort nl effectif vs reconstruit dans la base de Fourier
    """

    ddl_idx = post['idx_ddl']

    ddl_nl_labels = [str(k)+' : $'+v+'$' for k, v in hbm_res['input']['syst']['ddl_visu'].items() if k in ddl_idx]

    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(12,8))
    fig.suptitle('Déplacements et efforts nl')

    colors_list = ['b', 'c', 'r', 'orange', 'm', 'g', 'k', 'y', 'gray']
    custom_cycler = (cycler(color=colors_list[:ddl_idx.shape[0]]) +
                     cycler(lw=[1]*ddl_idx.shape[0]))

    axs[0].set_xlim(hbm_res[module]['tau'][0],hbm_res[module]['tau'][-1])
    axs[1].set_xlim(hbm_res[module]['tau'][0],hbm_res[module]['tau'][-1])
    axs[1].set_ylim([5*np.min(hbm_res[module]['f_nl_tilde']),np.max(hbm_res[module]['f_nl_t'])])

    q_t_nl = hbm_res[module][post['quantite']][hbm_res['input']['syst']['ddl_nl']]
    f_nl_t = hbm_res[module]['f_nl_t'][hbm_res['input']['syst']['ddl_nl']]
    f_nl_tilde  = hbm_res[module]['f_nl_tilde'][hbm_res['input']['syst']['ddl_nl']]

    axs[1].text(0.02, 1.05,'\u03C9 = {a:.3f} [rad.s-1] / f = {b:.3f} [Hz] / sol_idx = {c:d}'.format(a=hbm_res[module]['omega'][sol_idx],\
                           b=hbm_res[module]['omega'][sol_idx]/(2*np.pi),c=sol_idx), ha='left', va='center', \
                           transform=axs[0].transAxes)

    # déplacements
    axs[0].set_prop_cycle(custom_cycler)
    try:
        lineObjects = axs[0].plot(hbm_res[module]['tau'],q_t_nl[ddl_idx,:,sol_idx].T,lw=1.5)
    except IndexError :
        lineObjects = axs[0].plot(hbm_res[module]['tau'],q_t_nl[hbm_res['input']['syst']['mask_front'],:,sol_idx].T)
    axs[0].set_xlim(hbm_res[module]['tau'][0],hbm_res[module]['tau'][-1])

    # autoscaling en y
    axs[0].relim()
    axs[0].autoscale_view(tight=True)

    # TODO à revoir
    if hbm_res['input']['syst']['profil_contact'] is not None:
        if hbm_res['input']['syst']['profil_contact'] == 'cst' and post['quantite'] == 'x_t':
            axs[0].hlines(hbm_res['input']['syst']['d_t'][ddl_idx],xmin=hbm_res[module]['tau'][0],xmax=hbm_res[module]['tau'][-1],linestyle='dashed',alpha = 0.5)
            for n in hbm_res['input']['syst']['mask_front']:
                axs[0].fill_between(hbm_res[module]['tau'],max(1.1*q_t_nl[hbm_res['input']['syst']['mask_front'],:,sol_idx].min(),(2*hbm_res['input']['syst']['d_t']).min()),hbm_res['input']['syst']['d_t'][n],color='gray',zorder=-1,alpha=0.75)
            axs[0].set_ylim(top=max(1.1*q_t_nl[hbm_res['input']['syst']['mask_front'],:,sol_idx].max(),1.1*hbm_res['input']['syst']['d_t'].max()),
                            bottom=min((1.1*q_t_nl[hbm_res['input']['syst']['mask_front'],:,sol_idx]).min(),(1.1*hbm_res['input']['syst']['d_t']).min()))
        else:
            axs[0].set_prop_cycle(custom_cycler)
            if hbm_res['input']['syst']['usure']:
                d_t_carter = (hbm_res[module]['usure']['d_t_cont'][...,sol_idx] - hbm_res[module]['usure']['alpha_t_cont'][...,sol_idx])+ hbm_res['input']['syst']['ep_abr']
                axs[0].plot(hbm_res[module]['usure']['theta'],d_t_carter.T,linestyle='dashed',alpha=0.5,lw=0.75)
                axs[0].plot(hbm_res[module]['usure']['theta'],hbm_res[module]['usure']['d_t_cont'][ddl_idx//hbm_res['input']['syst']['ddl_noeud'],:,sol_idx].T,linestyle='dashed',alpha=0.5,lw=0.75)
            else:
                axs[0].plot(hbm_res[module]['tau'],hbm_res[module]['d_t_cont'][...,sol_idx].T,linestyle='dashed',alpha=0.5,lw=0.75)

            if hbm_res['input']['syst']['usure']:
                for n in ddl_idx//hbm_res['input']['syst']['ddl_noeud']:
                    axs[0].fill_between(hbm_res[module]['usure']['theta'],1.1*d_t_carter.max(),d_t_carter[n,:],color='gray',zorder=-1,alpha=0.75)
                    axs[0].fill_between(hbm_res[module]['usure']['theta'],d_t_carter[n,:],hbm_res[module]['usure']['d_t_cont'][n,:,sol_idx],color='gray',zorder=-1,alpha=0.075)
            else:
                for n in ddl_idx//hbm_res['input']['syst']['ddl_noeud']:
                    axs[0].fill_between(hbm_res[module]['tau'],1.1*hbm_res[module]['d_t_cont'][n,:,sol_idx].max(),hbm_res[module]['d_t_cont'][n,:,sol_idx],color = 'gray',zorder=-1,alpha=0.75)

            if hbm_res['input']['syst']['usure']:
                axs[0].set_ylim(top=max(1.1*q_t_nl[ddl_idx,:,sol_idx].max(),1.1*hbm_res[module]['usure']['d_t_cont'][...,sol_idx].max()))
            else:
                axs[0].set_ylim(top=max(1.1*q_t_nl[ddl_idx,:,sol_idx].max(),1.1*hbm_res[module]['d_t_cont'][hbm_res['input']['syst']['mask_front'],:,sol_idx].max()))


    axs[0].set_prop_cycle(custom_cycler)

    axs[0].legend(iter(lineObjects),ddl_nl_labels,loc='center left', bbox_to_anchor=(1, 0.5),fontsize=10)

    # efforts
    axs[1].set_prop_cycle(custom_cycler)
    axs[1].plot(hbm_res[module]['tau'],f_nl_t[ddl_idx,:,sol_idx].T,linestyle='dashed',alpha = 0.5)
    axs[1].plot(hbm_res[module]['tau'],f_nl_tilde[ddl_idx,:,sol_idx].T,lw=1.5)

    axs[0].set_ylabel(r'$x$(t) [' + dep_unit + ']')

    axs[1].set_xlabel(r'$\tau$')

    if hbm_res['input']['solv']['nu'] == 1 :
        axs[1].set_xticks([0, np.pi, 2*np.pi])
        axs[1].set_xticklabels(['$0$', '$T/2$', '$T$'])
    elif hbm_res['input']['solv']['nu'] == 2 :
        axs[1].set_xticks([0, np.pi, 2*np.pi, 3*np.pi, 4*np.pi])
        axs[1].set_xticklabels(['$0$', '$T/2$', '$T$', '$3T/2$', '$2T$'])

    axs[1].set_ylabel(r'$f_{nl}$ [' + fnl_unit + ']')
