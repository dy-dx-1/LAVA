# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 13:10:41 2020

@author: fanny
"""

import os
import numpy as np
import calc_norme, reshape_hbm
from math import log10
import export_funcs as ef


#%%
# Définition de la fonction export_CRF
def get_CRF(hbm_res,visual,fname,x_lim,y_lim,x_ticks_loc,y_ticks_loc,x_ticks_lab,y_ticks_lab,y_axis_expo):
    """
    hbm_res : dictionnaire résultats HBM
    visual : dictionnaire des infos à visualiser
    fname : nom du fichier courant
    x_lim, y_lim : [xmin, xmax] de l'objet AxesSubplot ax_CRF0 etc...
    x_ticks_loc, y_ticks_loc : the x,y ticks as a list of locations (minor=False)
    x_ticks_lab, y_ticks_lab : the x,y major ticklabels as a list of text instances (minor=False, which=None)
    y_axis_expo : text instance de l'exposant du y axis si exposant il y a, sinon vide ('')
    """
    fname = fname + '_crf'
    syst = hbm_res['input']['syst']
    solv = hbm_res['input']['solv']

    # si pas de dossier tikz/CRF/fname en créer un
    if not os.path.exists('tikz/CRF/'+fname):
        os.mkdir('tikz/CRF/'+fname)


    """
    La fonction export_CRF va - écrire les fichiers .txt des données associées puis ;
                              - écrire le fichier .tex qui appellera les .txt via la commande \input{***} lors de la compilation pdflatex.
    """

    # ---- Début de l'écriture des différents .txt requis par le fichier .tex -------

    # FRF
    try :
        flag_FRF = 1
        """
        # Vérification
        plt.plot(hbm_res['frf']['omega'],hbm_res['norme_lin'],color = 'gray',linestyle='--')
        """
        file = open('FRF.txt','w')
        file.write('\\addplot [%\n')
        file.write('color=gray!50,%\n')
        file.write('thin%\n')
        file.write(']\n')
        file.write('coordinates{%\n')
        for k in range(0,len(hbm_res['frf']['omega'])):
            file.write('('+str(hbm_res['frf']['omega'][k])+','+str(hbm_res['norme_lin'][k])+')'+'\n')
        file.write('};')
        file.close()

    except KeyError:
        flag_FRF = 0
        pass

    if hbm_res['input']['stab']['stab']:
        # CRF
        # On récupère les indices des solutions stables et instables
        idx_S = np.where(np.asarray(hbm_res['stab']['statut_stab'][hbm_res['input']['stab']['ref']])=='S')[0]
        idx_I = np.where(np.asarray(hbm_res['stab']['statut_stab'][hbm_res['input']['stab']['ref']])=='I')[0]

        # puis on scinde les indices en différents tronçons (branches) S et I
        idx_branches_S = ef.consecutive(idx_S)
        idx_branches_I = ef.consecutive(idx_I)

        # Ecriture des fichiers stable+i+.txt
        for i,branch in enumerate(idx_branches_S):
            omega_branch = hbm_res['crf']['omega'][branch]
            x_norme_branch = hbm_res['norme_cont'][branch]

            """
            # Vérification
            plt.plot(omega_branch,x_norme_branch,linestyle='-', c=colors['orange'], alpha=0.7)
            """

            file = open('stable'+str(i)+'.txt','w')
            file.write('\\addplot [%\n')
            file.write('color=orangepoly,%\n')
            file.write('solid,thick,smooth%\n')
            file.write(']\n')
            file.write('coordinates{%\n')
            for k in range(0,len(omega_branch)):
                file.write('('+str(omega_branch[k])+','+str(x_norme_branch[k])+')'+'\n')
            file.write('};')
            file.close()

        # Ecriture des fichiers instable+i+.txt
        for i,branch in enumerate(idx_branches_I) :
            omega_branch = hbm_res['crf']['omega'][branch]
            x_norme_branch = hbm_res['norme_cont'][branch]

            """
            # Vérification
            plt.plot(omega_branch,x_norme_branch,linestyle='-', c=colors['rouge'], alpha=0.7)
            """

            file = open('instable'+str(i)+'.txt','w')
            file.write('\\addplot [%\n')
            file.write('color=orangepoly,%\n')
            file.write('densely dashed,thick,smooth,%\n')
            file.write(']\n')
            file.write('coordinates{%\n')
            for k in range(0,len(omega_branch)):
                file.write('('+str(omega_branch[k])+','+str(x_norme_branch[k])+')'+'\n')
            file.write('};')
            file.close()

        # LP
        if hbm_res['stab']['bifurcations']['Limit_Points']['omega']:
            file = open('LP.txt','w')
            file.write('\\addplot[only marks,%\n')
            file.write('color=gold,%\n')
            file.write('draw=black,%\n')
            file.write('very thin,%\n')
            file.write('mark=*,%\n')
            file.write('mark options={scale=0.55}%\n')
            # file.write('mark=text,%\n')
            # file.write('text mark as node=true,%\n')
            # file.write('text mark=\\textbf{\\textsf{LP}},%\n')
            # file.write('text mark style={%\n')
            # file.write('draw opacity=0,%\n')
            # file.write('font=\\tiny,%\n')
            # file.write('},%\n')
            file.write(']\n')
            file.write('coordinates{%\n')
            for i,omega_LP in enumerate(hbm_res['stab']['bifurcations']['Limit_Points']['omega']) :
                x_norme_LP = calc_norme.result(visual,solv,syst,hbm_res['stab']['bifurcations']['Limit_Points']['x_tilde'][i],\
                                                   hbm_res['stab']['bifurcations']['Limit_Points'][visual['quantite']][i])
                """
                # Vérification
                plt.scatter(omega_LP,x_norme_LP, marker='$LP$', s=100,c='none',edgecolors='gold')
                """


                file.write('('+str(omega_LP)+','+str(x_norme_LP[0])+')'+'\n')
            file.write('};')
            file.close()

        # BP
        if hbm_res['stab']['bifurcations']['Branch_Points']['omega']:
            file = open('BP.txt','w')
            file.write('\\addplot[only marks,%\n')
            file.write('color=vertpoly,%\n')
            file.write('draw=black,%\n')
            file.write('very thin,%\n')
            file.write('mark=diamond*,%\n')
            file.write('mark options={scale=0.65}%\n')
            # file.write('mark=text,%\n')
            # file.write('text mark as node=true,%\n')
            # file.write('text mark=\\textbf{\\textsf{BP}},%\n')
            # file.write('text mark style={%\n')
            # file.write('draw opacity=0,%\n')
            # file.write('font=\\tiny,%\n')
            # file.write('},%\n')
            file.write(']\n')
            file.write('coordinates{%\n')
            for i,omega_BP in enumerate(hbm_res['stab']['bifurcations']['Branch_Points']['omega']) :
                x_norme_BP = calc_norme.result(visual,solv,syst,hbm_res['stab']['bifurcations']['Branch_Points']['x_tilde'][i],\
                                                   hbm_res['stab']['bifurcations']['Branch_Points'][visual['quantite']][i])

                """
                # Vérification
                plt.scatter(omega_BP,x_norme_BP, marker='$BP$', s=100,c='none',edgecolors='indigo')
                """

                file.write('('+str(omega_BP)+','+str(x_norme_BP[0])+')'+'\n')
            file.write('};')
            file.close()

        # NS
        if hbm_res['stab']['bifurcations']['Neimark_Sacker']['omega']:
            file = open('NS.txt','w')
            file.write('\\addplot[only marks,%\n')
            # file.write('color=deepskyblue,%\n')
            file.write('color=bleupoly,%\n')
            file.write('draw=black,%\n')
            file.write('very thin,%\n')
            file.write('mark=triangle*,%\n')
            file.write('mark options={scale=0.7}%\n')
            # file.write('mark=text,%\n')
            # file.write('text mark as node=true,%\n')
            # file.write('text mark=\\textbf{\\textsf{NS}},%\n')
            # file.write('text mark style={%\n')
            # file.write('draw opacity=0,%\n')
            # file.write('font=\\tiny,%\n')
            # file.write('},%\n')
            file.write(']\n')

            file.write('coordinates{%\n')
            for i,omega_NS in enumerate(hbm_res['stab']['bifurcations']['Neimark_Sacker']['omega']) :
                x_norme_NS = calc_norme.result(visual,solv,syst,hbm_res['stab']['bifurcations']['Neimark_Sacker']['x_tilde'][i],\
                                                   hbm_res['stab']['bifurcations']['Neimark_Sacker'][visual['quantite']][i])

                """
                # Vérification
                plt.scatter(omega_NS,x_norme_NS, marker='$NS$', s=100,c='none',edgecolors='deepskyblue')
                """

                file.write('('+str(omega_NS)+','+str(x_norme_NS[0])+')'+'\n')
            file.write('};')
            file.close()

        # PD
        if hbm_res['stab']['bifurcations']['Period_Doubling']['omega']:
            file = open('PD.txt','w')
            file.write('\\addplot[only marks,%\n')
            file.write('color=royalblue,%\n')
            file.write('draw=black,%\n')
            file.write('very thin,%\n')
            file.write('mark=square*,%\n')
            file.write('mark options={scale=0.55}%\n')
            # file.write('mark=text,%\n')
            # file.write('text mark as node=true,%\n')
            # file.write('text mark=\\textbf{\\textsf{PD}},%\n')
            # file.write('text mark style={%\n')
            # file.write('draw opacity=0,%\n')
            # file.write('font=\\tiny,%\n')
            # file.write('},%\n')
            file.write(']\n')

            file.write('coordinates{%\n')
            for i,omega_PD in enumerate(hbm_res['stab']['bifurcations']['Period_Doubling']['omega']) :
                x_norme_PD = calc_norme.result(visual,solv,syst,hbm_res['stab']['bifurcations']['Period_Doubling']['x_tilde'][i],\
                                                   hbm_res['stab']['bifurcations']['Period_Doubling'][visual['quantite']][i])

                """
                # Vérification
                plt.scatter(omega_PD,x_norme_PD, marker='$PD$', s=100,c='none',edgecolors='royalblue')
                """

                file.write('('+str(omega_PD)+','+str(x_norme_PD[0])+')'+'\n')
            file.write('};')
            file.close()


    else :
        # Ecriture de la CRF sans stabilité
        file = open('crf_nostab.txt','w')
        file.write('\\addplot [%\n')
        file.write('color=bleupoly,%\n')
        file.write('solid,thick,smooth%\n')
        file.write(']\n')
        file.write('coordinates{%\n')
        for k in range(0,len(hbm_res['crf']['omega'])):
            file.write('('+str(hbm_res['crf']['omega'][k])+','+str(hbm_res['norme_cont'][k])+')'+'\n')
        file.write('};')
        file.close()


    # ---- Début de l'écriture du fichier .tex  -------
    #
    file = open(fname+'.tex','w')

    # importer les packages
    ef.get_tikzbegin(file)
    # couleurs poly
    ef.get_poly_colors(file)
    # couleurs bifurcations
    ef.get_bifurc_colors(file)

    # Fonction pour plot le contenu du graphique
    file.write('% fonction pour plot le contenu du graphique\n')
    file.write('\\newcommand*\myplots[1][]{\n')

    # FRF
    if flag_FRF :
        file.write('% FRF\n')
        file.write('\\input{FRF.txt}\n')

    # Tracer des fréquences propres du systèmes, il faut renseigner la clé 'omega_i' avec une petite boucle pour faire plusieurs \draw, voir le wiki, je n'ai pas le code sous les yeux...
    file.write('% fréquence(s) de résonance \n')

    mask_omega_i_xlim = np.where(np.logical_and(syst['omega_i']>x_lim[0],\
                                               syst['omega_i']<x_lim[1]))

    omega_i_xlim = syst['omega_i'][mask_omega_i_xlim]

    for i in range(0,len(omega_i_xlim)):
        file.write('\\draw[gray, densely dashed] (axis cs:'+str(omega_i_xlim[i])+','+str(y_lim[0]) \
                   + ') -- (axis cs:'+str(omega_i_xlim[i])+','+str(y_lim[1]) \
                   + ');\n')
    if hbm_res['input']['stab']['stab']:
        # Stable
        file.write('% stable\n')
        for i in range(0,len(idx_branches_S),1):
            file.write('\\input{stable'+str(i)+'.txt}\n')
        # Instable
        file.write('% instable\n')
        for j in range(0,len(idx_branches_I),1):
            file.write('\\input{instable'+str(j)+'.txt}\n')
        file.write('% bifurcations\n')
        # LP
        if hbm_res['stab']['bifurcations']['Limit_Points']['omega']:
            file.write('% LP\n')
            file.write('\\input{LP.txt}\n')
        # BP
        if hbm_res['stab']['bifurcations']['Branch_Points']['omega']:
            file.write('% BP\n')
            file.write('\\input{BP.txt}\n')
        # NS
        if hbm_res['stab']['bifurcations']['Neimark_Sacker']['omega']:
            file.write('% NS\n')
            file.write('\\input{NS.txt}\n')
        # PD
        if hbm_res['stab']['bifurcations']['Period_Doubling']['omega']:
            file.write('% PD\n')
            file.write('\\input{PD.txt}\n')
    else:
        file.write('% crf , sans stabilité\n')
        file.write('\\input{crf_nostab.txt}\n')

    file.write('}\n')
    file.write('%\n')
    file.write('\\begin{document}\n')
    file.write('\\begin{tikzpicture}[]\n')
    file.write('\\begin{axis}[\n')
    file.write('width=10cm,\n')
    file.write('height=6cm,\n')
    file.write('restrict x to domain*='+str(0.8*x_lim[0])+':'+str(1.2*x_lim[1])+',\n')
    file.write('restrict y to domain*='+str(0.8*y_lim[0])+':'+str(1.2*y_lim[1])+',\n')
    file.write('each nth point={1},\n')
    file.write('scale only axis,\n')
    file.write('xmin='+str(x_lim[0])+', xmax='+str(x_lim[1])+',\n')
    file.write('ymin='+str(y_lim[0])+', ymax='+str(y_lim[1])+',\n')


    # on convertit ici en chaîne de caractères les ticks de matplotlib (ils sont généralement mieux que ceux de tikz)
    x_ticks_loc_tikz = ef.get_tikz_ticks_loc(x_ticks_loc)
    y_ticks_loc_tikz = ef.get_tikz_ticks_loc(y_ticks_loc)

    # on récupère les tickslabel de matplotlib de la même manière
    x_ticks_lab_tikz = ef.get_tikz_ticks_lab(x_ticks_lab,visual)
    y_ticks_lab_tikz = ef.get_tikz_ticks_lab(y_ticks_lab,visual)

    file.write('xtick='+x_ticks_loc_tikz+',\n')
    file.write('xticklabels='+x_ticks_lab_tikz+',\n')
    file.write('ytick='+y_ticks_loc_tikz+',\n')
    file.write('yticklabels='+y_ticks_lab_tikz+',\n')
    file.write('scaled y ticks = false,\n')
    file.write('xtick pos=left,\n')
    file.write('ytick pos=left,\n')

    file.write('xlabel={$\omega$ [rad$\cdot$s$^{-1}$]},\n')

    # ylabel du numero_ddl + norme
    if not len(y_axis_expo):

        # Norme euclidienne
        if visual['norme'] == '2' :
            if visual['quantite']=='x_t':
                #file.write('ylabel={$\\vert\\vert \\tilde{\\bm{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} \\vert\\vert_{2}$ [m]},\n')
                file.write('ylabel={$\\vert\\vert \\bm{'+ syst['ddl_visu'][visual['numero_ddl']] +'} (t)\\vert\\vert_{2}$ [m]},\n')
            elif visual['quantite']=='x_t_dot':
                #file.write('ylabel={$\\vert\\vert \\tilde{\\bm{\\dot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}}} \\vert\\vert_{2}$ [m$\cdot$s$^{-1}$]},\n')
                file.write('ylabel={$\\vert\\vert \\bm{\\dot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} (t)\\vert\\vert_{2}$ [m$\cdot$s$^{-1}$]},\n')
            elif visual['quantite']=='x_t_ddot':
                #file.write('ylabel={$\\vert\\vert \\tilde{\\bm{\\ddot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} \\vert\\vert_{2}$ [m$\cdot$s$^{-2}$]},\n')
                file.write('ylabel={$\\vert\\vert \\bm{\\ddot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} (t)\\vert\\vert_{2}$ [m$\cdot$s$^{-2}$]},\n')

        # Norme infinie
        elif visual['norme'] == 'INF':
            if visual['quantite']=='x_t':
                 file.write('ylabel={$\\vert\\vert \\bm{'+ syst['ddl_visu'][visual['numero_ddl']] +'} (t)\\vert\\vert_{\infty}$ [m]},\n')
            elif visual['quantite']=='x_t_dot':
                 file.write('ylabel={$\\vert\\vert \\bm{\\dot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} (t)\\vert\\vert_{\infty}$ [m$\cdot$s$^{-1}$]},\n')
            elif visual['quantite']=='x_t_ddot':
                 file.write('ylabel={$\\vert\\vert \\bm{\\ddot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} (t)\\vert\\vert_{\infty}$ [m$\cdot$s$^{-2}$]},\n')

        # Norme peak-to-peak
        elif visual['norme'] == 'P2P':
            if visual['quantite']=='x_t':
                file.write('ylabel={$\\bm{'+ syst['ddl_visu'][visual['numero_ddl']] +'} (t)_{cc/2}$ [m]},\n')
            elif visual['quantite']=='x_t_dot':
                file.write('ylabel={$\\bm{\\dot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} (t)_{cc/2}$ [m$\cdot$s$^{-1}$]},\n')
            elif visual['quantite']=='x_t_ddot':
                file.write('ylabel={$\\bm{\\ddot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} (t)_{cc/2}$ [m$\cdot$s$^{-2}$]},\n')
    else:
        # conversion unicode vers str utf8 puis strip des deux premiers caractères '1e'
        y_axis_expo = ef.unicode2str(y_axis_expo[2:])
        # Norme euclidienne
        if visual['norme'] == '2' :
            if visual['quantite']=='x_t':
                #file.write('ylabel={$\\vert\\vert \\tilde{\\bm{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} \\vert\\vert_{2}$ [$\\times 10^{'+y_axis_expo+'}$~m]},\n')
                file.write('ylabel={$\\vert\\vert \\bm{'+ syst['ddl_visu'][visual['numero_ddl']] +'} (t)\\vert\\vert_{2}$ [$\\times 10^{'+y_axis_expo+'}$~m]},\n')
            elif visual['quantite']=='x_t_dot':
                #file.write('ylabel={$\\vert\\vert \\tilde{\\bm{\\dot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}}} \\vert\\vert_{2}$ [$\\times 10^{'+y_axis_expo+'}$~m$\cdot$s$^{-1}$]},\n')
                file.write('ylabel={$\\vert\\vert \\bm{\\dot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} (t)\\vert\\vert_{2}$ [$\\times 10^{'+y_axis_expo+'}$~m$\cdot$s$^{-1}$]},\n')
            elif visual['quantite']=='x_t_ddot':
                #file.write('ylabel={$\\vert\\vert \\tilde{\\bm{\\ddot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} \\vert\\vert_{2}$ [$\\times 10^{'+y_axis_expo+'}$~m$\cdot$s$^{-2}$]},\n')
                file.write('ylabel={$\\vert\\vert \\bm{\\ddot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} (t)\\vert\\vert_{2}$ [$\\times 10^{'+y_axis_expo+'}$~m$\cdot$s$^{-2}$]},\n')


        # Norme infinie
        elif visual['norme'] == 'INF':
            if visual['quantite']=='x_t':
                 file.write('ylabel={$\\vert\\vert \\bm{'+ syst['ddl_visu'][visual['numero_ddl']] +'} (t)\\vert\\vert_{\infty}$ [$\\times 10^{'+y_axis_expo+'}$~m]},\n')
            elif visual['quantite']=='x_t_dot':
                 file.write('ylabel={$\\vert\\vert \\bm{\\dot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} (t)\\vert\\vert_{\infty}$ [$\\times 10^{'+y_axis_expo+'}$~m$\cdot$s$^{-1}$]},\n')
            elif visual['quantite']=='x_t_ddot':
                 file.write('ylabel={$\\vert\\vert \\bm{\\ddot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} (t)\\vert\\vert_{\infty}$ [$\\times 10^{'+y_axis_expo+'}$~m$\cdot$s$^{-2}$]},\n')

        # Norme peak-to-peak
        elif visual['norme'] == 'P2P':
            if visual['quantite']=='x_t':
                file.write('ylabel={$\\bm{'+ syst['ddl_visu'][visual['numero_ddl']] +'} (t)_{cc/2}$ [$\\times 10^{'+y_axis_expo+'}$~m]},\n')
            elif visual['quantite']=='x_t_dot':
                file.write('ylabel={$\\bm{\\dot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} (t)_{cc/2}$ [$\\times 10^{'+y_axis_expo+'}$~m$\cdot$s$^{-1}$]},\n')
            elif visual['quantite']=='x_t_ddot':
                file.write('ylabel={$\\bm{\\ddot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}} (t)_{cc/2}$ [$\\times 10^{'+y_axis_expo+'}$~m$\cdot$s$^{-2}$]},\n')


    file.write('scale=1,axis background/.style={fill=white},\n')
    file.write('axis on top]\n')

    if ('gap' in syst) and (visual['quantite'] == 'x_t') and \
                np.array([s in syst['ddl_visu'][visual['numero_ddl']] for s in ['x', 'r']]).any():
        file.write('% contact à seuil fixe \n')
        file.write('\\draw [black!50]('+str(x_lim[0])+','+str(syst['gap'])+') -- ('+str(x_lim[1])+','+str(syst['gap'])+');% node[above,pos=.06] {\\sf seuil};\n')
    file.write('% plot de la CRF \n')
    file.write('\\myplots\n')
    file.write('\\end{axis}\n')
    file.write('\\end{tikzpicture}\n')
    file.write('\\end{document}\n')
    file.close()

    # compilation pdflatex de fname.tex
    os.system('pdflatex -interaction=batchmode '+fname+'.tex 1>/dev/null')
    # tout ce qui est autour de pdflatex + fname.tex est là pour virer les informations de compilation qui viennent polluer la console
    # https://latex.org/forum/viewtopic.php?t=4315
    # sinon simplement os.system('pdflatex '+fname+'.tex') pour avoir info compilation

    # organisation des fichiers
    if flag_FRF :
        os.system('mv FRF* tikz/CRF/'+fname)


    if hbm_res['input']['stab']['stab']:
        os.system('mv stable* tikz/CRF/'+fname)
        os.system('mv instable* tikz/CRF/'+fname)

        if hbm_res['stab']['bifurcations']['Limit_Points']['omega']:
            os.system('mv LP.txt tikz/CRF/'+fname)
        if hbm_res['stab']['bifurcations']['Branch_Points']['omega']:
            os.system('mv BP.txt tikz/CRF/'+fname)
        if hbm_res['stab']['bifurcations']['Neimark_Sacker']['omega']:
            os.system('mv NS.txt tikz/CRF/'+fname)
        if hbm_res['stab']['bifurcations']['Period_Doubling']['omega']:
            os.system('mv PD.txt tikz/CRF/'+fname)
    else:
        os.system('mv crf_nostab* tikz/CRF/'+fname)

    os.system('mv '+fname+'* tikz/CRF/'+fname)

    # ouverture du pdf
    os.system('evince tikz/CRF/'+fname+'/'+fname+'.pdf &')# & permet de laisser la main sur la console donc sur le GUI

    print('GUI2TikZ : création tikz/CRF/'+fname+' OK')

    return

#%%
# Définition de la fonction get_evol_temp

def get_evol_temp(hbm_res,visual,fname,value,y_lim,y_ticks_loc,y_ticks_lab,y_axis_expo):
    """
    hbm_res : dictionnaire résultats HBM
    visual : dictionnaire des infos à visualiser
    fname : nom du fichier courant
    value : valeur courante du slider_CRF
    y_lim : [ymin, ymax] de l'objet AxesSubplot self.evol_temp
    y_ticks_loc : the y ticks as a list of locations (minor=False)
    y_ticks_lab : the y major ticklabels as a list of text instances (minor=False, which=None)
    y_axis_expo : text instance de l'exposant du y axis si exposant il y a, sinon vide ('')
    """
    syst = hbm_res['input']['syst']
    solv = hbm_res['input']['solv']

    omega =  np.round(hbm_res['crf']['omega'][value],5)
    freq = np.round(omega / (2*np.pi),5)

    # si pas de dossier tikz/freq_temp/fname/temp/ en créer un
    if not os.path.exists('tikz/freq_temp/'+fname+'/temp'):
        os.mkdir('tikz/freq_temp/'+fname)
        os.mkdir('tikz/freq_temp/'+fname+'/temp')


    """
    La fonction get_evol_temp va - écrire les fichiers .txt des données associées puis ;
                                 - écrire le fichier .tex qui appellera les .txt via la commande \input{***} lors de la compilation pdflatex.
    """
    n_t = solv['n_t']

    # pour la détection des instants de contact
    # on récupère le déplacement pour tous les ddls
    x_t = hbm_res['crf']['x_t'][:, value]
    # on reshape les ddl en colonnes
    x_t_reshaped = reshape_hbm.x_t_3d(x_t,n_t)
    # on concatène -T/2  0 : 0 à T : T +3T/2
    x_nT = np.concatenate((x_t_reshaped[n_t//2:,0,visual['numero_ddl']],x_t_reshaped[:,0,visual['numero_ddl']],x_t_reshaped[:n_t//2,0,visual['numero_ddl']]),axis=0)

    # pour visualisation quantité
    # on récupère la bonne quantité pour tous les ddls
    q_t = hbm_res['crf'][visual['quantite']][:, value]
    # on reshape les ddl en colonnes
    q_t_reshaped = reshape_hbm.x_t_3d(q_t,n_t)
    q_T = q_t_reshaped[:,0,visual['numero_ddl']]
    q_Tleft = np.append(q_t_reshaped[n_t//2:,0,visual['numero_ddl']],q_t_reshaped[0,0,visual['numero_ddl']])
    q_Tright = np.append(q_t_reshaped[-1,0,visual['numero_ddl']],q_t_reshaped[:n_t//2,0,visual['numero_ddl']])

    tau_nT = np.linspace(-np.pi,3*np.pi,2*n_t,endpoint=False)
    tau_T = np.linspace(0,2*np.pi,n_t,endpoint=False)
    tau_left = np.append(np.linspace(-np.pi,0,n_t//2,endpoint=False),0.)
    tau_right = np.append(tau_T[-1],np.linspace(2*np.pi,3*np.pi,n_t//2,endpoint=False))

    # ecriture du fichier moving_gap_nT.txt si requis
    if 'moving_gap' in syst :

        if len(syst['ddl_nl']) > 1:

            moving_gap = (syst['moving_gap'].reshape((min(syst['noeud_front'],syst['ddl_nl'].shape[0]),-1)).T)
            moving_gap = moving_gap[:,visual['numero_ddl']//syst['ddl_noeud']]
        else:
            moving_gap = syst['moving_gap'].flatten()

        moving_gap_nT = np.concatenate((moving_gap[n_t//2:],moving_gap,moving_gap[:n_t//2]),axis=0)

        if visual['quantite']=='x_t':
            file = open('moving_gap_nT.txt','w')
            file.write('\\addplot [name path=gap,%\n')
            file.write('color=black!50,%\n')
            file.write('smooth,%\n')
            file.write(']\n')
            file.write('coordinates{%\n')
            for k in range(0,len(moving_gap_nT)):
                file.write('('+str(tau_nT[k])+','+str(moving_gap_nT[k])+')'+'\n')
            file.write('};')
            file.close()

    # Couleur période
    if hbm_res['stab']['statut_stab'][hbm_res['input']['stab']['ref']][value]=='S':
        c_T = 'orangepoly'
    elif hbm_res['stab']['statut_stab'][hbm_res['input']['stab']['ref']][value]=='I':
        c_T = 'rougepoly'
    else:
        c_T = 'bleupoly'


    # ecriture du fichier q_T.txt
    file = open('q_T.txt','w')
    file.write('\\addplot [%\n')
    file.write('color='+c_T+',%\n')
    file.write('solid,very thick,smooth,%\n')
    file.write(']\n')
    file.write('coordinates{%\n')
    for k in range(0,len(q_T)):
        file.write('('+str(tau_T[k])+','+str(q_T[k])+')'+'\n')
    file.write('};')
    file.close()

    # ecriture du fichier q_Tleft.txt
    file = open('q_Tleft.txt','w')
    file.write('\\addplot [%\n')
    file.write('color='+c_T+'!55,%\n')
    file.write('solid,very thick,smooth,%\n')
    file.write(']\n')
    file.write('coordinates{%\n')
    for k in range(0,len(q_Tleft)):
        file.write('('+str(tau_left[k])+','+str(q_Tleft[k])+')'+'\n')
    file.write('};')
    file.close()

    # ecriture du fichier q_Tright.txt
    file = open('q_Tright.txt','w')
    file.write('\\addplot [%\n')
    file.write('color='+c_T+'!55,%\n')
    file.write('solid,very thick,smooth,%\n')
    file.write(']\n')
    file.write('coordinates{%\n')
    for k in range(0,len(q_Tright)):
        file.write('('+str(tau_right[k])+','+str(q_Tright[k])+')'+'\n')
    file.write('};')
    file.close()


    # ---- Début de l'écriture du fichier .tex  -------
    file = open(fname + '_evoltemp' + '.tex','w')

    # importer les packages
    ef.get_tikzbegin(file)
    # couleurs poly
    ef.get_poly_colors(file)
    # constantes : pi, 2pi et 3pi
    ef.get_pi(file)

    # Fonction pour plot le contenu du graphique
    file.write('% fonction pour plot le contenu du graphique\n')
    file.write('\\newcommand*\myplots[1][]{\n')

    # input si contact à seuil fixe
    if ('gap' in syst) :

        # On récupère les indices des solutions x_t>gap
        idx_contact = np.where(x_nT > syst['gap'])[0]

        # si on détecte des contacts
        if idx_contact.size:
            # puis on scinde les indices en différents instants de contact
            idx_insts_contact = ef.consecutive(idx_contact)

            contact_startstop = [(tau_nT[inst_contact][0],tau_nT[inst_contact][-1]) for inst_contact in idx_insts_contact]
            file.write('% zones grises instants de contact \n')
            for i,inst_contact in enumerate(idx_insts_contact) :
                ef.get_rect_filldraw(file,contact_startstop[i],y_lim)

    if ('gap' in syst) and (visual['quantite']=='x_t') and \
        np.array([s in syst['ddl_visu'][visual['numero_ddl']] for s in ['x','r']]).any():
        file.write('% contact à seuil fixe : gap \n')
        file.write('\\draw[black!50,name path=gap]('+str(tau_nT[0])+','+str(syst['gap'])+') -- ('+str(tau_nT[-1])+','+str(syst['gap'])+');% node[above,pos=.1] {\\sf carter};\n')
        file.write('\\path[name path=axis] (axis cs:-\\pi,'+str(y_lim[1])+') -- (axis cs:\\tpi,'+str(y_lim[1])+');\n')
        file.write('\\addplot[bottom color=gray!30,top color=softgray!50] fill between[of = gap and axis];\n')

    # input si contact à seuil variable
    if 'moving_gap' in syst :

        # On récupère les indices des solutions x_t>moving_gap
        idx_contact = np.where(x_nT > np.ravel(moving_gap_nT))[0]

        # si on détecte des contacts
        if idx_contact.size:
            # puis on scinde les indices en différents instants de contact
            idx_insts_contact = ef.consecutive(idx_contact)

            contact_startstop = [(tau_nT[inst_contact][0],tau_nT[inst_contact][-1]) for inst_contact in idx_insts_contact]
            file.write('% zones grises instants de contact \n')
            for i,inst_contact in enumerate(idx_insts_contact) :
                ef.get_rect_filldraw(file,contact_startstop[i],y_lim)

    if 'moving_gap' in syst and visual['quantite']=='x_t' and\
        np.array([s in syst['ddl_visu'][visual['numero_ddl']] for s in ['x','r']]).any():
        file.write('% contact à seuil variable : moving_gap \n')
        file.write('\\input{moving_gap_nT.txt}\n')
        file.write('\\path[name path=axis] (axis cs:-\\pi,'+str(y_lim[1])+') -- (axis cs:\\tpi,'+str(y_lim[1])+');\n')
        file.write('\\addplot[bottom color=gray!30,top color=softgray!50] fill between [of = gap and axis];\n')

    # délimitations pour mise en évidence de la période
    file.write('% lignes verticales pointillées à tau = 0 et T \n')
    file.write('\\draw [black!35,thick,dashed](axis cs: 0.0, '+str(y_lim[0])+') -- (axis cs: 0.0, '+str(y_lim[1])+');\n')
    file.write('\\draw [black!35,thick,dashed](axis cs: \\dpi, '+str(y_lim[0])+') -- (axis cs: \\dpi, '+str(y_lim[1])+');\n')

    file.write('% solution obtenue par HBM à f = '+str(freq)+' Hz, soit omega = '+str(omega)+' rad.s-1 pour '+fname+'\n')
    file.write('\\input{q_Tleft.txt}\n')
    file.write('\\input{q_Tright.txt}\n')
    file.write('\\input{q_T.txt}\n')

    file.write('}\n')
    file.write('%\n')
    file.write('\\begin{document}\n')
    file.write('\\begin{tikzpicture}[]\n')
    file.write('\\begin{axis}[\n')
    file.write('width=10cm,\n')
    file.write('height=6cm,\n')
    file.write('each nth point={5},\n') # à adapter ?
    file.write('scale only axis,\n')
    file.write('xmin=-\\pi, xmax=\\tpi,\n')
    file.write('ymin='+str(y_lim[0])+', ymax='+str(y_lim[1])+',\n')

    # on convertit ici en chaîne de caractères les ticks de matplotlib (ils sont généralement mieux que ceux de tikz)
    y_ticks_loc_tikz = ef.get_tikz_ticks_loc(y_ticks_loc)

    # on récupère les tickslabel de matplotlib de la même manière
    y_ticks_lab_tikz = ef.get_tikz_ticks_lab(y_ticks_lab,visual)

    file.write('xtick={-\\pi, 0, \\pi, \\dpi, \\tpi},\n')    # {-pi,0,pi,2pi,3pi}
    file.write('xticklabels={$-T/2$,$0$,$T/2$,$T$,$3T/2$},\n')
    file.write('ytick='+y_ticks_loc_tikz+',\n')
    file.write('yticklabels='+y_ticks_lab_tikz+',\n')
    file.write('xtick pos=left,\n')
    file.write('ytick pos=left,\n')
    file.write('scaled y ticks = false,\n')

    file.write('xlabel={temps norm.},\n')

    if not len(y_axis_expo):
        # ylabel du numéro ddl
        if visual['quantite']=='x_t':
            file.write('ylabel={$'+ syst['ddl_visu'][visual['numero_ddl']] +'(t)$ [m]},\n')
        elif visual['quantite']=='x_t_dot':
            file.write('ylabel={$\\dot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}(t)$ [m$\cdot$s$^{-1}$]},\n')
        elif visual['quantite']=='x_t_ddot':
            file.write('ylabel={$\\ddot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}(t)$ [m$\cdot$s$^{-2}$]},\n')
    else :
        # conversion unicode vers str utf8 puis strip des deux premiers caractères '1e'
        y_axis_expo = ef.unicode2str(y_axis_expo[2:])
        # ylabel du numéro ddl
        if visual['quantite']=='x_t':
            file.write('ylabel={$'+ syst['ddl_visu'][visual['numero_ddl']] +'(t)$ [$\\times 10^{'+y_axis_expo+'}$~m]},\n')
        elif visual['quantite']=='x_t_dot':
            file.write('ylabel={$\\dot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}(t)$ [$\\times 10^{'+y_axis_expo+'}$~m$\cdot$s$^{-1}$]},\n')
        elif visual['quantite']=='x_t_ddot':
            file.write('ylabel={$\\ddot{'+ syst['ddl_visu'][visual['numero_ddl']] +'}(t)$ [$\\times 10^{'+y_axis_expo+'}$~m$\cdot$s$^{-2}$]},\n')

    file.write('scale=1,axis background/.style={fill=white},\n')
    file.write('axis on top]\n')


    file.write('% plot de la quantité voulue \n')
    file.write('\\myplots\n')
    file.write('\\end{axis}\n')
    file.write('\\end{tikzpicture}\n')
    file.write('\\end{document}\n')
    file.close()


    # compilation pdflatex de fname.tex
    os.system('pdflatex -interaction=batchmode ' + fname + '_evoltemp' + '.tex 1>/dev/null')
    # tout ce qui est autour de pdflatex + fname.tex est là pour virer les informations de compilation qui viennent polluer la console
    # https://latex.org/forum/viewtopic.php?t=4315
    # sinon simplement os.system('pdflatex '+fname+'.tex') pour avoir info compilation

    # organisation des fichiers
    if 'moving_gap' in syst and visual['quantite']=='x_t' and \
        np.array([s in syst['ddl_visu'][visual['numero_ddl']] for s in ['x','r']]).any():
        os.system('mv moving_gap* tikz/freq_temp/'+fname+'/temp')

    os.system('mv q_T* tikz/freq_temp/'+fname+'/temp')
    os.system('mv '+fname+'* tikz/freq_temp/'+fname+'/temp')

    # ouverture du pdf
    os.system('evince tikz/freq_temp/'+fname+'/temp/'+ fname + '_evoltemp' + '.pdf &')# & permet de laisser la main sur la console donc sur le GUI

    print('GUI2TikZ : création tikz/freq_temp/'+fname+'/temp OK')
    return

#%%
# Définition de la fonction get_contrib_freq

def get_contrib_freq(hbm_res,visual,fname,value,y_lim,y_ticks_loc,y_ticks_lab):
    """
    hbm_res : dictionnaire résultats HBM
    visual : dictionnaire des infos à visualiser
    fname : nom du fichier courant
    value : valeur courante du slider_CRF
    y_lim : [ymin, ymax] de l'objet AxesSubplot self.evol_temp
    y_ticks_loc : the y ticks as a list of locations (minor=False)
    y_ticks_lab : the y major ticklabels as a list of text instances (minor=False, which=None)
    """
    fname = fname
    solv = hbm_res['input']['solv']
    syst = hbm_res['input']['syst']

    omega =  np.round(hbm_res['crf']['omega'][value],5)
    freq = np.round(omega / (2*np.pi),5)

    # si pas de dossier tikz/CRF/fname/temp/ en créer un
    if not os.path.exists('tikz/freq_temp/'+fname+'/freq'):
        os.mkdir('tikz/freq_temp/'+fname+'/freq')

    """
    La fonction get_contrib_freq va - écrire le fichier .txt des données associé puis ;
                                    - écrire le fichier .tex qui appellera le .txt via la commande \input{***} lors de la compilation pdflatex.
    """

    # indices des harmoniques
    H_range = np.arange(0,solv['n_harm']+1)

    # on récupère les contributions des harmoniques associées à la bonne quantité et avec la normalisation courante
    H_j_max = hbm_res['crf']['||H_j||_2'][visual['quantite']]['max'][:, value, visual['numero_ddl']]
    H_j_non = hbm_res['crf']['||H_j||_2'][visual['quantite']]['non'][:, value, visual['numero_ddl']]
    H_j_sum = hbm_res['crf']['||H_j||_2'][visual['quantite']]['sum'][:, value, visual['numero_ddl']]

    # Couleur période
    if hbm_res['stab']['statut_stab'][hbm_res['input']['stab']['ref']][value]=='S':
        c_T = 'orangepoly'
    elif hbm_res['stab']['statut_stab'][hbm_res['input']['stab']['ref']][value]=='I':
        c_T = 'rougepoly'
    else:
        c_T = 'bleupoly'

    # écriture du fichier H_j_max.txt
    if visual['norme_harm'] == 'max' :
        file = open('H_j_max.txt','w')
        file.write('\\addplot [%\n')
        file.write('fill='+c_T+']\n')
        file.write('coordinates{%\n')
        for j in range(0,len(H_range)):
            file.write('('+str(H_range[j])+','+str(H_j_max[j])+')'+'\n')
        file.write('};')
        file.close()

    # écriture du fichier H_j_non.txt
    elif visual['norme_harm'] == 'non' :
        file = open('H_j_non.txt','w')
        file.write('\\addplot [%\n')
        file.write('fill='+c_T+']\n')
        file.write('coordinates{%\n')
        for j in range(0,len(H_range)):
            file.write('('+str(H_range[j])+','+str(H_j_non[j])+')'+'\n')
        file.write('};')
        file.close()

    # écriture du fichier H_j_sum.txt
    elif visual['norme_harm'] == 'sum' :
        file = open('H_j_sum.txt','w')
        file.write('\\addplot [%\n')
        file.write('fill='+c_T+']\n')
        file.write('coordinates{%\n')
        for j in range(0,len(H_range)):
            file.write('('+str(H_range[j])+','+str(H_j_sum[j])+')'+'\n')
        file.write('};')
        file.close()

    """
    La fonction get_contrib_freq va - écrire le fichier .txt des données associé puis ;
                                    - écrire le fichier .tex qui appellera le .txt via la commande \input{***} lors de la compilation pdflatex.
    """

    # ---- Début de l'écriture du fichier .tex  -------
    file = open(fname + '_spectre' + '.tex','w')

    # importer les packages
    ef.get_tikzbegin(file)
    # couleurs poly
    ef.get_poly_colors(file)

    # Fonction pour plot le contenu du graphique
    file.write('% fonction pour plot le contenu du graphique\n')
    file.write('\\newcommand*\myplots[1][]{\n')

    file.write('% solution obtenue par HBM à f = '+str(freq)+' Hz, soit omega = '+str(omega)+' rad.s-1 pour '+fname+'\n')

    y_max = 1.1
    if visual['norme_harm'] == 'max' :
        file.write('% contributions fréquentielles normalisées max \n')
        file.write('\\input{H_j_max.txt}\n')
        file.write('%\\input{H_j_non.txt}\n')
        file.write('%\\input{H_j_sum.txt}\n')
        y_min = np.min(H_j_max)*0.5

    elif visual['norme_harm'] == 'non' :
        file.write('% contributions fréquentielles non normalisées \n')
        file.write('%\\input{H_j_max.txt}\n')
        file.write('\\input{H_j_non.txt}\n')
        file.write('%\\input{H_j_sum.txt}\n')
        y_min = np.min(H_j_non)*0.5
        y_max = np.max(H_j_non)*1.3

    elif visual['norme_harm'] == 'sum' :
        file.write('% contributions fréquentielles normalisées par la somme \n')
        file.write('%\\input{H_j_max.txt}\n')
        file.write('%\\input{H_j_non.txt}\n')
        file.write('\\input{H_j_sum.txt}\n')
        y_min = np.min(H_j_sum)*0.5

    if y_min < 1e-15:
        y_min = 1e-5


    file.write('% troncature HBM si comparaison avec du l\'intégration temporelle \n')
    file.write('%\\draw[black,thin] (axis cs:'+str(solv['n_harm'])+',1e-4) -- node[midway, rotate = 90, yshift =0.25cm]{$H = '+str(solv['n_harm'])+'$} (axis cs:'+str(solv['n_harm'])+',1.1);\n')
    file.write('}\n')

    file.write('%\n')
    file.write('\\begin{document}\n')
    file.write('\\begin{tikzpicture}\n')
    file.write('\\begin{axis}[\n')
    file.write('ymode=log,\n')
    file.write('log origin=infty,\n')
    file.write('width=10cm,\n')
    file.write('height=6cm,\n')
    file.write('scale only axis,\n')
    file.write('ybar, bar width=.125cm,ymin = '+str(y_min)+',ymax='+str(y_max)+',xmin=-0.9,xmax='+str(solv['n_harm']+0.9)+',\n') # xmax = nb harmoniques + 0,9
    file.write('%xtick={1,5,10,15,20,25,30,35,40},\n')
    file.write('%xticklabels = {1,5,10,15,20,25,30,35,40},\n')
    file.write('xtick pos=left,\n')
    file.write('ytick pos=left,\n')
    file.write('xlabel={harmonique $j$},\n')

    # ylabel
    if visual['norme_harm'] == 'max' :
        file.write('ylabel={$\\tilde{\\bm{'+ syst['ddl_visu'][visual['numero_ddl']] +'}}(j)$ norm.  max.},\n')
    elif visual['norme_harm'] == 'non' :
        file.write('ylabel={$\\tilde{\\bm{'+ syst['ddl_visu'][visual['numero_ddl']] +'}}(j)$},\n')
    elif visual['norme_harm'] == 'sum' :
        file.write('ylabel={$\\tilde{\\bm{'+ syst['ddl_visu'][visual['numero_ddl']] +'}}(j)$ norm som.},\n')
    file.write('scale=1,\n')
    file.write('tick align=inside,\n')
    file.write('axis on top]\n')

    file.write('% plot des contributions \n')
    file.write('\\myplots%\n')
    file.write('\\end{axis}%\n')
    file.write('\\end{tikzpicture}\n')
    file.write('\\end{document}\n')
    file.close()


    # compilation pdflatex de fname.tex
    os.system('pdflatex -interaction=batchmode ' + fname + '_spectre' + '.tex 1>/dev/null')
    # tout ce qui est autour de pdflatex + fname.tex est là pour virer les informations de compilation qui viennent polluer la console
    # https://latex.org/forum/viewtopic.php?t=4315
    # sinon simplement os.system('pdflatex '+fname+'.tex') pour avoir info compilation

    # organisation des fichiers
    if visual['norme_harm'] == 'max' :
        os.system('mv H_j_max* tikz/freq_temp/'+fname+'/freq')
    elif visual['norme_harm'] == 'non' :
        os.system('mv H_j_non* tikz/freq_temp/'+fname+'/freq')
    elif visual['norme_harm'] == 'sum' :
        os.system('mv H_j_sum* tikz/freq_temp/'+fname+'/freq')

    os.system('mv '+fname+'* tikz/freq_temp/'+fname+'/freq')

    # ouverture du pdf
    os.system('evince tikz/freq_temp/'+fname+'/freq/' + fname + '_spectre' + '.pdf &')# & permet de laisser la main sur la console donc sur le GUI

    print('GUI2TikZ : création tikz/freq_temp/'+fname+'/freq OK')


    return



#%%
# Définition de la fonction get_efforts_nl

def get_efforts_nl(hbm_res,visual,fname,value,y_lim,y_ticks_loc,y_ticks_lab,y_axis_expo):
    """
    hbm_res : dictionnaire résultats HBM
    visual : dictionnaire des infos à visualiser
    fname : nom du fichier courant
    value : valeur courante du slider_CRF
    y_lim : [ymin, ymax] de l'objet AxesSubplot self.effrots_nl
    y_ticks_loc : the y ticks as a list of locations (minor=False)
    y_ticks_lab : the y major ticklabels as a list of text instances (minor=False, which=None)
    y_axis_expo : text instance de l'exposant du y axis si exposant il y a, sinon vide ('')
    """
    fname = fname + '_fnl'
    syst = hbm_res['input']['syst']
    solv = hbm_res['input']['solv']

    omega =  np.round(hbm_res['crf']['omega'][value],5)
    freq = np.round(omega / (2*np.pi),5)


    # Si pas de dossier tikz/efforts_nl/fname/ en créer un
    if not os.path.exists('tikz/efforts_nl/'+fname):
        os.mkdir('tikz/efforts_nl/'+fname)

    n_t = solv['n_t']

    # on récupère les efforts nl pour tous les q ddls nl
    # temporel
    f_nl_t = hbm_res['crf']['f_nl_t'][:, value]
    # on reshape les ddl en colonnes
    f_nl_t_reshaped = reshape_hbm.x_t_3d(f_nl_t,n_t)
    # fréquentiel reconstruit
    f_nl_tilde = hbm_res['crf']['f_nl_tilde'][:, value]
    # on reshape les ddl en colonnes
    f_nl_tilde_reshaped = reshape_hbm.x_t_3d(f_nl_tilde,n_t)

    try :
        idx_ddl_nl = np.where(syst['ddl_nl']==visual['numero_ddl'])[0][0]

        f_nl_t_T = f_nl_t_reshaped[:,0,idx_ddl_nl]
        f_nl_t_Tleft = np.append(f_nl_t_T[n_t//2:],f_nl_t_T[0])
        f_nl_t_Tright = np.append(f_nl_t_T[-1],f_nl_t_T[:n_t//2])

        f_nl_tilde_T = f_nl_tilde_reshaped[:,0,idx_ddl_nl]
        f_nl_tilde_Tleft = np.append(f_nl_tilde_T[n_t//2:],f_nl_tilde_T[0])
        f_nl_tilde_Tright = np.append(f_nl_tilde_T[-1],f_nl_tilde_T[:n_t//2])

    except IndexError:
        f_nl_t_T = np.zeros(n_t)
        f_nl_t_Tleft = np.append(f_nl_t_T[n_t//2:],f_nl_t_T[0])
        f_nl_t_Tright = np.append(f_nl_t_T[-1],f_nl_t_T[:n_t//2])

        f_nl_tilde_T =  np.zeros(n_t)
        f_nl_tilde_Tleft = np.append(f_nl_tilde_T[n_t//2:],f_nl_tilde_T[0])
        f_nl_tilde_Tright = np.append(f_nl_tilde_T[-1],f_nl_tilde_T[:n_t//2])

    tau_T = np.linspace(0,2*np.pi,n_t,endpoint=False)
    tau_left = np.append(np.linspace(-np.pi,0,n_t//2,endpoint=False),0.)
    tau_right = np.append(tau_T[-1],np.linspace(2*np.pi,3*np.pi,n_t//2,endpoint=False))


    # temporel
    # ecriture du fichier f_nl_t_T.txt
    file = open('f_nl_t_T.txt','w')
    file.write('\\addplot [%\n')
    file.write('color=black,%\n')
    file.write('solid,very thick,%\n')
    file.write(']\n')
    file.write('coordinates{%\n')
    for k in range(0,len(tau_T)):
        file.write('('+str(tau_T[k])+','+str(f_nl_t_T[k])+')'+'\n')
    file.write('};')
    file.close()

    # ecriture du fichier f_nl_t_Tleft.txt
    file = open('f_nl_t_Tleft.txt','w')
    file.write('\\addplot [%\n')
    file.write('color=black!55,%\n')
    file.write('solid,very thick,%\n')
    file.write(']\n')
    file.write('coordinates{%\n')
    for k in range(0,len(tau_left)):
        file.write('('+str(tau_left[k])+','+str(f_nl_t_Tleft[k])+')'+'\n')
    file.write('};')
    file.close()

    # ecriture du fichier f_nl_t_Tright.txt
    file = open('f_nl_t_Tright.txt','w')
    file.write('\\addplot [%\n')
    file.write('color=black!55,%\n')
    file.write('solid,very thick,%\n')
    file.write(']\n')
    file.write('coordinates{%\n')
    for k in range(0,len(tau_right)):
        file.write('('+str(tau_right[k])+','+str(f_nl_t_Tright[k])+')'+'\n')
    file.write('};')
    file.close()

    # fréquentiel reconstruit
    # ecriture du fichier f_nl_tilde_T.txt
    file = open('f_nl_tilde_T.txt','w')
    file.write('\\addplot [%\n')
    file.write('color=orangepoly,%\n')
    file.write('solid,very thick,smooth,%\n')
    file.write(']\n')
    file.write('coordinates{%\n')
    for k in range(0,len(tau_T)):
        file.write('('+str(tau_T[k])+','+str(f_nl_tilde_T[k])+')'+'\n')
    file.write('};')
    file.close()

    # ecriture du fichier f_nl_tilde_Tleft.txt
    file = open('f_nl_tilde_Tleft.txt','w')
    file.write('\\addplot [%\n')
    file.write('color=orangepoly!55,%\n')
    file.write('solid,very thick,smooth,%\n')
    file.write(']\n')
    file.write('coordinates{%\n')
    for k in range(0,len(tau_left)):
        file.write('('+str(tau_left[k])+','+str(f_nl_tilde_Tleft[k])+')'+'\n')
    file.write('};')
    file.close()

    # ecriture du fichier f_nl_tilde_Tright.txt
    file = open('f_nl_tilde_Tright.txt','w')
    file.write('\\addplot [%\n')
    file.write('color=orangepoly!55,%\n')
    file.write('solid,very thick,smooth,%\n')
    file.write(']\n')
    file.write('coordinates{%\n')
    for k in range(0,len(tau_right)):
        file.write('('+str(tau_right[k])+','+str(f_nl_tilde_Tright[k])+')'+'\n')
    file.write('};')
    file.close()


    # ---- Début de l'écriture du fichier .tex  -------
    file = open(fname+'.tex','w')

    # Importer les packages
    ef.get_tikzbegin(file)
    # Couleurs poly
    ef.get_poly_colors(file)
    # constantes : pi, 2pi et 3pi
    ef.get_pi(file)


    # Fonction pour plot le contenu du graphique
    file.write('% fonction pour plot le contenu du graphique\n')
    file.write('\\newcommand*\myplots[1][]{\n')


    # Délimitations pour mise en évidence de la période
    file.write('% lignes verticales pointillées à tau = 0 et T \n')
    file.write('\\draw [black!35,thick,dashed](axis cs: 0.0, '+str(y_lim[0])+') -- (axis cs: 0.0, '+str(y_lim[1])+');\n')
    file.write('\\draw [black!35,thick,dashed](axis cs: \\dpi, '+str(y_lim[0])+') -- (axis cs: \\dpi, '+str(y_lim[1])+');\n')

    file.write('% solution obtenue par HBM à f = '+str(freq)+' Hz, soit omega = '+str(omega)+' rad.s-1 pour '+fname+'\n')
    file.write('% effort temporel\n')
    file.write('\\input{f_nl_t_Tleft.txt}\n')
    file.write('\\input{f_nl_t_Tright.txt}\n')
    file.write('\\input{f_nl_t_T.txt}\n')

    file.write('% effort fréquentiel reconstruit\n')
    file.write('\\input{f_nl_tilde_Tleft.txt}\n')
    file.write('\\input{f_nl_tilde_Tright.txt}\n')
    file.write('\\input{f_nl_tilde_T.txt}\n')

    file.write('}\n')
    file.write('%\n')
    file.write('\\begin{document}\n')
    file.write('\\begin{tikzpicture}[]\n')
    file.write('\\begin{axis}[\n')
    file.write('width=10cm,\n')
    file.write('height=6cm,\n')
    file.write('each nth point={5},\n') # à adapter ?
    file.write('scale only axis,\n')
    file.write('xmin=-\\pi, xmax=\\tpi,\n')
    file.write('ymin='+str(y_lim[0])+', ymax='+str(y_lim[1])+',\n')

    # on convertit ici en chaîne de caractères les ticks de matplotlib (ils sont généralement mieux que ceux de tikz)
    y_ticks_loc_tikz = ef.get_tikz_ticks_loc(y_ticks_loc)

    # on récupère les tickslabel de matplotlib de la même manière
    y_ticks_lab_tikz = ef.get_tikz_ticks_lab(y_ticks_lab,visual)

    file.write('xtick={-\\pi, 0, \\pi, \\dpi, \\tpi},\n')    # {-pi,0,pi,2pi,3pi}
    file.write('xticklabels={$-T/2$,$0$,$T/2$,$T$,$3T/2$},\n')
    file.write('ytick='+y_ticks_loc_tikz+',\n')
    file.write('yticklabels='+y_ticks_lab_tikz+',\n')
    # file.write('scaled y ticks = false,\n')
    file.write('xtick pos=left,\n')
    file.write('ytick pos=left,\n')
    file.write('scaled y ticks = false,\n')

    file.write('xlabel={$\\tau$ : temps norm.},\n')

    if not len(y_axis_expo):
        # ylabel du numéro ddl
        file.write('ylabel={$f^{'+str(syst['ddl_visu'][visual['numero_ddl']])+'}_{\\mathrm{nl}} (t)$ [N]},\n')

    else :
        # conversion unicode vers str utf8 puis strip des deux premiers caractères '1e'
        y_axis_expo = ef.unicode2str(y_axis_expo[2:])
        file.write('ylabel={$f^{'+str(syst['ddl_visu'][visual['numero_ddl']])+'}_{\\mathrm{nl}} (t)$ [$\\times 10^{'+y_axis_expo+'}$~N]},\n')

    file.write('scale=1,axis background/.style={fill=white},\n')
    file.write('axis on top]\n')


    file.write('% plot de la quantité voulue \n')
    file.write('\\myplots\n')
    file.write('\\end{axis}\n')
    file.write('\\end{tikzpicture}\n')
    file.write('\\end{document}\n')
    file.close()


    # compilation pdflatex de fname.tex
    os.system('pdflatex -interaction=batchmode '+fname+'.tex 1>/dev/null')
    # tout ce qui est autour de pdflatex + fname.tex est là pour virer les informations de compilation qui viennent polluer la console
    # https://latex.org/forum/viewtopic.php?t=4315
    # sinon simplement os.system('pdflatex '+fname+'.tex') pour avoir info compilation

    # organisation des fichiers
    os.system('mv f_nl_* tikz/efforts_nl/'+fname)
    os.system('mv '+fname+'* tikz/efforts_nl/'+fname)

    # ouverture du pdf
    os.system('evince tikz/efforts_nl/'+fname+'/'+fname+'.pdf &')# & permet de laisser la main sur la console donc sur le GUI

    print('GUI2TikZ : création tikz/efforts_nl/'+fname+' OK')

    return






