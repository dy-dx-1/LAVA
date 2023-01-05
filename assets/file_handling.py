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

def get_hbm_params(hbm_res:dict)->str: 
    n_harm = hbm_res['input']['solv']['n_harm']
    n_t = hbm_res['input']['solv']['n_t']
    nu = hbm_res['input']['solv']['nu']
    return f"n_harm = {n_harm} | n_t = {n_t} | nu = {nu}"

def generate_slider_stylesheet(hbm_res:dict)->str:
    """
    Fonction qui permet de colorer le slider groove en fonction d'une liste de couleurs provenant
    de l'analyse de stabilité hbm_res['stab']['color_sol'][self.hbm_res['input']['stab']['ref']]
    """
    color_range = hbm_res['stab']['color_sol'][hbm_res['input']['stab']['ref']]
    groove_color_range = 'stop:0 ' + color_range[0]
    current_color = color_range[0]
    for i in range(0, len(color_range), 1):
        if color_range[i] == current_color:
            continue
        else:
            current_color = color_range[i]
            groove_color_range += ', stop:' + str((2 * i - 1) / 2 / len(color_range)) + ' ' + color_range[
                i - 1] + ', stop:' + str((2 * i) / 2 / len(color_range)) + ' ' + color_range[i]
    groove_color_range += ', stop:1 ' + color_range[-1]
    groove_color = groove_color_range
    return f"""
    QSlider::groove:horizontal {{
    border: 1px solid #999999;
    height: 8px; 
    border-color: black;
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, {groove_color});
    margin: -4px 0;
    }}
    QSlider::handle:horizontal {{
    background-color: "colors['dark_gray']";
    border: 1px solid #5c5c5c;
    border-radius: 0px;
    border-color: black;
    height: 12px;
    width: 6px;
    margin: -8px 2; 
    }}""" 
