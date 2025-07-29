from bs4 import BeautifulSoup
import sys
import os
from pathlib import Path

# Change these scenarios as needed
scenarios = {
    "Q1": "31_S1906M_ITALY",
    "Q2": "32_S1905M_ENGLAND",
    "Q3": "62_F1906M_GERMANY",
    "Q4": "78_F1904M_AUSTRIA"
}

# Argument should be python generate_title.py Q1
user_choice = sys.argv[1].upper()
selected_scenario = scenarios[user_choice]
game_id, season_phase, power = selected_scenario.split("_")


# Create body
soup = BeautifulSoup("<html><head><title>Diplomacy Game</title></head><body></body></html>", "html.parser")
body = soup.body

# ----- game_state -----
div_game_state = soup.new_tag("div", attrs={"class": "game_state"})
html_content = (
    f"Imagine you are playing as {power.title()} in this round. "
    f'<img src="https://raw.githubusercontent.com/ALLAN-DIP/diplomacy-wizard-study/refs/heads/main/dipnet/svgs/cicero/output_{game_id}_{season_phase}.svg" '
    f'height="800" alt="Diplomacy Game"><br>\n&nbsp;'
)
div_game_state.append(BeautifulSoup(html_content, "html.parser"))
body.append(div_game_state)

# ----- game_history -----
div_game_history = soup.new_tag("div", attrs={"class": "game_history"})
video_html = (
    'Here is a story of the game from start until now: <br/>\n'
    f'<video width="600" controls=""><source type="video/mp4" src="https://github.com/ALLAN-DIP/diplomacy-wizard-study/raw/refs/heads/main/dipnet/mp4/output_{game_id}_{season_phase}.mp4"> '
    'Your browser does not support the video tag.</video>\n'
    '<br>\n&nbsp;'
)
div_game_history.append(BeautifulSoup(video_html, "html.parser"))
body.append(div_game_history)

# ----- sugg-TB side-self -----
sugg_tb_side_self_div = soup.new_tag("div", attrs={
    "class": "sugg-TB side-self",
    "style": "display: none;"
})
p_sugg = soup.new_tag("p")
p_sugg.string = "Here are some suggestions:"
sugg_tb_side_self_div.append(p_sugg)

base_dir = os.path.dirname(__file__)
suggestion_path = os.path.normpath(os.path.join(base_dir, "..", "dipnet", "html", f"output_{game_id}_{season_phase}_{power.upper()}_best.html"))

with open(suggestion_path, "r", encoding="utf-8") as f:
    ul_html = f.read()
    sugg_tb_side_self_div.append(BeautifulSoup(ul_html, "html.parser"))
body.append(sugg_tb_side_self_div)

# ----- sugg-VB side-self -----
sugg_vb_side_self_div = soup.new_tag("div", attrs={
    "class": "sugg-VB side-self",
    "style": "display: none;"
})
p_sugg = soup.new_tag("p")
p_sugg.string = "Here are some suggestions:"
sugg_vb_side_self_div.append(p_sugg)

html_content = (
    f'<img src="https://raw.githubusercontent.com/ALLAN-DIP/diplomacy-wizard-study/refs/heads/main/dipnet/svgs/cicero/output_{game_id}_{season_phase}_{power.upper()}_best.svg" '
    f'height="800" alt="Diplomacy Game"><br>\n&nbsp;'
)
sugg_vb_side_self_div.append(BeautifulSoup(html_content, "html.parser"))
body.append(sugg_vb_side_self_div)

# ----- friction-YCO ------
yco_friction_div = soup.new_tag("div", attrs={"class": "friction-YCO"})
fill_tag = soup.new_tag("span", style="color: red;")
fill_tag.string = "[FILL]"
yco_friction_div.append(fill_tag)
body.append(yco_friction_div)

# ----- sugg-TB side-other -----
sugg_tb_side_other_div = soup.new_tag("div", attrs={
    "class": "sugg-TB side-other",
    "style": "display: none;"
})
p_sugg = soup.new_tag("p")
p_sugg.string = "Here are some suggestions that we would have given to other players:"
sugg_tb_side_other_div.append(p_sugg)

base_dir = os.path.dirname(__file__)
suggestion_path = os.path.normpath(os.path.join(base_dir, "..", "dipnet", "html", f"output_{game_id}_{season_phase}_~{power.upper()}_best.html"))

