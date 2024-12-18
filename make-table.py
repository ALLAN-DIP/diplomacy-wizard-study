import sys
import json

# Code to convert the given list to an HTML table

def list_to_html_table(data):
    """Converts a nested list into an HTML table."""
    html = '<table style="border-collapse: collapse; width: 100%; border: 1px solid black;">\n'
    html += '  <thead>\n    <tr style="background-color: #f2f2f2;">\n'
    html += '      <th style="border: 1px solid black; padding: 8px; text-align: left;">Unit</th>\n'
    html += '      <th style="border: 1px solid black; padding: 8px; text-align: left;">Action</th>\n'
    html += '      <th style="border: 1px solid black; padding: 8px; text-align: right;">Confidence</th>\n'
    html += '    </tr>\n  </thead>\n  <tbody>\n'

    for row in data:
        unit, actions = row[0], row[1:]
        first = True
        for action, prob in actions:
            html += '    <tr>\n'
            if first:
                html += f'      <td style="border: 1px solid black; padding: 8px;" rowspan="{len(actions)}">{unit}</td>\n'
                first = False
            html += f'      <td style="border: 1px solid black; padding: 8px;">{action}</td>\n'
            html += f'      <td style="border: 1px solid black; padding: 8px; text-align: right;">{prob:.3f}</td>\n'
            html += '    </tr>\n'

    html += '  </tbody>\n</table>'
    return html

def list_to_bullet_points(data):
    """Converts a nested list into a list of bullet points."""
    html = '<ul>\n'
    for row in data:
        html += f'  <li>{row[0]}</li>\n'
        html += '  <ul>\n'
        for action, prob in row[1:]:
            html += f'    <li>{action} (confidence: {prob:.3f})</li>\n'
        html += '  </ul>\n'
    html += '</ul>'
    return html

path2data = sys.argv[1]
with open(path2data, 'r') as f:
    data = json.load(f)

power = path2data.split('/')[-2].split('-')[-1]
alternations = data["alterations"][power]
alts = {}
for alt in alternations:
    unit = ' '.join(alt[0].split(' ')[:2])
    if unit in alts:
        alts[unit].append(alt)
    else:
        alts[unit] = [alt]

# Example data
data2table = [
    [x] + alts[x] for x in alts
]

# Convert list to HTML table
# html_table = list_to_html_table(data2table)
# print(html_table)

# Convert list to bullet points
html_bullet_points = list_to_bullet_points(data2table)
print(html_bullet_points)

