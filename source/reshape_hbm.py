# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 09:43:14 2019

@author: yacola
"""

import numpy as np

def x_tilde_3d(x_tilde,N,n_ddl = None):
    """
    Reshape les variables fréquentielles avec les ddl sur l'axe 3
    """
    if not n_ddl:
        n_ddl = x_tilde.shape[0]//N

    # (n_H,nbr_sol) -> (N,n_ddl,nbr_sol)
    x_tilde_reshaped = x_tilde.reshape(N,n_ddl,-1) # Value -1 tells numpy to compute the dimension automatically.
    # (N,n_ddl,nbr_sol) -> (N,nbr_sol,n_ddl)
    x_tilde_reshaped = np.moveaxis(x_tilde_reshaped, 2, 1)
    return x_tilde_reshaped


def x_t_3d(x_t,n_t,n_ddl = None):
    """
    Reshape les variables temporelles avec les ddl sur l'axe 3
    """
    if not n_ddl:
        n_ddl = x_t.shape[0]//n_t

    # (n_t*n_ddl,nbr_sol) -> (n_ddl,n_t,nbr_sol) # not (n_t,n_ddl,nbr_sol)
    x_t_reshaped = x_t.reshape(n_ddl,n_t,-1) # Value -1 tells numpy to compute the dimension automatically.
    # (n_ddl,n_t,nbr_sol) -> (n_t,nbr_sol,n_ddl) # m is moved to the end
    x_t_reshaped = np.moveaxis(x_t_reshaped, 0, 2)
    return x_t_reshaped