with open(suggestion_path, "r", encoding="utf-8") as f:
    ul_html = f.read()
    sugg_tb_side_other_div.append(BeautifulSoup(ul_html, "html.parser"))
body.append(sugg_tb_side_other_div)

# ----- sugg-TKT side-other -----
sugg_tkt_side_other_div = soup.new_tag("div", attrs={
    "class": "sugg-TKT side-other",
    "style": "display: none;"
})

p_sugg = soup.new_tag("p")
p_sugg.string = "Here are some suggestions that we would have given to other players:"
sugg_tkt_side_other_div.append(p_sugg)

base_dir = os.path.dirname(__file__)
suggestion_path = os.path.normpath(os.path.join(base_dir, "..", "dipnet", "html", f"output_{game_id}_{season_phase}_~{power.upper()}.html"))

with open(suggestion_path, "r", encoding="utf-8") as f:
    ul_html = f.read()
    sugg_tkt_side_other_div.append(BeautifulSoup(ul_html, "html.parser"))
body.append(sugg_tkt_side_other_div)

# ----- sugg-VB side-other -----
sugg_vb_side_other = soup.new_tag("div", attrs={
    "class": "sugg-VB side-other",
    "style": "display: none;"
})
p_sugg = soup.new_tag("p")
p_sugg.string = "Here are some suggestions that we would have given to other players:"
sugg_vb_side_other.append(p_sugg)

html_content = (
    f'<img src="https://raw.githubusercontent.com/ALLAN-DIP/diplomacy-wizard-study/refs/heads/main/dipnet/svgs/cicero/output_{game_id}_{season_phase}_all-{power.upper()}_best.svg" '
    f'height="800" alt="Diplomacy Game"><br>\n&nbsp;'
)
sugg_vb_side_other.append(BeautifulSoup(html_content, "html.parser"))
body.append(sugg_vb_side_other)

# ---- sugg-VKT side-other -----
sugg_vkt_side_other = soup.new_tag("div", attrs={
    "class": "sugg-VKT side-other",
    "style": "display: none;"
})
p_sugg = soup.new_tag("p")
p_sugg.string = "Here are some suggestions that we would have given to other players:"
sugg_vkt_side_other.append(p_sugg)

country_styles = {
    "AUSTRIA": "#e25033",
    "ENGLAND": "darkviolet",
    "FRANCE": "royalblue",
    "GERMANY": "#c1a790",
    "ITALY": "#c1a790", # I'm not sure what color this should be
    "RUSSIA": "#757d91",
    "TURKEY": "#e1cc32",
}

other_powers_container = soup.new_tag("div")

for country, color in sorted(country_styles.items()):  # Alphabetical
    if country == power.upper():
        continue  # Skip current country 

    details_tag = soup.new_tag("details", attrs={
        "style": "margin-bottom: 1em; border: 1px solid #ccc; border-radius: 5px;"
    })

    summary_tag = soup.new_tag("summary", attrs={
        "style": f"padding: 0.5em; font-weight: bold; background-color: {color}; color: white; cursor: pointer;"
    })
    summary_tag.string = country
    details_tag.append(summary_tag)

    inner_div = soup.new_tag("div", attrs={
        "style": "padding: 0.5em; background: #f9f9f9;"
    })

    img_tag = soup.new_tag("img", attrs={
        "src": f"https://raw.githubusercontent.com/ALLAN-DIP/diplomacy-wizard-study/refs/heads/main/dipnet/svgs/cicero/output_{season_phase}_{country}.svg",
        "height": "600",
        "alt": "Diplomacy Game"
    })
    inner_div.append(img_tag)
    details_tag.append(inner_div)

    other_powers_container.append(details_tag)

nbsp_tag = soup.new_string("\u00a0")
other_powers_container.append(nbsp_tag)

sugg_vkt_side_other.append(other_powers_container)
body.append(sugg_vkt_side_other)

# ---- Final prompt -----

order_prompt = soup.new_tag("p")
order_prompt.string = "Select your orders for the following units:"
body.append(order_prompt)

print(body.decode_contents())

with open("output.html", "w", encoding="utf-8") as f:
    f.write(body.decode_contents())