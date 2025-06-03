from flask import *
from game.player import Player
from game.quest_system import QuestSystem
from ai.dialog_engine import DialogEngine
import uuid, json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
player = Player(name="Demo")

dialog_engine = DialogEngine()
quest_system = QuestSystem(dialog_engine)  

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

@app.route("/", methods=['GET', 'POST'])
def mainPage():
  if 'tavern_session_id' in session:
    dialog_engine.reset_conversation(session['tavern_session_id'])
    session.pop('tavern_session_id', None)
    session.pop('tavern_history', None)
  if 'shop_session_id' in session:
    dialog_engine.reset_conversation(session['shop_session_id'])
    session.pop('shop_session_id', None)
    session.pop('shop_history', None)
    session.pop('shop_message', None)
  if 'mine_session_id' in session:
    dialog_engine.reset_conversation(session['mine_session_id'])
    session.pop('mine_session_id', None)
    session.pop('mine_history', None)

  quest_updates = []
  available_actions = quest_system.get_available_actions_for_location("mainPage", player)
  
  if request.method == 'POST':
    quest_action = request.form.get('quest_action')
    if quest_action:
      updates, expired = quest_system.perform_action(quest_action, "mainPage", player)
      quest_updates.extend(updates)
  
  return render_template("mainPage.html", player=player, 
      quest_updates=quest_updates, available_actions=available_actions)

@app.route("/mainpage_action", methods=['POST'])
def mainpage_action():
  quest_action = request.form.get('quest_action')
  if quest_action:
    updates, expired = quest_system.perform_action(quest_action, "mainPage", player)
    return jsonify({'quest_updates': updates, 'expired': expired})
  return jsonify({'error': 'No action specified'})

@app.route("/tavern", methods=['GET', 'POST'])
def pub():
  session_key = 'tavern_session_id'
  history_key = 'tavern_history'
  if session_key not in session:
    session[session_key] = str(uuid.uuid4())
    session[history_key] = []
    dialog_engine.reset_conversation(session[session_key])

  history = session.get(history_key, [])
  character = "tavern_keeper"  
  quest_updates = []
  available_actions = quest_system.get_available_actions_for_location("tavern", player)

  if request.method == 'POST':
    action = request.form.get('action')
    
    if action == 'quest_action':
      quest_action = request.form.get('quest_action')
      if quest_action:
        updates, expired = quest_system.perform_action(quest_action, "tavern", player)
        quest_updates.extend(updates)
    else:
      message = request.form.get('message')
      if message:
        for available_action in available_actions:
          if available_action['action'] in ['talk_to_bartek', 'gather_information']:
            updates, expired = quest_system.perform_action(available_action['action'], "tavern", player)
            quest_updates.extend(updates)

        player_stats = {
          "level": player.level,
          "gold": player.gold,
          "experience": player.experience,
          "location": "tavern"
        }
        response = dialog_engine.get_npc_response(
          user_input=message, 
          character=character, 
          session_id=session[session_key],
          player_stats=player_stats
        )
        history.append({'user': message, 'npc': response})
        session[history_key] = history

  return render_template("tavern.html", player=player, history=history, 
        quest_updates=quest_updates, available_actions=available_actions)

@app.route("/tradesman", methods=['GET', 'POST'])
def shop():
  session_key = 'shop_session_id'
  history_key = 'shop_history'
  character = "merchant"
  shop_message = session.pop('shop_message', None)

  if session_key not in session:
    session[session_key] = str(uuid.uuid4())
    session[history_key] = []
    dialog_engine.reset_conversation(session[session_key])

  history = session.get(history_key, [])
  quest_updates = []
  available_actions = quest_system.get_available_actions_for_location("tradesman", player)

  if request.method == 'POST':
    action = request.form.get('action')

    if action == 'quest_action':
      quest_action = request.form.get('quest_action')
      if quest_action:
        updates, expired = quest_system.perform_action(quest_action, "tradesman", player)
        quest_updates.extend(updates)
    elif action == 'talk':
      message = request.form.get('message')
      if message:
        for available_action in available_actions:
          if available_action['action'] in ['talk_to_erik', 'investigate_items']:
            updates, expired = quest_system.perform_action(available_action['action'], "tradesman", player)
            quest_updates.extend(updates)
        
        player_stats = {
          "level": player.level,
          "gold": player.gold,
          "experience": player.experience,
          "location": "shop"
        }
        response = dialog_engine.get_npc_response(
          user_input=message, 
          character=character, 
          session_id=session[session_key],
          player_stats=player_stats
        )
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
                         shop_message=shop_message,
                         quest_updates=quest_updates,
                         available_actions=available_actions)

