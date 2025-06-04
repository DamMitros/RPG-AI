from flask import *
from game.player import Player
from game.quest_system import QuestSystem
from game.crafting_system import CraftingSystem
from ai.dialog_engine import DialogEngine
import uuid, json, random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
player = Player(name="Demo")

dialog_engine = DialogEngine()
quest_system = QuestSystem(dialog_engine)
crafting_system = CraftingSystem()  

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

  session.pop('inventory_message', None)
  session.pop('forest_message', None)

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
  action = request.form.get('action')
  quest_action = request.form.get('quest_action')
  quest_updates = []
  
  if quest_action:
    updates, expired = quest_system.perform_action(quest_action, "mainPage", player)
    quest_updates.extend(updates)
    return jsonify({'quest_updates': updates, 'expired': expired})
  elif action in ['clear_bandits', 'gather_herbs']:
    updates, expired = quest_system.perform_action(action, "mainPage", player)
    quest_updates.extend(updates)
    
    if action == 'clear_bandits':
      player.add_experience(20)
      player.add_gold(10)
      session['action_message'] = "You successfully cleared some bandits from the area!"
    elif action == 'gather_herbs':
      player.add_experience(10)
      player.add_gold(5)
      player.add_item({
        "id": "mountain_herb",
        "name": "Mountain Herb",
        "description": "A rare herb found in mountainous regions",
        "sell_value": 8
      })
      session['action_message'] = "You gathered some valuable mountain herbs!"
    
    return jsonify({'quest_updates': updates, 'expired': expired, 'message': session.get('action_message', '')})
  
  return jsonify({'error': 'No valid action specified'})

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
          if available_action['action'] in ['talk_to_bartek', 'gather_information', 'deliver_item']:
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
          
          updates, expired = quest_system.perform_action("buy_materials", "tradesman", player)
          quest_updates.extend(updates)
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

@app.route("/smithy", methods=['GET', 'POST'])
def smithy():
  quest_updates = []
  available_actions = quest_system.get_available_actions_for_location("smithy", player)
  craft_message = session.pop('craft_message', None)
  
  if request.method == 'POST':
    action = request.form.get('action')
    
    if action == 'quest_action':
      quest_action = request.form.get('quest_action')
      if quest_action:
        updates, expired = quest_system.perform_action(quest_action, "smithy", player)
        quest_updates.extend(updates)
    elif action == 'craft':
      recipe_id = request.form.get('recipe_id')
      success, message = crafting_system.craft_item(recipe_id, player)
      
      if success:
        updates, expired = quest_system.perform_action("craft_equipment", "smithy", player)
        quest_updates.extend(updates)
      
      craft_message = message
      session['craft_message'] = craft_message
      return redirect(url_for('smithy'))

  available_recipes = crafting_system.get_available_recipes(player.level)
  craftable_recipes = {}
  for recipe_id, recipe in available_recipes.items():
    can_craft, message = crafting_system.can_craft(recipe_id, player)
    craftable_recipes[recipe_id] = {
      'recipe': recipe,
      'can_craft': can_craft,
      'message': message
    }
  
  return render_template("smithy.html", 
                        player=player, 
                        craftable_recipes=craftable_recipes,
                        craft_message=craft_message,
                        quest_updates=quest_updates,
                        available_actions=available_actions)

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
        
        if quest_action == 'mine_ore':
          player.add_item({
            "id": "silver_ore",
            "name": "Silver Ore",
            "description": "Valuable silver ore mined from the depths",
            "sell_value": 25
          })
          player.add_experience(30)
    else:
      message = request.form.get('message')
      if message:
        for available_action in available_actions:
          if available_action['action'] in ['investigate_mine', 'investigate_mine_sounds', 'search_area', 'rescue_person', 'mine_ore']:
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

