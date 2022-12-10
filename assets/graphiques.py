from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib

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
        
    def clear(self): 
        self.figure.clear() 

class Courbe_Frequence(DynamicGraph): 
    """
    Sets up and draws the CRF in the desired layout. 
    regen_values method regenerates class variables (domain, image & size) of the CRF. 
    Also holds the ddls of the system in a generator 
    """
    @classmethod
    def regen_values(cls): 
       cls.domain = cls.hbm_res['crf']['omega']
       cls.size = len(cls.domain)
       cls.image = cls.hbm_res['crf']['norme']['x_t']['inf'][0]

    def __init__(self, layout): 
        self.figure, self.ax = fig_crf_cont(self.hbm_res, self.post)
        self.canvas = FigureCanvas(self.figure)     # self.canvas is the widget that we will use to show the graph 
        layout.addWidget(self.canvas)   # Adding the graph to a layout container in the ui 
        self.canvas.draw()              # drawing static background of the graph
        self.background = None          # at init, background is None to let everything setup properly before caching the background 

class Evolution_Temporelle(DynamicGraph): 
    q_t_nl = None 

    def __init__(self, layout): 
        super().__init__(layout, self.domain, self.image)
    
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
########-----------------------------------###################----------------------------########################---------------
def norme_result(norme,solv,syst,x_tilde,x_t):
    """
    Calcule la norme d'une solution ou d'un array de solutions
    """

    if not x_tilde.size: # si vide (pas de bifurcation de ce type détectée)
        return np.array([[]])

    if norme == '2':
        return np.sqrt(np.einsum('ijk,ijk->ik',x_tilde,x_tilde,optimize=True))
    elif norme == 'inf':
        return np.amax(np.abs(x_t),axis=1)
    elif norme == 'p2p': # peak to peak ; crete à crete
        return np.amax(x_t,axis=1) - np.amin(x_t,axis=1)
    elif norme == 'rms': # root mean square, https://fr.wikipedia.org/wiki/Valeur_efficace
        return np.sqrt(np.mean(x_t**2,axis=1))
    else :
        raise Exception('Erreur : type de norme \''+ norme +'\' non reconnu')

