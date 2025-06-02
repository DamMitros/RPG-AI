from flask import *
from game.player import Player
from ai.interface import get_npc_response, reset_conversation
import uuid, json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
player = Player(name="Demo")

try:
  with open('merchant_inventory.json', 'r') as f:
    merchant_inventory_data = json.load(f)
except FileNotFoundError:
  merchant_inventory_data = []

def get_merchant_item(item_id):
  for item in merchant_inventory_data:
    if item['id'] == item_id:
      return item
  return None

@app.route("/")
def mainPage():
  if 'tavern_session_id' in session:
    reset_conversation(session['tavern_session_id'])
    session.pop('tavern_session_id', None)
    session.pop('tavern_history', None)
  if 'shop_session_id' in session:
    reset_conversation(session['shop_session_id'])
    session.pop('shop_session_id', None)
    session.pop('shop_history', None)
    session.pop('shop_message', None)
  return render_template("mainPage.html", player=player)

@app.route("/tavern", methods=['GET', 'POST'])
def pub():
  session_key = 'tavern_session_id'
  history_key = 'tavern_history'
  if session_key not in session:
    session[session_key] = str(uuid.uuid4())
    session[history_key] = []
    reset_conversation(session[session_key])

  history = session.get(history_key, [])
  character = "mysterious_stranger" if player.level > 5 else "tavern_keeper"

  if request.method == 'POST':
    message = request.form.get('message')
    if message:
      response = get_npc_response(message, character, session[session_key])
      history.append({'user': message, 'npc': response})
      session[history_key] = history

  return render_template("tavern.html", player=player, history=history)

@app.route("/tradesman", methods=['GET', 'POST'])
def shop():
  session_key = 'shop_session_id'
  history_key = 'shop_history'
  character = "merchant"
  shop_message = session.pop('shop_message', None)

  if session_key not in session:
    session[session_key] = str(uuid.uuid4())
    session[history_key] = []
    reset_conversation(session[session_key])

  history = session.get(history_key, [])

  if request.method == 'POST':
    action = request.form.get('action')

    if action == 'talk':
      message = request.form.get('message')
      if message:
        response = get_npc_response(message, character, session[session_key])
        history.append({'user': message, 'npc': response})
        session[history_key] = history
    elif action == 'buy':
      item_id = request.form.get('item_id')
      item_to_buy = get_merchant_item(item_id)
      if item_to_buy and item_to_buy['quantity'] > 0:
        if player.gold >= item_to_buy['price']:
          player.gold -= item_to_buy['price']
          player.add_item({
            "id": item_to_buy['id'],
            "name": item_to_buy['name'],
            "description": item_to_buy['description'],
            "sell_value": item_to_buy.get('sell_value', item_to_buy['price'] // 3)
          })
          item_to_buy['quantity'] -= 1
          shop_message = f"You bought {item_to_buy['name']}."
        else:
          shop_message = "You don't have enough gold."
      elif item_to_buy:
        shop_message = "Sorry, that item is out of stock."
      else:
        shop_message = "Invalid item."
    elif action == 'sell':
      item_id_to_sell = request.form.get('item_id')
      item_in_player_inv = next((item for item in player.inventory if item['id'] == item_id_to_sell), None)

      if item_in_player_inv:
        sell_price = item_in_player_inv.get('sell_value', 1)
        if player.remove_item(item_id_to_sell):
          player.gold += sell_price
          merchant_item = get_merchant_item(item_id_to_sell)
          if merchant_item:
            merchant_item['quantity'] += 1
          shop_message = f"You sold {item_in_player_inv['name']} for {sell_price} gold."
        else:
          shop_message = "Error selling item."
      else:
        shop_message = "You don't have that item to sell."

    if shop_message:
      session['shop_message'] = shop_message
    return redirect(url_for('shop'))

  merchant_wares = [item for item in merchant_inventory_data if item['quantity'] > 0]
  return render_template("shop.html",
                         player=player,
                         history=history,
                         merchant_wares=merchant_wares,
                         player_inventory=player.inventory,
                         shop_message=shop_message)

@app.route("/smithy")
def smithy():
  return render_template("smithy.html", player=player)

@app.route("/pickboard")
def pickboard():
  return render_template("pickboard.html", player=player)

if __name__ == "__main__":
  app.run(debug=True)