@app.route('/inventory')
def inventory():
    inventory_items = getattr(player, 'inventory', [])
    item_counts = {}
    for item in inventory_items:
        item_key = item['id'] if 'id' in item else item['name']
        if item_key in item_counts:
            item_counts[item_key]['quantity'] += 1
        else:
            item_counts[item_key] = {
                'name': item['name'],
                'description': item.get('description', ''),
                'quantity': 1,
                'sell_value': item.get('sell_value', 0),
                'type': item.get('type', 'misc')
            }
    
    return render_template('inventory.html', 
                         player=player, 
                         items=item_counts,
                         message=session.get('inventory_message'))

@app.route('/inventory', methods=['POST'])
def inventory_action():
    action = request.form.get('action')
    item_id = request.form.get('item_id')
    message = ""
    
    if action == 'use_item' and item_id:
        item = next((item for item in player.inventory if item.get('id') == item_id or item['name'] == item_id), None)
        if item:
            if item.get('type') == 'consumable':
                player.remove_item(item_id)
                if 'health_restore' in item:
                    player.health = min(player.max_health, player.health + item['health_restore'])
                    message = f"Used {item['name']}. Health restored!"
                elif 'mana_restore' in item:
                    player.mana = min(player.max_mana, player.mana + item['mana_restore'])
                    message = f"Used {item['name']}. Mana restored!"
            else:
                message = f"Cannot use {item['name']}."
        else:
            message = "Item not found."
    
    session['inventory_message'] = message
    return redirect(url_for('inventory'))

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

@app.route('/forest')
def forest():
    quest_updates = []
    available_actions = quest_system.get_available_actions_for_location("forest", player)
    
    return render_template('forest.html', 
                         player=player, 
                         available_actions=available_actions,
                         quest_updates=quest_updates,
                         message=session.get('forest_message'))

@app.route('/forest', methods=['POST'])
def forest_action():
    action = request.form.get('action')
    quest_updates = []
    message = ""
    
    if action == 'quest_action':
        quest_action = request.form.get('quest_action')
        if quest_action:
            updates, expired = quest_system.perform_action(quest_action, "forest", player)
            quest_updates.extend(updates)
    elif action == 'hunt':
        success_chance = 0.7 + (player.level * 0.1)  
        
        if random.random() < success_chance:
            exp_gain = random.randint(15, 25)
            gold_gain = random.randint(10, 20)
            
            player.experience += exp_gain
            player.gold += gold_gain
            player.check_level_up()
            player.add_item({
                'id': 'wolf_pelt',
                'name': 'Wolf Pelt',
                'description': 'A fine pelt from a forest wolf. Can be sold or used for crafting.',
                'type': 'materials',
                'sell_value': 15
            })
            
            message = f"Successful hunt! You gained {exp_gain} experience, {gold_gain} gold, and a wolf pelt."
            updates, expired = quest_system.perform_action("hunt_wolf", "forest", player)
            quest_updates.extend(updates)
        else:
            message = "The hunt was unsuccessful. The wolves evaded you this time."
    elif action == 'explore':
        find_chance = 0.6
        
        if random.random() < find_chance:
            items = [
                {'id': 'healing_herb', 'name': 'Healing Herb', 'description': 'A natural remedy that restores 20 health.', 'type': 'consumable', 'health_restore': 20},
                {'id': 'silver_coin', 'name': 'Silver Coin', 'description': 'An old silver coin found in the forest.', 'type': 'misc', 'sell_value': 5},
                {'id': 'mushroom', 'name': 'Forest Mushroom', 'description': 'An edible mushroom. Restores 10 health.', 'type': 'consumable', 'health_restore': 10}
            ]
            found_item = random.choice(items)
            player.add_item(found_item)
            message = f"You found a {found_item['name']} while exploring!"
            updates, expired = quest_system.perform_action("explore_forest", "forest", player)
            quest_updates.extend(updates)
        else:
            message = "You explored the forest but found nothing of interest."
    
    session['forest_message'] = message
    return redirect(url_for('forest'))

if __name__ == "__main__":
  app.run(debug=True)