@app.route("/smithy") # trzeba to w końcu zaimlpementować
def smithy():
  return render_template("smithy.html", player=player)

@app.route("/pickboard", methods=['GET', 'POST'])
def pickboard():
  message = None
  
  if request.method == 'POST':
    action = request.form.get('action')
    quest_id = request.form.get('quest_id')
    quest_type = request.form.get('quest_type')
    
    if action == 'accept_quest' and quest_id:
      if quest_system.accept_quest(quest_id, player):
        message = f"Quest accepted! Check your active quests for details."
      else:
        message = "Unable to accept quest. You may already have it active."
    elif action == 'complete_quest' and quest_id:
      completed_quest = quest_system.complete_quest(quest_id, player)
      if completed_quest:
        message = f"Quest completed! You earned {completed_quest['reward_gold']} gold and {completed_quest['reward_exp']} experience."
      else:
        message = "Unable to complete quest."
    elif action == 'refresh_quests':
      quest_system.refresh_generated_quests(player.level, force=True)
      message = "New quests have been posted on the notice board!"
    elif action == 'generate_quest':
      new_quest = quest_system.quest_generator.generate_quest(
        quest_type=quest_type if quest_type else None,
        player_level=player.level
      )
      if new_quest:
        quest_system.generated_quests_cache[new_quest["id"]] = new_quest
        message = f"A new {new_quest['type']} quest has been posted: {new_quest['title']}"
      else:
        message = "Failed to generate new quest. Try again later."
  
  available_quests = quest_system.get_available_quests(player)
  active_quests = quest_system.get_player_active_quests(player)
  
  return render_template("pickboard.html", 
                        player=player, 
                        available_quests=available_quests,
                        active_quests=active_quests,
                        message=message)

@app.route("/mine_entrance", methods=['GET', 'POST'])
def mine_entrance():
  session_key = 'mine_session_id'
  history_key = 'mine_history'
  character = "mysterious_stranger"
  
  if session_key not in session:
    session[session_key] = str(uuid.uuid4())
    session[history_key] = []
    dialog_engine.reset_conversation(session[session_key])

  history = session.get(history_key, [])
  quest_updates = []
  available_actions = quest_system.get_available_actions_for_location("mine_entrance", player)

  if request.method == 'POST':
    action = request.form.get('action')
    
    if action == 'quest_action':
      quest_action = request.form.get('quest_action')
      if quest_action:
        updates, expired = quest_system.perform_action(quest_action, "mine_entrance", player)
        quest_updates.extend(updates)
    else:
      message = request.form.get('message')
      if message:
        for available_action in available_actions:
          if available_action['action'] in ['investigate_mine', 'investigate_mine_sounds', 'search_area', 'rescue_person']:
            updates, expired = quest_system.perform_action(available_action['action'], "mine_entrance", player)
            quest_updates.extend(updates)
        
        player_stats = {
          "level": player.level,
          "gold": player.gold,
          "experience": player.experience,
          "location": "mine_entrance"
        }
        response = dialog_engine.get_npc_response(
          user_input=message, 
          character=character, 
          session_id=session[session_key],
          player_stats=player_stats
        )
        history.append({'user': message, 'npc': response})
        session[history_key] = history

  return render_template("mine_entrance.html", player=player, history=history,
          quest_updates=quest_updates, available_actions=available_actions)

@app.route("/conversation_stats")
def conversation_stats():
  stats = dialog_engine.get_conversation_stats()
  return jsonify(stats)

@app.route("/quality_report")
def quality_report():
  report = dialog_engine.get_quality_report()
  return jsonify(report)

@app.route("/session_stats/<session_id>")
def session_stats(session_id):
  stats = dialog_engine.get_conversation_stats(session_id)
  return jsonify(stats)

if __name__ == "__main__":
  app.run(debug=True)