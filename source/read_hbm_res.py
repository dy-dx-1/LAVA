# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 11:21:08 2018

@author: yacola
"""
import pickle

# Sauvegarde
def save_obj(obj,name):
    
    if not name.endswith('.pkl'):
        name += '.pkl'
      
    with open('save/'+ name , 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

# Lecture
def load_obj(name):
    
    if not name.endswith('.pkl'):
        name += '.pkl'
        
    with open('input/' + name , 'rb') as f:
        return pickle.load(f)
    
    
