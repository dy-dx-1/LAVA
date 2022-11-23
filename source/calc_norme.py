# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 09:51:53 2018

@author: yacola
"""

import numpy as np
import reshape_hbm


def no_x_t(norme,x_tilde,i_DFT,n_t):
    """
    Calcule et renvoit la norme d'une seule solution (en déplacement) si x_t indisponible
    """
    if norme == '2':
        return np.linalg.norm(np.dot(i_DFT,x_tilde),2) # np.sqrt(np.dot(x_tilde,x_tilde))
    elif norme == 'INF':
        return  max(abs(np.dot(i_DFT,x_tilde)))
    elif norme == 'P2P' :
        return  (max(np.dot(i_DFT,x_tilde))-min(np.dot(i_DFT,x_tilde)))/2
    else :
        raise Exception('Erreur : type de norme \''+ norme +'\' non reconnu')


def result(visual,solv,syst,x_tilde,x_t):
    """
    Calcule et renvoit la norme d'une solution ou d'un array de solutions
    """
    norme = visual['norme']
    no_ddl = visual['numero_ddl']
    
    n_ddl = syst['n_ddl']
    N = solv['N']
    n_t = solv['n_t']

    # Conversion en array si besoin
    if type(x_tilde) is list:
        x_tilde = np.asarray(x_tilde).T
    if type(x_t) is list:
        x_t = np.asarray(x_t).T

    # Reshape 3D pour cas à plusieurs ddl : axe 3 = ddl
    x_t_reshaped = reshape_hbm.x_t_3d(x_t,n_t)
    x_tilde_reshaped = reshape_hbm.x_tilde_3d(x_tilde,N)

    # Calcul de la norme :
    if norme == '2':
        """
        FR  : https://www.drgoulu.com/2016/01/17/einsum/
        ENG : https://stackoverflow.com/questions/32154475/einsum-and-distance-calculations
        -> avec boucle for : 14.4 ms ± 59.4 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
        res = np.zeros((nbr_sol))
        for i in range(0,nbr_sol,1):
            res[i] = np.sqrt(np.dot(x_tilde_reshaped[:,i,no_ddl],x_tilde_reshaped[:,i,no_ddl]))
        return res
        -> avec einsum     : 139 µs  ± 285 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
        """
        return np.linalg.norm(x_t_reshaped[:,:,no_ddl],2,axis=0)# np.sqrt(np.einsum('ij,ij->j', x_tilde_reshaped[:,:,no_ddl],x_tilde_reshaped[:,:,no_ddl],optimize=True))

    elif norme == 'INF' :
        """
        res = np.zeros((nbr_sol))
        for i in range(0,nbr_sol,1):
            res[i,] = max(abs(x_t_reshaped[:,i,no_ddl]))
        return res
        -> avec boucle for : 64.2 ms ± 541 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
        -> avec np.amax :    2.78 ms ± 6.15 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
        """
        return np.amax(np.abs(x_t_reshaped[:,:,no_ddl]),axis=0)

    elif norme == 'P2P' :
        """
        res = np.zeros((nbr_sol))
        for i in range(0,nbr_sol,1):
            res[i] = (max(x_t_reshaped[:,i,no_ddl])-min(x_t_reshaped[:,i,no_ddl]))/2
        return res
        -> avec boucle for   : 121 ms ± 276 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
        -> avec np.amax/amin : 2.84 ms ± 17.5 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
        """
        return (np.amax(x_t_reshaped[:,:,no_ddl],axis=0)-np.amin(x_t_reshaped[:,:,no_ddl],axis=0))/2
    
    
    elif norme == 'MAXMIN':
        return np.hstack((np.amax(x_t_reshaped[:,:,no_ddl],axis=0)[:,None],np.amin(x_t_reshaped[:,:,no_ddl],axis=0)[:,None]))
    
    else :
        raise Exception('Erreur : type de norme \''+ norme +'\' non reconnu')
