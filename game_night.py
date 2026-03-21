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

# Your app content goes here
st.title("")


from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="refresh")

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
    except JSONDecodeError:
        data = default_data

for key in data:
    st.session_state[key] = data[key]
    if "play_transition" not in st.session_state:
        st.session_state.play_transition = False
    if "last_game_bg" not in st.session_state:
        st.session_state.last_game_bg = None

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
    with st.expander("Players"):

        sorted_players = sorted(
            st.session_state.players,
            key=lambda p: p["name"].lower()
        )

    for idx, player in enumerate(sorted_players):

        for idx, player in enumerate(st.session_state.players):

            col1, col2, col3 = st.columns([1,3,1])

            with col1:
                zoomable_image(player["photo"], size=70, uid=f"player_{idx}")

            with col2:
                st.write(player["name"])

            if admin:
                with col3:
                    if st.button("❌", key=f"del_player_{idx}"):
                        st.session_state.players.pop(idx)
                        save_data()
                        if st.button("❌", key=f"del_player_{idx}"):
                            st.session_state.players.pop(idx)
                            save_data()

    # ---------- CREATE TEAM ----------
    player_names = sorted(
        [p["name"] for p in st.session_state.players],
        key=lambda x: x.lower()
    )

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

    for idx, team in enumerate(st.session_state.teams):

        colA, colB = st.columns([5,1])

        with colA:
            zoomable_image(team["photo"], size=150, uid=f"team_{team['name']}")
            st.subheader(team["name"])

        if admin:
            with colB:
                if st.button("❌", key=f"del_team_{idx}"):
                    st.session_state.teams.pop(idx)
                    save_data()
                    if st.button("❌", key=f"del_team_{idx}"):
                        st.session_state.teams.pop(idx)
                        save_data()

        cols = st.columns(3)

        sorted_members = sorted(team["members"], key=lambda x: x.lower())
        for i, member in enumerate(sorted_members):
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
        st.session_state.play_transition = True
        st.session_state.last_game_bg = template["background"]

        save_data()
        st.success(f"{template['name']} added to event!")

# ---------- DISPLAY GAMES ----------
for idx, game in enumerate(st.session_state.games):

    if admin:
        if st.button(f"Delete {game['name']}", key=f"del_game_{idx}"):
            st.session_state.games.pop(idx)
            save_data()

    rounds_html = ""

    for r in range(game["rounds"]):

        if admin:
            winner = st.selectbox(
                f"Winner Round {r+1} ({game['name']})",
                [""] + [team["name"] for team in st.session_state.teams],
                key=f"round_{idx}_{r}"
            )

            # FIX: only save if changed
            if game["round_winners"][r] != winner:
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

<h1 style="color:{game['color']}; text-align:center; width:100%; margin:0 auto;">
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

    for idx, (team_name, score) in enumerate(sorted_scores):

        team_data = next(
            t for t in st.session_state.teams
            if t["name"] == team_name
        )

        col1, col2 = st.columns([1,4])

        with col1:
            zoomable_image(
                team_data["photo"],
                size=60,
                uid=f"leader_{idx}"
            )

        with col2:
            st.write(f"{team_name} — {round(score,2)} points")
# ---------- ANIMATION ----------
if st.session_state.play_transition:

    images = [
        t["background"]
        for t in st.session_state.game_templates
        if t.get("background")
    ]

    imgs_html = ""

    for img in images:
        imgs_html += f'<img src="data:image/jpg;base64,{img}" class="slide-img">'

    final_img = st.session_state.last_game_bg or ""

    st.markdown(
        f"""
<style>

.transition-overlay {{
position:fixed;
top:0;
left:0;
width:100%;
height:100%;
background:black;
z-index:99999;
overflow:hidden;
display:flex;
align-items:center;
justify-content:center;
flex-direction:column;
}}

.slider {{
display:flex;
gap:40px;
animation: slide 5s linear forwards;
}}

.slide-img {{
height:200px;
border-radius:20px;
}}

@keyframes slide {{
0% {{ transform: translateX(100%); }}
100% {{ transform: translateX(-100%); }}
}}

.final-img {{
position:absolute;
height:300px;
animation: zoomout 2s 5s forwards;
}}

@keyframes zoomout {{
0% {{ transform: scale(1); }}
100% {{ transform: scale(0.2); opacity:0; }}
}}

</style>

<div class="transition-overlay">

<div class="slider">
{imgs_html}
</div>

<img src="data:image/jpg;base64,{final_img}" class="final-img">

<audio autoplay>
<source src="https://www.soundjay.com/buttons/sounds/button-09.mp3">
</audio>

</div>

<script>
setTimeout(() => {{
window.location.reload();
}}, 7000);
</script>

""",
        unsafe_allow_html=True
    )

    st.session_state.play_transition = False