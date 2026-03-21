import streamlit as st
import base64
import json
import os
from json import JSONDecodeError
st.set_option('client.showErrorDetails', False)
st.markdown("""
<style>
[data-testid="stToolbar"] {display: none !important;}
header {display: none !important;}
footer {display: none !important;}
[data-testid="stStatusWidget"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

hide_streamlit_style = """
<style>
div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}
div[data-testid="stDecoration"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}
div[data-testid="stStatusWidget"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}
#MainMenu {
    visibility: hidden;
    height: 0%;
}
header {
    visibility: hidden;
    height: 0%;
}
footer {
    visibility: hidden;
    height: 0%;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown("""
<style>
body {
    overflow-x: hidden;
}
</style>
""", unsafe_allow_html=True)

# Your app content goes here
st.title("")


from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=5000, key="refresh")

# ---------- SHARED DATA STORAGE ----------
DATA_FILE = "data.json"

default_data = {
    "players": [],
    "teams": [],
    "games": [],
    "game_templates": [],
    "welcome_text": "Welcome to Game Night!"
}

data = default_data

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # keep previous session data instead of wiping everything
        data = st.session_state if st.session_state else default_data

for key in data:
    st.session_state[key] = data[key]

def save_data():

    data = {
        "players": st.session_state.players,
        "teams": st.session_state.teams,
        "games": st.session_state.games,
        "game_templates": st.session_state.game_templates,
        "welcome_text": st.session_state.welcome_text
    }

    temp_file = "data_temp.json"

    with open(temp_file, "w") as f:
        json.dump(data, f)

    os.replace(temp_file, DATA_FILE)
def zoomable_image(img_base64, size=80, uid="img"):

    st.markdown(f"""
    <style>
    .zoom-img-{uid} {{
        width:{size}px;
        border-radius:10px;
        cursor:pointer;
    }}

    .overlay-{uid} {{
        position:fixed;
        top:0;
        left:0;
        width:100%;
        height:100%;
        background:rgba(0,0,0,0.95);
        display:none;
        justify-content:center;
        align-items:center;
        z-index:9999;
    }}

    .overlay-{uid} img {{
        max-width:95%;
        max-height:95%;
        border-radius:10px;
    }}

    .overlay-{uid}:target {{
        display:flex;
    }}
    </style>

    <a href="#{uid}">
        <img src="data:image/png;base64,{img_base64}" class="zoom-img-{uid}">
    </a>

    <div id="{uid}" class="overlay-{uid}">
        <a href="#">
            <img src="data:image/png;base64,{img_base64}">
        </a>
    </div>
    """, unsafe_allow_html=True)
# ---------- ADMIN ACCESS ----------
admin = False
secret_access = st.text_input("", placeholder="")

if secret_access == "admin":
    admin_password = st.text_input("Enter Admin Password", type="password")
    if admin_password == "1234":
        admin = True

# ---------- PAGE LAYOUT ----------
main_col, side_col = st.columns([3,1])

