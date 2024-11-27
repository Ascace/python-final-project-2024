from flask import Flask, render_template, request, redirect, url_for, jsonify
import random

app = Flask(__name__)

# Define territories and initial ownership
territories = {
    "North America": {
        "owner": None,
        "troops": 0,
        "coords": "183,9,195,17,197,32,195,46,181,53,168,65,168,74,155,59,155,46,142,40,143,23,159,21,176,7,115,28,123,42,116,59,110,70,115,82,122,90,139,62,131,68,151,75,157,92,149,107,136,127,127,138,123,154,106,150,91,156,99,167,100,182,91,190,80,176,66,159,62,136,57,111,57,93,49,75,30,70,16,74,19,51,26,38,47,40,59,40,82,40,101,47,110,40,91,44,72,41,38,36"
    },
    "South America": {
        "owner": None,
        "troops": 0,
        "coords": "99,184,107,181,121,181,114,183,130,181,135,184,144,193,164,201,184,213,115,239,112,261,114,290,119,316,131,327,128,306,138,285,151,267,168,249,175,229,182,223,168,208,155,199,178,208,97,192,97,200,95,220,102,233"
    },
    "Europe": {
        "owner": None,
        "troops": 0,
        "coords": "306,152,298,146,287,136,277,141,270,148,263,161,257,167,248,156,247,165,239,170,239,160,229,149,222,157,223,168,219,174,212,178,201,174,197,165,195,152,203,150,207,140,218,126,231,114,243,101,209,119,195,121,179,121,182,113,187,105,194,102,205,85,198,85,209,93,213,105,221,114,219,60,203,61,199,69,207,78,222,76,224,69,211,61,287,48,311,45,299,47,333,45,326,65,328,83,327,100,315,103,307,116,307,128,308,138,231,81,235,69,241,59,249,50,260,49,271,43,235,86,236,103,243,85,223,120"
    },
    "Africa": {
        "owner": None,
        "troops": 0,
        "coords": "249,178,251,184,259,184,264,195,269,187,277,184,284,194,287,201,291,209,295,217,300,222,303,229,305,234,313,233,319,233,319,242,312,250,305,257,298,265,297,274,299,280,300,286,295,289,289,299,287,307,285,312,279,320,271,325,262,325,255,309,257,317,248,297,253,300,248,287,250,279,250,268,247,261,244,249,239,237,231,239,221,241,211,244,204,237,203,228,199,220,197,209,199,195,205,185,213,179,205,191,234,177,227,177,241,177,218,177,323,284,323,273,325,290,319,304,320,298,314,284,306,288,302,297,305,307,305,313,311,312"
    },
    "Asia": {
        "owner": None,
        "troops": 0,
        "coords": "344,182,353,189,362,221,371,203,355,198,380,189,395,200,406,216,418,208,411,183,428,171,430,153,426,144,422,133,433,129,443,146,459,133,465,128,465,116,460,105,465,96,460,86,457,71,467,54,480,45,463,33,443,30,424,26,402,26,385,26,365,18,349,25,343,33,330,37,330,58,328,80,330,94,322,103,308,109,317,126,323,141,314,153,274,153,290,153,273,169,289,174,289,189,296,205,311,222,325,215,335,197,318,184,334,186,323,188"
    },
    "Australia": {
        "owner": None,
        "troops": 0,
        "coords": "411,237,389,237,388,247,395,261,413,268,426,250,433,226,454,222,463,234,471,245,458,245,442,243,443,224,447,257,462,273,451,266,467,255,474,272,481,281,487,296,486,309,475,321,479,328,465,329,454,314,436,310,423,319,412,309,406,292,416,283,426,279,430,268,437,265"
    }
}

players = []
turn = 0
messages = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/setup", methods=["GET", "POST"])
def setup():
    global players, territories
    if request.method == "POST":
        num_players = int(request.form.get("num_players"))
        players = [{"name": f"Player {i + 1}", "troops": 20} for i in range(num_players)]

        # Assign territories randomly to players
        shuffled_players = players * (len(territories) // len(players)) + players[:len(territories) % len(players)]
        random.shuffle(shuffled_players)
        for idx, territory in enumerate(territories.keys()):
            territories[territory]["owner"] = shuffled_players[idx]["name"]
            territories[territory]["troops"] = 3

        return redirect(url_for("game"))

    return render_template("setup.html")

@app.route("/game")
def game():
    global players, turn, messages
    current_player = players[turn]
    return render_template("game.html", players=players, territories=territories, current_player=current_player, messages=messages)

@app.route("/attack", methods=["POST"])
def attack():
    global territories, messages
    data = request.json
    attacker = data["attacker"]
    defender = data["defender"]
    attacking_territory = territories[attacker]
    defending_territory = territories[defender]

    if attacking_territory["owner"] != players[turn]["name"]:
        return jsonify({"error": "You can only attack from your own territory."}), 400

    if attacking_territory["troops"] <= 1:
        return jsonify({"error": "Not enough troops to attack."}), 400

    if attacking_territory["owner"] == defending_territory["owner"]:
        return jsonify({"error": "Cannot attack your own territory."}), 400

    # Duel: Highest random number out of 100
    attacker_roll = random.randint(1, 100)
    defender_roll = random.randint(1, 100)

    if attacker_roll > defender_roll:
        defending_territory["troops"] -= 1
        messages.append(f"{attacker} won the duel! Defender lost 1 troop.")
        if defending_territory["troops"] <= 0:
            messages.append(f"{defender} was conquered! Ownership transferred to {attacking_territory['owner']}.")
            defending_territory["owner"] = attacking_territory["owner"]
            defending_territory["troops"] = 1
            attacking_territory["troops"] -= 1
    else:
        attacking_territory["troops"] -= 1
        messages.append(f"{defender} won the duel! Attacker lost 1 troop.")

    return jsonify({"territories": territories, "messages": messages})

@app.route("/reinforce", methods=["POST"])
def reinforce():
    global players, territories, messages
    data = request.json
    player = data["player"]
    territory = data["territory"]
    troops = int(data["troops"])

    current_player = [p for p in players if p["name"] == player][0]
    if current_player["troops"] < troops:
        return jsonify({"error": "Not enough troops"}), 400

    territories[territory]["troops"] += troops
    current_player["troops"] -= troops
    messages.append(f"{troops} troops added to {territory}.")

    return jsonify({"territories": territories, "messages": messages})

@app.route("/next_turn")
def next_turn():
    global turn, players, messages
    turn = (turn + 1) % len(players)
    current_player = players[turn]
    reinforcements = len([t for t in territories.values() if t["owner"] == current_player["name"]]) // 3
    current_player["troops"] += reinforcements
    messages.append(f"{current_player['name']} received {reinforcements} reinforcements.")
    return redirect(url_for("game"))

@app.route('/')
def world_map():
    return render_template('map.html')  # Ensure your map HTML is saved as "templates/map.html"

@app.route('/region-click', methods=['POST'])
def region_click():
    data = request.json
    region = data.get("region")
    if region in territories:
        return jsonify({"message": f"You clicked on {region}!", "owner": territories[region]["owner"], "troops": territories[region]["troops"]})
    return jsonify({"error": "Invalid region"}), 400


if __name__ == "__main__":
    app.run(debug=True)
