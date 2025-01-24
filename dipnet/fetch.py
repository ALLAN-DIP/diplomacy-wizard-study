import pandas as pd
import sys
import os
import tqdm

path2files = sys.argv[1]
files = os.listdir(path2files)
selected_games = pd.read_csv('selected_games.csv')

for i, row in tqdm.tqdm(selected_games.iterrows()):
    game_id, gname, power = row['name'].split('_')

    # Loading the json file
    json_fpath = os.path.join(path2files, f'output_{game_id}_{gname}.json')
    os.system(f'cp {json_fpath} data/lr5')

    # Loading the svg file
    svg_fpath = os.path.join(path2files, f'output_{game_id}_{gname}*.svg')
    os.system(f'cp {svg_fpath} svgs/lr5')

PARRENT_PATH = "https://raw.githubusercontent.com/ALLAN-DIP/diplomacy-wizard-study/refs/heads/main/dipnet/"

# generating a html file as a report
with open('overview.html', 'w') as f:
    f.write('<html>\n')
    f.write('<head>\n')
    f.write('<title>Overview on Scenarios</title>\n')
    f.write('</head>\n')
    f.write('<body>\n')
    f.write('<h1>Scenarios</h1>\n')
    f.write('<p>Selected games from Dipnet dataset:</p>\n')
    f.write('<ul>\n')
    for i, row in selected_games.sort_values(by='n_units').iterrows():
        game_id, gname, power = row['name'].split('_')
        level, n_units = row['complexity'], row['n_units']
        f.write(f'<li>{game_id}_{gname}_{power} (Level: {level}, # units involved: {n_units})</li>\n')
        notes = row['notes']
        if notes:
            f.write(f'<p>{notes}</p>\n')
        local_path_to_svg = PARRENT_PATH + f'svgs/lr5/output_{game_id}_{gname}_{power}.svg'
        f.write(f'<img src="{local_path_to_svg}" width="800" height="800">\n')
        f.write('<hr>\n')
    f.write('</ul>\n')
    f.write('</body>\n')
    f.write('</html>\n')