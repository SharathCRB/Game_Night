import streamlit as st
import base64
st.markdown("""
<style>

/* hide menu */
#MainMenu {visibility: hidden;}

/* hide header */
header {visibility: hidden;}

/* hide footer */
footer {visibility: hidden;}

/* cover Streamlit branding */
body::after {
    content: "";
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 80px;
    background: black;  /* match your page background */
    z-index: 9999;
}

</style>
""", unsafe_allow_html=True)
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=5000, key="refresh")

# ---------- HIDDEN ADMIN ACCESS ----------
admin = False

secret_access = st.text_input("", placeholder="")

if secret_access == "admin":
    admin_password = st.text_input("Enter Admin Password", type="password")
    if admin_password == "1234":
        admin = True


# ---------- PAGE LAYOUT ----------
main_col, side_col = st.columns([3,1])


# ---------- SESSION STORAGE ----------
if "players" not in st.session_state:
    st.session_state.players = []

if "teams" not in st.session_state:
    st.session_state.teams = []

if "games" not in st.session_state:
    st.session_state.games = []

if "game_templates" not in st.session_state:
    st.session_state.game_templates = []

if "welcome_text" not in st.session_state:
    st.session_state.welcome_text = "Welcome to Game Night!"


# ---------- MAIN COLUMN ----------
with main_col:

    st.title("Game Night")

    if admin:
        st.session_state.welcome_text = st.text_area(
            "Edit Welcome Message",
            st.session_state.welcome_text
        )

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

                st.session_state.players.append({
                    "name": player_name,
                    "photo": player_photo
                })

                st.success(f"{player_name} added!")


    # ---------- PLAYER LIST ----------
    st.header("Players")

    for player in st.session_state.players:

        col1, col2 = st.columns([1,3])

        with col1:
            st.image(player["photo"], width=80)

        with col2:
            st.write(player["name"])

    st.markdown("---")


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

                st.session_state.teams.append({
                    "name": team_name,
                    "members": team_members,
                    "photo": team_photo
                })

                st.success(f"{team_name} created!")


    # ---------- TEAM DISPLAY ----------
    st.header("Teams")

    for team in st.session_state.teams:

        st.image(team["photo"], width=200)
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

            st.success(f"{template['name']} added to event!")

# ---------- DISPLAY GAMES ----------
for idx, game in enumerate(st.session_state.games):

    rounds_html = ""

    # ---------- ROUNDS ----------
    for r in range(game["rounds"]):

        if admin:
            winner = st.selectbox(
                f"Winner Round {r+1} ({game['name']})",
                [""] + [team["name"] for team in st.session_state.teams],
                key=f"round_{idx}_{r}"
            )
            game["round_winners"][r] = winner

        winner = game["round_winners"][r]

        rounds_html += f"<p><b>Round {r+1} Winner:</b> {winner}</p>"


    # ---------- CALCULATE GAME WINNER ----------
    game_winner = "TBD"

    # only calculate winner if ALL rounds have winners
    if "" not in game["round_winners"]:

        team_scores = {}

        for winner in game["round_winners"]:
            team_scores[winner] = team_scores.get(winner, 0) + 1

        max_score = max(team_scores.values())

        winners = [
            t for t, s in team_scores.items()
            if s == max_score
        ]

        if len(winners) == 1:
            game_winner = winners[0]
        else:
            game_winner = "Tie"


    # ---------- BACKGROUND STYLE ----------
    if game.get("background"):
        style = f"background:linear-gradient(rgba(0,0,0,0.7),rgba(0,0,0,0.7)),url(data:image/jpg;base64,{game['background']});background-size:cover;background-position:center;"
    else:
        style = "background:#111;"


    # ---------- GAME CARD ----------
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

    scores = {
        team["name"]: 0
        for team in st.session_state.teams
    }

    for game in st.session_state.games:

        if game["rounds"] == 0:
            continue

        # points per round
        round_points = game["points"] / game["rounds"]

        for winner in game["round_winners"]:

            if winner:
                scores[winner] += round_points


    # sort leaderboard
    sorted_scores = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for team, score in sorted_scores:
        st.write(f"{team} — {round(score,2)} points")