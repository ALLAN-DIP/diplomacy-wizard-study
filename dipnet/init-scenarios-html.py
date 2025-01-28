import pandas as pd

PARRENT_PATH = "https://raw.githubusercontent.com/ALLAN-DIP/diplomacy-wizard-study/refs/heads/main/dipnet/"
selected_games = pd.read_csv('selected_scenarios.csv')

# generating a html file as a report
with open('scenarios.html', 'w') as f:
    f.write('<html>\n')
    f.write('<head>\n')
    f.write('<title>Overview on Scenarios</title>\n')
    f.write('</head>\n')
    f.write('<body>\n')
    f.write('<h1>Scenarios</h1>\n')
    f.write('<p>Selected games from Dipnet dataset:</p>\n')
    f.write('<ul>\n')
    for i, row in selected_games.iterrows():
        game_id, gname, power = row['Game Name'].split('_')
        treatment = row['Treatment']
        suggestions = row['Suggestions (CICERO)']
        stance = row['Stance']
        level, n_units = row['Complexity'], row['# units involved']
        
        # plot the scenario for lr5 and cicero generated versions in two columns and add the treatment and suggestions and stance to the cicero ones
        f.write('<li>\n')
        f.write(f'<h2>{game_id}_{gname}_{power}</h2>\n')
        f.write(f'<p>Level: {level}, # units involved: {n_units}</p>\n')
        f.write(f'<p>Treatment: {treatment}</p>\n')
        f.write(f'<p>Suggestions: {suggestions}</p>\n')
        f.write(f'<p>Stance: {stance}</p>\n')
        f.write('<table>\n')
        f.write('<tr>\n')
        f.write('<td>\n')
        local_path_to_svg = PARRENT_PATH + f'svgs/cicero/output_{game_id}_{gname}_{power}.svg'
        f.write('[CICERO]\n')
        f.write(f'<img src="{local_path_to_svg}" width="800" height="800">\n')
        f.write('</td>\n')
        f.write('<td>\n')
        local_path_to_svg = PARRENT_PATH + f'svgs/lr5/output_{game_id}_{gname}_{power}.svg'
        f.write('[Logistics Regression]\n')
        f.write(f'<img src="{local_path_to_svg}" width="800" height="800">\n')
        f.write('</td>\n')
        f.write('</tr>\n')
        f.write('</table>\n')
        f.write('</li>\n')
        f.write('<hr>\n')

    f.write('</ul>\n')
    f.write('</body>\n')
    f.write('</html>\n')
