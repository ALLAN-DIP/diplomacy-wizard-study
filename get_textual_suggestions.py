import sys
import json
import argparse

from constants import POWERS

parser = argparse.ArgumentParser(description='Extract a diplomacy JSON file move suggestions to HTML bullet points.')
parser.add_argument('path2data', type=str, help='Path to the JSON file.')
parser.add_argument('--best', action='store_true', help='Only show the best move for each unit.')
args = parser.parse_args()

def list_to_bullet_points(data, best=False):
    """Converts a nested list into a list of bullet points for each unit."""
    html = '<ul>\n'
    for unit, alts in data.items():
        if best:
            best_alt = max(alts, key=lambda x: x[1])
            html += f'  <li>{best_alt[0]}</li>\n'
        else:
            html += f'  <li>{unit}\n'
            html += f'    <ul>\n'
            for alt in alts:
                # write with 4 decimal places
                html += f'      <li>{alt[0]} (confidence: {alt[1]:.4f})</li>\n'
            html += f'    </ul>\n'
            html += f'  </li>\n'
    html += '</ul>'
    return html


path2data = args.path2data
with open(path2data, 'r') as f:
    data = json.load(f)

alternations = data["alterations"]
for power in POWERS:
    alts = {}
    for alt in alternations[power]:
        unit = ' '.join(alt[0].split(' ')[:2])
        if unit in alts:
            alts[unit].append(alt)
        else:
            alts[unit] = [alt]
    
    # Convert list to bullet points
    html_bullet_points = list_to_bullet_points(alts, best=args.best)
    print(f'<h2>{power}</h2>')
    print(html_bullet_points)