def init_fig_crf_cont(hbm_res,post,ddl=None):
    fig, ax = plt.subplots()
    # Afficher les fréquences propres # https://github.com/matplotlib/matplotlib/issues/13618
    # calcul ou extraction des xi
    if not 'xi' in hbm_res['input']['syst'] and hbm_res['input']['syst']['type_amort'] == 'modal':
        # 2*xi_i_omega_i
        cn = hbm_res['input']['syst']['phi_i'].T @ hbm_res['input']['syst']['C'] @ hbm_res['input']['syst']['phi_i']
        xi_i = np.diag(cn)/(2*hbm_res['input']['syst']['omega_i'])
    else:
        xi_i = hbm_res['input']['syst']['xi']
    # fréquences amorties
    ax.set_xticks(hbm_res['input']['syst']['omega_i']*np.sqrt(1 - xi_i**2), minor=True)
    ax.grid(which='minor', alpha=0.5, axis='x')
    # ajout d'un twin pour fréquence = omega/(2*np.pi) en haut
    ax_twin = ax.twiny()

    # orientation en sens croissant de l'axe des x en fonction du sens de parcours
    if hbm_res['input']['syst']['omega_start'] < hbm_res['input']['syst']['omega_end'] :
        ax.set_xlim(hbm_res['input']['syst']['omega_start'],hbm_res['input']['syst']['omega_end'])
        ax_twin.set_xlim([hbm_res['input']['syst']['omega_start']/(2*np.pi),hbm_res['input']['syst']['omega_end']/(2*np.pi)])
    else :
        ax.set_xlim(hbm_res['input']['syst']['omega_end'],hbm_res['input']['syst']['omega_start'])
        ax_twin.set_xlim([hbm_res['input']['syst']['omega_end']/(2*np.pi),hbm_res['input']['syst']['omega_start']/(2*np.pi)])
    ax_twin.set_xlabel('$f$ [Hz]')

    ax.set_xlabel('$\omega$ [rad.s-1]')

    if post['norme'] == '2' :
        if ddl is not None:
            if post['quantite']=='x_t':
                ax.set_ylabel(r'$||\widetilde{'+hbm_res['input']['syst']['ddl_visu'][ddl]+'}||_{2}$ [m]')
            elif post['quantite']=='x_t_dot':
                ax.set_ylabel(r'$||\omega\nabla\widetilde{'+hbm_res['input']['syst']['ddl_visu'][ddl]+'}||_{2}$ [m.s-1]')
            elif post['quantite']=='x_t_ddot':
                ax.set_ylabel(r'$||\omega^{2}\nabla^{2}\widetilde{'+hbm_res['input']['syst']['ddl_visu'][ddl]+'}||_{2}$ [m.s-2]')
        else:
            if post['quantite']=='x_t':
                ax.set_ylabel(r'$||\widetilde{q}||_{2}$ [m]')
            elif post['quantite']=='x_t_dot':
                ax.set_ylabel(r'$||\omega\nabla\widetilde{q}||_{2}$ [m.s-1]')
            elif post['quantite']=='x_t_ddot':
                ax.set_ylabel(r'$||\omega^{2}\nabla^{2}\widetilde{q}||_{2}$ [m.s-2]')

    elif post['norme'] == 'inf':
        if ddl is not None:
            if post['quantite']=='x_t':
                ax.set_ylabel(r'$||'+hbm_res['input']['syst']['ddl_visu'][ddl]+'$(t)$||_{\infty}$ [m]')
            elif post['quantite']=='x_t_dot':
                ax.set_ylabel(r'$||\dot{'+hbm_res['input']['syst']['ddl_visu'][ddl]+'}$(t)$||_{\infty}$ [m.s-1]')
            elif post['quantite']=='x_t_ddot':
                ax.set_ylabel(r'$||\ddot{'+hbm_res['input']['syst']['ddl_visu'][ddl]+'}$(t)$||_{\infty}$ [m.s-2]')
        else:
            if post['quantite']=='x_t':
                ax.set_ylabel(r'$||q$(t)$||_{\infty}$ [m]')
            elif post['quantite']=='x_t_dot':
                ax.set_ylabel(r'$||\dot{q}$(t)$||_{\infty}$ [m.s-1]')
            elif post['quantite']=='x_t_ddot':
                ax.set_ylabel(r'$||\ddot{q}$(t)$||_{\infty}$ [m.s-2]')

    elif post['norme'] == 'p2p':
        if ddl is not None:
            if post['quantite']=='x_t':
                ax.set_ylabel(r'$'+hbm_res['input']['syst']['ddl_visu'][ddl]+'$(t)$_{cc/2}$ [m]')
            elif post['quantite']=='x_t_dot':
                ax.set_ylabel(r'$\dot{'+hbm_res['input']['syst']['ddl_visu'][ddl]+'}$(t)$_{cc/2}$ [m.s-1]')
            elif post['quantite']=='x_t_ddot':
                ax.set_ylabel(r'$\ddot{'+hbm_res['input']['syst']['ddl_visu'][ddl]+'}$(t)$_{cc/2}$ [m.s-2]')
        else:
            if post['quantite']=='x_t':
                ax.set_ylabel(r'$||q$(t)$||_{cc/2}$ [m]')
            elif post['quantite']=='x_t_dot':
                ax.set_ylabel(r'$||\dot{q}$(t)$||_{cc/2}$ [m.s-1]')
            elif post['quantite']=='x_t_ddot':
                ax.set_ylabel(r'$||\ddot{q}$(t)$||_{cc/2}$ [m.s-2]')

    elif post['norme'] == 'rms':
        if ddl is not None:
            if post['quantite']=='x_t':
                ax.set_ylabel(r'RMS($'+hbm_res['input']['syst']['ddl_visu'][ddl]+'$(t)) [m]')
            elif post['quantite']=='x_t_dot':
                ax.set_ylabel(r'RMS($\dot{'+hbm_res['input']['syst']['ddl_visu'][ddl]+'}$(t)) [m.s-1]')
            elif post['quantite']=='x_t_ddot':
                ax.set_ylabel(r'RMS($\ddot{'+hbm_res['input']['syst']['ddl_visu'][ddl]+'}$(t)) [m.s-2]')
        else:
            if post['quantite']=='x_t':
                ax.set_ylabel(r'RMS($q$(t)) [m]')
            elif post['quantite']=='x_t_dot':
                ax.set_ylabel(r'RMS($\dot{q}$(t)) [m.s-1]')
            elif post['quantite']=='x_t_ddot':
                ax.set_ylabel(r'RMS($\ddot{q}$(t)) [m.s-2]')
    return fig, ax
