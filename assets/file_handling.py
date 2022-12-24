from re import search 
def get_sys_info(name:str, hbm_res:dict)->tuple:
    match = search(r"\/((?:(?!\/).)+?)\.pkl", name)
    if not match: 
        fichier = "Nom inconnu" 
    else: 
        fichier = match.group(1)
    nb_heures = round(hbm_res['crf']['temps_calcul'].get('h')) 
    nb_min = round(hbm_res['crf']['temps_calcul'].get('m')) 
    nb_s = round(hbm_res['crf']['temps_calcul'].get('s'), 2) 
    temps_calcul = f"{nb_heures} h: {nb_min} m: {nb_s} s"
    return f"Fichier: {fichier}  |  Temps de calcul: {temps_calcul}"