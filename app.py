from flask import *
from game.player import Player
from ai.dialog_engine import get_npc_response

app = Flask(__name__)
app.secret_key = 'your_secret_key' 
player = Player(name="Demo")

@app.route("/")
def mainPage():
  return render_template("mainPage.html", player=player)

@app.route("/tavern", methods=['GET', 'POST'])
def pub():
  response = None

  if 'session_id' not in session:
    session['session_id'] = str(id(player))

  character = "mysterious_stranger" if player.level > 5 else "tavern_keeper"
    
  if request.method == 'POST':
    message = request.form.get('message')
    response = get_npc_response(message, character, session['session_id'])
        
  return render_template("tavern.html", player=player, response=response)

@app.route("/tradesman")
def shop():
  return render_template("shop.html", player=player)

@app.route("/smithy")
def smithy():
  return render_template("smithy.html", player=player)

@app.route("/pickboard")
def pickboard():
  return render_template("pickboard.html", player=player)

if __name__ == "__main__":
  app.run(debug=True)