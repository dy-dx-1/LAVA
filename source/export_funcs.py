# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 16:18:16 2020

@author: yacola
"""

import numpy as np
import unicodedata as ud

def get_tikzbegin(file):
    file.write('\documentclass[10pt]{standalone}\n')
    file.write('% importer les packages\n')
    file.write('\\usepackage[T1]{fontenc}\n') 
    file.write('\\usepackage{times}\n') 
    file.write('\\usepackage{amsmath,color}\n')
    file.write('\\usepackage{amssymb}\n')
    file.write('\\usepackage{tikz}\n') 
    file.write('\\usepackage{pgfplots}\n') 
    file.write('\\usepackage{xcolor}\n')
    file.write('\\usepackage{textcomp,bm}\n')
    file.write('\\pgfplotsset{compat=newest}\n') 
    file.write('\\usetikzlibrary{decorations.text}\n')
    file.write('\\usepgfplotslibrary{units,fillbetween}\n')
    file.write('\\usetikzlibrary{spy,backgrounds,calc,shapes.geometric,plotmarks}\n')
    file.write('%\n')
    return

def get_poly_colors(file):
    file.write('% couleurs poly\n')
    file.write('\\definecolor{bleupoly}{RGB}{81,173,229}\n')
    file.write('\\definecolor{vertpoly}{RGB}{0,205,0}\n') 
    file.write('\\definecolor{rougepoly}{RGB}{191,32,51}\n') 
    file.write('\\definecolor{orangepoly}{RGB}{246,135,18}\n')
    file.write('\\definecolor{softgray}{rgb}{0.91,0.91,0.91}\n')
    file.write('% couleur dominante\n')
    file.write('\\definecolor{ref}{RGB}{88,139,174} % bleu "air force"\n')
    file.write('%\n')
    return

def get_pi(file):
    # constantes : pi, 2pi et 3pi
    file.write('% constantes multiples de pi \n')
    file.write('\\def\\pi{'+str(np.around(np.pi,5))+'}\n')
    file.write('\\def\\dpi{'+str(np.around(2*np.pi,5))+'}\n')
    file.write('\\def\\tpi{'+str(np.around(3*np.pi,5))+'}\n')
    file.write('%\n')
    return

def get_bifurc_colors(file):
    file.write('% couleurs bifurcations\n')
    file.write('% LP\n')
    file.write('\\definecolor{gold}{RGB}{255,215,0}\n') 
    file.write('% BP\n')
    file.write('\\definecolor{indigo}{RGB}{75,0,130}\n')
    file.write('% NS\n')
    file.write('\\definecolor{deepskyblue}{RGB}{0,191,255}\n') 
    file.write('% PD\n')
    file.write('\\definecolor{royalblue}{RGB}{0,35,102}\n')
    file.write('%\n')
    return


def consecutive(data, stepsize=1):
    """
    Permet de scinder une liste de données au niveau des discontinuités trouvées
    cf : https://stackoverflow.com/questions/7352684/how-to-find-the-groups-of-consecutive-elements-from-an-array-in-numpy
    """
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)

def get_tikz_ticks_loc(ticks_loc):
    """
    convertit des ticks loc matplotlib en un string de ticks au format tikz
    """
    return '{' + ', '.join([str(tick_loc) for tick_loc in ticks_loc]) + '}'  

def get_tikz_ticks_lab(ticks_lab,visual):
    """
    convertit les instances text de ticks_label de matplotlib en un string tickslabel au format tikz
    on concatène les listes avec ', ' entre chaque strings + remplace par visual['sep_deci'] les séparateurs décimaux points
    """
    return '{' + ', '.join([''.join(('$',unicode2str(tick_lab.get_text()),'$')) for tick_lab in ticks_lab]).replace('.', visual['sep_deci']) + '}'   


def unicode2str(unistr):
    """
    convertit correctement les unicodes obtenus via tickslabels.get_text() en strings bien compatibles avec tex
    https://stackoverflow.com/questions/15538099/conversion-of-unicode-minus-sign-from-matplotlib-ticklabels
    """
    digits = {'MINUS': u'-',
              'ZERO': u'0',
              'ONE': u'1',
              'TWO': u'2',
              'THREE': u'3',
              'FOUR': u'4',
              'FIVE': u'5',
              'SIX': u'6',
              'SEVEN': u'7',
              'EIGHT': u'8',
              'NINE': u'9',
              'STOP': u'.'}
    return ''.join([value for u in unistr for key,value in digits.items() if key in ud.name(u)])
 
def get_rect_filldraw(file,contact_startstop,y_lim):
    # coordonnées des deux extrémités opposées du rectangle
    x0 = contact_startstop[0]
    x1 = contact_startstop[1]
    y0 = y_lim[0]
    y1 = y_lim[1]    
    file.write('%\\filldraw[black!10] (axis cs: '+str(x0)+', '+str(y0)+') -- (axis cs: '+str(x1)+', '+str(y0)+') -- (axis cs: '+str(x1)+', '+str(y1)+') -- (axis cs: '+str(x0)+', '+str(y1)+') --cycle;\n')
    return