def fig_crf_cont(hbm_res,post):

    colors = post['colors']

    if 'crf' in hbm_res:
        if 'frf' in hbm_res: # c'est modifié :)
             x_tilde_lin = np.moveaxis(hbm_res['frf']['x_tilde'].reshape((hbm_res['input']['solv']['N'],hbm_res['input']['syst']['n_ddl'],-1)), 0, 1)
             norme_lin = norme_result(post['norme'],hbm_res['input']['solv'],hbm_res['input']['syst'],x_tilde_lin,hbm_res['frf'][post['quantite']])

        """
        # ensemble des ddls
        fig, ax = init_fig_crf_cont(hbm_res,post)
        fig.suptitle('aperçu global')

        # quantité : déplacement 'x_t' ; vitesse 'x_t_dot' ; accélération 'x_t_ddot'
        ax.plot(hbm_res['crf']['omega'], hbm_res['crf']['norme'][post['quantite']][post['norme']][hbm_res['input']['syst']['ddl_nl'],:].T, linestyle='-', c=colors['soft_gray'], alpha=0.7)
        for ddl in post['idx_ddl']:
            ax.scatter(hbm_res['crf']['omega'], hbm_res['crf']['norme'][post['quantite']][post['norme']][ddl,:], c=hbm_res['stab']['color_sol'][hbm_res['input']['stab']['ref']], s=15)
            # frf
            if post['hbm_lin']:
                frf_lines = matplotlib.collections.LineCollection([np.column_stack((hbm_res['frf']['omega'],norme_lin[ddl,:]))],linestyle='--',color=colors['soft_gray'],alpha=0.4)
                ax.add_collection(frf_lines, autolim=False)

        if post['save_fig']:
            # pour visualiser rapidement si le calcul à donner qqch
            plt.savefig(hbm_res['input']['syst']['rep_sortie']+'/figures/crf/crf_all.png')
        """

        for ddl in post['idx_ddl']:
            fig, ax = init_fig_crf_cont(hbm_res,post,ddl)
            # crf
            # quantité : déplacement 'x_t' ; vitesse 'x_t_dot' ; accélération 'x_t_ddot'
            ax.plot(hbm_res['crf']['omega'], hbm_res['crf']['norme'][post['quantite']][post['norme']][ddl,...], linestyle='-', c=colors['soft_gray'], alpha=0.7)
            ax.scatter(hbm_res['crf']['omega'], hbm_res['crf']['norme'][post['quantite']][post['norme']][ddl,...], c=hbm_res['stab']['color_sol'][hbm_res['input']['stab']['ref']], s=15)

            # mode nl
            if 'mnl' in hbm_res:
                ax.plot(hbm_res['mnl']['omega'], hbm_res['mnl']['norme'][post['quantite']][post['norme']][ddl,...],color='darkgray',linestyle='dashed',lw=1.5)
                ax.scatter(hbm_res['mnl']['omega'], hbm_res['mnl']['norme'][post['quantite']][post['norme']][ddl,...],c='r',s=15,marker='x')

            # bifurcations
            if hbm_res['input']['stab']['stab']:

                # Points limites
                norme_LP = norme_result(post['norme'],hbm_res['input']['solv'],hbm_res['input']['syst'],hbm_res['stab']['bifurcations']['Limit_Points']['x_tilde'],hbm_res['stab']['bifurcations']['Limit_Points'][post['quantite']])
                # Points fourches (branch point)
                norme_BP = norme_result(post['norme'],hbm_res['input']['solv'],hbm_res['input']['syst'],hbm_res['stab']['bifurcations']['Branch_Points']['x_tilde'],hbm_res['stab']['bifurcations']['Branch_Points'][post['quantite']])
                # Bifurcations Neimark_Sacker
                norme_NS = norme_result(post['norme'],hbm_res['input']['solv'],hbm_res['input']['syst'],hbm_res['stab']['bifurcations']['Neimark_Sacker']['x_tilde'],hbm_res['stab']['bifurcations']['Neimark_Sacker'][post['quantite']])
                # Bifurcations Period_Doubling
                norme_PD = norme_result(post['norme'],hbm_res['input']['solv'],hbm_res['input']['syst'],hbm_res['stab']['bifurcations']['Period_Doubling']['x_tilde'],hbm_res['stab']['bifurcations']['Period_Doubling'][post['quantite']])
                # Neutral_saddle points
                norme_Nsp = norme_result(post['norme'],hbm_res['input']['solv'],hbm_res['input']['syst'],hbm_res['stab']['bifurcations']['Neutral_saddle']['x_tilde'],hbm_res['stab']['bifurcations']['Neutral_saddle'][post['quantite']])

                if hbm_res['stab']['bifurcations']['Limit_Points']['omega'].size:
                    ax.scatter(hbm_res['stab']['bifurcations']['Limit_Points']['omega'],norme_LP[ddl,:],marker='$LP$',s=100,c='none',edgecolors='gold')

                if hbm_res['stab']['bifurcations']['Branch_Points']['omega'].size:
                    ax.scatter(hbm_res['stab']['bifurcations']['Branch_Points']['omega'],norme_BP[ddl,:],marker='$BP$',s=100,c='none',edgecolors='indigo',zorder=5)

                if hbm_res['stab']['bifurcations']['Neimark_Sacker']['omega'].size:
                    ax.scatter(hbm_res['stab']['bifurcations']['Neimark_Sacker']['omega'],norme_NS[ddl,:],marker='$NS$',s=100,c='none',edgecolors='deepskyblue')

                if hbm_res['stab']['bifurcations']['Period_Doubling']['omega'].size:
                    ax.scatter(hbm_res['stab']['bifurcations']['Period_Doubling']['omega'],norme_PD[ddl,:],marker='$PD$',s=100,c='none',edgecolors='royalblue')

                if hbm_res['stab']['bifurcations']['Neutral_saddle']['omega'].size:
                    ax.scatter(hbm_res['stab']['bifurcations']['Neutral_saddle']['omega'],norme_Nsp[ddl,:],marker='$SP$',s=100,c='none',edgecolors='saddlebrown')

            # seuil de contact fixe
            if hbm_res['input']['syst']['profil_contact'] == 'cst' and post['quantite']=='x_t' and np.array([s in hbm_res['input']['syst']['ddl_visu'][ddl] for s in ['x', 'y', 'q', 'r']]).any():
                ax.hlines(hbm_res['input']['syst']['d_t'][ddl],xmin=hbm_res['input']['syst']['omega_start'],xmax=hbm_res['input']['syst']['omega_end'],color='gray',linestyle='-',linewidth=2,alpha=0.6)

            # frf
            if 'frf' in hbm_res:
                x_tilde_lin = np.moveaxis(hbm_res['frf']['x_tilde'].reshape((hbm_res['input']['solv']['N'],hbm_res['input']['syst']['n_ddl'],-1)), 0, 1)
                norme_lin = norme_result(post['norme'],hbm_res['input']['solv'],hbm_res['input']['syst'],x_tilde_lin,hbm_res['frf'][post['quantite']])
                """
                Pour ignorer automatiquement la frf dans l'autoscaling de matplotlib
                https://stackoverflow.com/questions/7386872/make-matplotlib-autoscaling-ignore-some-of-the-plots
                """
                frf_lines = matplotlib.collections.LineCollection([np.column_stack((hbm_res['frf']['omega'],norme_lin[ddl,...]))],linestyle='--',color=colors['soft_gray'],alpha=0.4)
                ax.add_collection(frf_lines, autolim=False)

    elif 'mnl' in hbm_res:
        for ddl in post['idx_ddl']:
            fig, ax = init_fig_crf_cont(hbm_res,post,ddl)
            ax.plot(hbm_res['mnl']['omega'], hbm_res['mnl']['norme'][post['quantite']][post['norme']][ddl,...].T,color='darkgray',linestyle='dashed',lw=1.5)
            ax.scatter(hbm_res['mnl']['omega'], hbm_res['mnl']['norme'][post['quantite']][post['norme']][ddl,...].T,c='r',s=15,marker='x')

    return fig, ax 