# ---------- MAIN COLUMN ----------
with main_col:

    st.title("Game Night")

    if admin:
        st.session_state.welcome_text = st.text_area(
            "Edit Welcome Message",
            st.session_state.welcome_text
        )
        save_data()

    st.markdown(f"## {st.session_state.welcome_text}")
    st.markdown("---")

    # ---------- ADD PLAYER ----------
    if admin:

        st.header("Add Player")

        player_name = st.text_input("Player Name")
        player_photo = st.file_uploader(
            "Upload Player Photo",
            type=["png","jpg","jpeg"]
        )

        if st.button("Add Player"):

            if player_name and player_photo:

                img_base64 = base64.b64encode(player_photo.read()).decode()

                st.session_state.players.append({
                    "name": player_name,
                    "photo": img_base64
                })

                save_data()
                st.success(f"{player_name} added!")

    # ---------- PLAYER LIST ----------
    st.header("Players")

    for idx, player in enumerate(st.session_state.players):

        img_html = f"""
        <img src="data:image/png;base64,{player['photo']}"
        style="
            width:70px;
            height:70px;
            border-radius:10px;
            object-fit:cover;
            margin-right:10px;
        ">
        """

        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:10px;
                max-width:100%;
                overflow-x:hidden;
            ">
                {img_html}
                <div style="
                    text-align:left;
                    font-size:18px;
                    word-wrap:break-word;
                ">
                    {player['name']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------- CREATE TEAM ----------
    player_names = [p["name"] for p in st.session_state.players]

    if admin:

        st.header("Create Team")

        team_name = st.text_input("Team Name")
        team_photo = st.file_uploader(
            "Upload Team Photo",
            type=["png","jpg","jpeg"]
        )

        team_members = st.multiselect(
            "Select Players",
            player_names
        )

        if st.button("Create Team"):

            if team_name and team_photo and team_members:

                img_base64 = base64.b64encode(team_photo.read()).decode()

                st.session_state.teams.append({
                    "name": team_name,
                    "members": team_members,
                    "photo": img_base64
                })

                save_data()
                st.success(f"{team_name} created!")

    # ---------- TEAM DISPLAY ----------
    st.header("Teams")

    for team in st.session_state.teams:

        zoomable_image(team["photo"], size=150, uid=f"team_{team['name']}")
        st.subheader(team["name"])

        cols = st.columns(3)

        for i, member in enumerate(team["members"]):
            cols[i % 3].write(member)

        st.markdown("---")

# ---------- CREATE GAME TEMPLATE ----------
if admin:

    st.header("Create Game Template")

    template_bg = st.file_uploader(
        "Template Background (JPG)",
        type=["jpg"],
        key="template_bg"
    )

    template_name = st.text_input("Template Game Name")
    template_color = st.color_picker("Template Game Title Color", "#FFFFFF")

    template_rounds = st.number_input("Template Rounds", min_value=1, step=1)
    template_points = st.number_input("Template Points", min_value=1, step=1)

    if st.button("Save Template"):

        bg_base64 = None

        if template_bg:
            bg_base64 = base64.b64encode(template_bg.read()).decode()

        st.session_state.game_templates.append({
            "name": template_name,
            "rounds": template_rounds,
            "points": template_points,
            "background": bg_base64,
            "color": template_color
        })

        save_data()
        st.success("Template saved!")

# ---------- ADD GAME FROM TEMPLATE ----------
if admin and st.session_state.game_templates:

    st.header("Add Game From Template")

    template_names = [t["name"] for t in st.session_state.game_templates]

    selected_template = st.selectbox(
        "Choose Template",
        template_names
    )

    if st.button("Add Game To Event"):

        template = next(
            t for t in st.session_state.game_templates
            if t["name"] == selected_template
        )

        st.session_state.games.append({
            "name": template["name"],
            "color": template["color"],
            "background": template["background"],
            "rounds": template["rounds"],
            "points": template["points"],
            "round_winners": ["" for _ in range(template["rounds"])]
        })

        save_data()
        st.success(f"{template['name']} added to event!")

# ---------- DISPLAY GAMES ----------
for idx, game in enumerate(st.session_state.games):

    rounds_html = ""

    for r in range(game["rounds"]):

        if admin:
            winner = st.selectbox(
                f"Winner Round {r+1} ({game['name']})",
                [""] + [team["name"] for team in st.session_state.teams],
                key=f"round_{idx}_{r}"
            )
            game["round_winners"][r] = winner
            save_data()

        winner = game["round_winners"][r]
        rounds_html += f"<p><b>Round {r+1} Winner:</b> {winner}</p>"

    game_winner = "TBD"

    if "" not in game["round_winners"]:

        team_scores = {}

        for winner in game["round_winners"]:
            team_scores[winner] = team_scores.get(winner, 0) + 1

        max_score = max(team_scores.values())

        winners = [t for t, s in team_scores.items() if s == max_score]

        if len(winners) == 1:
            game_winner = winners[0]
        else:
            game_winner = "Tie"

    if game.get("background"):
        style = f"background:linear-gradient(rgba(0,0,0,0.7),rgba(0,0,0,0.7)),url(data:image/jpg;base64,{game['background']});background-size:cover;background-position:center;"
    else:
        style = "background:#111;"

    st.markdown(
        f"""
<div style="{style} padding:40px;border-radius:15px;color:white;max-width:900px;margin:auto;margin-bottom:25px;box-shadow:0px 8px 25px rgba(0,0,0,0.4);">

<h1 style="color:{game['color']}; text-align:center;">
{game['name']}
</h1>

<p style="text-align:center;font-size:18px;">
Points: {game['points']}
</p>

{rounds_html}

<p style="font-size:26px; margin-top:20px;">
<b>Game Winner:</b> {game_winner}
</p>

</div>
""",
        unsafe_allow_html=True
    )

# ---------- LEADERBOARD ----------
with st.expander("Leaderboard"):

    scores = {team["name"]: 0 for team in st.session_state.teams}

    for game in st.session_state.games:

        if game["rounds"] == 0:
            continue

        round_points = game["points"] / game["rounds"]

        for winner in game["round_winners"]:
            if winner:
                scores[winner] += round_points

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    for team, score in sorted_scores:
        st.write(f"{team} — {round(score,2)} points")