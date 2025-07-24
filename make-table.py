import sys
import json
from bs4 import BeautifulSoup
import textwrap
POWERS = [
    'AUSTRIA', 'ENGLAND', 'FRANCE', 'GERMANY', 'ITALY', 'RUSSIA', 'TURKEY'
]

def html_to_colored_table(input_html):
    # Country to color mapping
    color_map = {
        "AUSTRIA": "#e25033",
        "ENGLAND": "darkviolet",
        "FRANCE": "royalblue",
        "GERMANY": "#c1a790",
        "ITALY": "forestgreen",
        "RUSSIA": "#757d91",
        "TURKEY": "#e1cc32"
    }

    soup = BeautifulSoup(input_html, "html.parser")
    accordions = ""

    # Traverse all <h2> tags and associated <ul> content
    for header in soup.find_all("h2"):
        country = header.text.strip().upper()
        color = color_map.get(country, "#cccccc")

        # Accumulate content between this <h2> and the next <h2>
        content = ""
        node = header.find_next_sibling()
        while node and node.name != "h2":
            content += str(node)
            node = node.find_next_sibling()

        # Build accordion section
        section = f"""
        <details style="margin-bottom: 1em; border: 1px solid #ccc; border-radius: 5px;">
          <summary style="padding: 0.5em; font-weight: bold; background-color: {color}; color: white; cursor: pointer;">
            {country}
          </summary>
          <div style="padding: 0.5em; background: #f9f9f9;">
            {content.strip()}
          </div>
        </details>
        """
        accordions += section

    return textwrap.dedent(accordions)


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


def list_to_bullet_points_best(data):
    """Converts a nested list into a list of bullet points."""
    html = '<ul>\n'
    for row in data:
        action, prob = row[1]
        html += f'  <li>{action}</li>\n'
    html += '</ul>'
    return html

def get_data_from_file(path):
    """Reads JSON data from a file."""
    with open(path, 'r') as f:
        return json.load(f)


def get_data_table(data, power):
    """Fetches data from a JSON file and returns the relevant table."""
    if power not in data["alterations"]:
        raise ValueError(f"Power '{power}' not found in the data.")
    alternations = data["alterations"][power]
    alts = {}
    for alt in alternations:
        unit = ' '.join(alt[0].split(' ')[:2])
        if unit in alts:
            alts[unit].append(alt)
        else:
            alts[unit] = [alt]
    data2table = [
        [x] + alts[x] for x in alts
    ]
    return data2table


# Convert list to HTML table
# html_table = list_to_html_table(data2table)
# print(html_table)

if __name__ == "__main__":
    path2data = sys.argv[1]
    power = sys.argv[2]
    mode = sys.argv[3]

    data = get_data_from_file(path2data)
    if power[0] == '~':
        power_excluded = power[1:]
        result = ""
        for p in POWERS:
            if p == power_excluded:
                continue
            data2table = get_data_table(data, p)

            result += f"\n<h2>{p}</h2>\n"
            if mode == 'best':
                result += list_to_bullet_points_best(data2table)
            else:
                result += list_to_bullet_points(data2table)
        print(html_to_colored_table(result))

    else:
        data2table = get_data_table(data, power)

        if mode == 'best':
            html_bullet_points_best = list_to_bullet_points_best(data2table)
            print(html_bullet_points_best)
        else:
            # Convert list to bullet points
            html_bullet_points = list_to_bullet_points(data2table)
            print(html_bullet_points)
