from flask import Flask, render_template, request, redirect, url_for,session, jsonify,redirect

app = Flask(__name__)
app.secret_key = "phase10-secret-key"

players = []

class Player:
    def __init__(self, name):
        self.name = name
        self.phase = 1
        self.score = 0
        self.skipped = False
        self.initials = self.make_initials()

    def make_initials(self):
        name = self.name.strip()
        if len(name) >= 2:
            return name[0].upper() + name[1].lower()
        elif len(name) == 1:
            return name[0].upper()
        else:
            return "?"

    def __str__(self):
        return f"{self.name} - Phase {self.phase}, Score {self.score}, Skipped: {self.skipped}"

@app.route('/')
def index():
    color_list = [
        "#FF6B6B", "#6BCB77", "#4D96FF", "#FFD93D", "#FF9CEE",
        "#6B5B95", "#88D498", "#FF8C42", "#2EC4B6", "#E94F37"
    ]
    return render_template('index.html', players=players, colors=color_list)

@app.route('/add_player', methods=['POST'])
def add_player():
    name = request.form['name']
    if name:
        players.append(Player(name))
    return redirect(url_for('index'))

from flask import redirect, url_for, render_template
def get_winner():
    return session.get('winner') 

@app.route('/winner')
def winner():
    if not players:
        return redirect(url_for('index'))

    winning_player = next((p for p in players if p.phase == 10), None)
    if not winning_player:
        return redirect(url_for('index'))

    return render_template("winner.html", winner=winning_player)





@app.route('/next_round', methods=['POST'])
def next_round():
    print("✅ /next_round POST received:", request.form)

    try:
        i = int(request.form.get('index', 0))
    except (ValueError, TypeError):
        return jsonify(success=False, error="Invalid player index"), 400

    if 0 <= i < len(players):
        player = players[i]

        # Parse score safely
        score_raw = request.form.get('score', '0')
        try:
            score = int(score_raw.strip()) if score_raw.strip() else 0
        except ValueError:
            score = 0

        # Always apply score
        player.score += score

        # Parse checkbox inputs
        completed = request.form.get('completed') == 'on'
        skipped = request.form.get('skipped') == 'on'

        # Update phase only if completed and NOT skipped
        if completed and not skipped:
            player.phase += 1

        # Mark if skipped (optional)
        player.skipped = skipped

        # Handle winner logic
        if completed and player.phase == 10:
            session['winner'] = {
                'name': player.name,
                'score': player.score
            }
            return jsonify(success=True, winner=True, redirect=url_for('winner'))

        return jsonify(success=True, score=player.score, phase=player.phase)

    return jsonify(success=False, error="Player not found"), 404









@app.route('/reset', methods=['POST'])
def reset():
    global players
    players = []
    print("Game has been reset.")
    # Optionally reset global winner if you're storing it
    global winner
    try:
        winner = None
    except NameError:
        pass  # ignore if you don't use a global winner

    return redirect(url_for('index'))


@app.route('/remove_player', methods=['POST'])
def remove_player():
    index = int(request.form.get('index'))
    if 0 <= index < len(players):
        del players[index]
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
