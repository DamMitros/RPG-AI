from flask import Blueprint, jsonify, request, current_app
import random

api_bp = Blueprint('api', __name__)

@api_bp.route("/player", methods=['GET'])
def get_player():
  player = current_app.config['PLAYER']
  return jsonify(player.to_dict())

@api_bp.route("/player", methods=['PUT'])
def update_player():
  player = current_app.config['PLAYER']
  data = request.get_json()
  
  if 'health' in data:
    player.health = max(0, min(player.max_health, data['health']))
  if 'mana' in data:
    player.mana = max(0, min(player.max_mana, data['mana']))
  if 'gold' in data:
    player.gold = max(0, data['gold'])
    
  return get_player()

@api_bp.route("/dialog", methods=['POST'])
def send_dialog_message():
  dialog_engine = current_app.config['DIALOG_ENGINE']
  data = request.get_json()
  
  session_id = data.get('session_id', 'default')
  message = data.get('message', '')
  context = data.get('context', {})
  response = dialog_engine.process_message(message, session_id, context)
  
  return jsonify({
    'speaker': 'NPC',
    'text': response.get('response', 'Nie rozumiem.'),
    'options': response.get('options', [])
  })

@api_bp.route("/conversation_stats")
def conversation_stats():
  dialog_engine = current_app.config['DIALOG_ENGINE']
  stats = dialog_engine.get_conversation_stats()
  return jsonify(stats)

@api_bp.route("/quality_report")
def quality_report():
  dialog_engine = current_app.config['DIALOG_ENGINE']
  report = dialog_engine.get_quality_report()
  return jsonify(report)

@api_bp.route("/session_stats/<session_id>")
def session_stats(session_id):
  dialog_engine = current_app.config['DIALOG_ENGINE']
  stats = dialog_engine.get_conversation_stats(session_id)
  return jsonify(stats)

@api_bp.route("/dialog/<session_id>/history", methods=['GET'])
def get_dialog_history(session_id):
  dialog_engine = current_app.config['DIALOG_ENGINE']
  history = dialog_engine.conversation_history.get(session_id, [])
  messages = []
  for entry in history:
    if isinstance(entry, dict):
      messages.append({
        'speaker': entry.get('speaker', 'Unknown'),
        'text': entry.get('text', ''),
        'timestamp': entry.get('timestamp', None)
      })
    else:
      messages.append({
        'speaker': 'System',
        'text': str(entry),
        'timestamp': None
      })
  
  return jsonify(messages)

@api_bp.route("/quests/available", methods=['GET'])
def get_available_quests():
    quest_system = current_app.config['QUEST_SYSTEM']
    player = current_app.config['PLAYER']
    generated_quests = quest_system.get_available_quests(player)
    active_quests = quest_system.get_player_active_quests(player)
    available_quests = []
    for quest in generated_quests:
        available_quests.append({
            'id': quest.get('id', ''),
            'title': quest.get('title', ''),
            'description': quest.get('description', ''),
            'type': quest.get('type', 'delivery'),
            'reward': {
                'gold': quest.get('reward_gold', 0),
                'experience': quest.get('reward_exp', 0),
                'items': quest.get('reward_items', [])
            },
            'requirements': quest.get('requirements', {}),
            'status': 'available'
        })
    
    return jsonify({
        'quests': available_quests,
        'active_quests': [
            {
                'id': quest.get('id', ''),
                'title': quest.get('title', ''),
                'description': quest.get('description', ''),
                'type': quest.get('type', 'delivery'),
                'reward': {
                    'gold': quest.get('reward_gold', 0),
                    'experience': quest.get('reward_exp', 0),
                    'items': quest.get('reward_items', [])
                },
                'requirements': quest.get('requirements', {}),
                'status': 'active',
                'progress': quest.get('progress', {})
            }
            for quest in active_quests
        ]
    })

@api_bp.route("/shop/items", methods=['GET'])
def get_shop_items():
    merchant_inventory = current_app.config['MERCHANT_INVENTORY']
    items = []
    for item in merchant_inventory:
        items.append({
            'id': item.get('id', ''),
            'name': item.get('name', ''),
            'description': item.get('description', ''),
            'type': item.get('type', 'item'),
            'value': item.get('price', 0),
            'price': item.get('price', 0), 
            'quantity': item.get('quantity', 1),
            'stats': item.get('stats', {}),
            'rarity': item.get('rarity', 'common')
        })
    
    return jsonify({
        'items': items
    })

@api_bp.route("/smithy/recipes", methods=['GET'])
def get_smithy_recipes():
    player = current_app.config['PLAYER']
    crafting_system = current_app.config['CRAFTING_SYSTEM']
    
    try:
        available_recipes = crafting_system.get_available_recipes(player.level)
        recipes_data = []
        
        for recipe_id, recipe in available_recipes.items():
            can_craft, craft_message = crafting_system.can_craft(recipe_id, player)
            
            recipes_data.append({
                'id': recipe_id,
                'name': recipe['name'],
                'description': recipe['description'],
                'type': recipe['result']['type'],
                'cost': recipe['gold_cost'],
                'level_required': recipe['level_required'],
                'crafting_time': recipe['crafting_time'],
                'materials': recipe['materials'],
                'result': recipe['result'],
                'can_craft': can_craft,
                'craft_message': craft_message
            })
        
        return jsonify({
            'success': True,
            'recipes': recipes_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting recipes: {str(e)}'
        })

@api_bp.route("/action", methods=['POST'])
def perform_action():
    data = request.get_json()
    location = data.get('location', '')
    action = data.get('action', '')
    
    player = current_app.config['PLAYER']

    if location == 'forest':
        return handle_forest_action(player, action, data)
    elif location == 'mine':
        return handle_mine_action(player, action, data)
    elif location == 'smithy':
        return handle_smithy_action(player, action, data)
    elif location not in ['', 'tavern', 'shop']:
        return jsonify({
            'success': False,
            'message': f'Unknown location: {location}'
        })
    quest_system = current_app.config['QUEST_SYSTEM']
    
    try:
        if action == 'rest':
            rest_cost = data.get('cost', 0) if data else 0
            
            if rest_cost > 0:
                if player.gold < rest_cost:
                    return jsonify({
                        'success': False,
                        'message': f"You don't have enough gold. Rest costs {rest_cost} gold."
                    })
                
                player.gold -= rest_cost
                player.health = player.max_health
                player.mana = player.max_mana
                
                return jsonify({
                    'success': True,
                    'message': f'You pay {rest_cost} gold and rest comfortably. Your health and mana have been fully restored!',
                    'data': {
                        'health': player.health,
                        'mana': player.mana,
                        'gold': player.gold
                    }
                })
            else:
                player.health = player.max_health
                player.mana = player.max_mana
                return jsonify({
                    'success': True,
                    'message': 'You feel refreshed and ready for adventure!',
                    'data': {
                        'health': player.health,
                        'mana': player.mana
                    }
                })
        
        elif action == 'explore':
            outcomes = [
                'You find a small pouch with 10 gold coins!',
                'You discover nothing of interest.',
                'You hear strange sounds in the distance.',
                'You find some useful herbs.'
            ]
            message = random.choice(outcomes)
            
            if 'gold' in message:
                player.gold += 10
            
            return jsonify({
                'success': True,
                'message': message,
                'data': {
                    'gold': player.gold
                }
            })
            
        elif action == 'mine':
            if random.random() < 0.7:
                ore_types = ['Iron Ore', 'Copper Ore', 'Silver Ore']
                ore = random.choice(ore_types)
                player.inventory.append({
                    'name': ore,
                    'type': 'material',
                    'description': f'Raw {ore.lower()} ready for processing',
                    'value': 5
                })
                return jsonify({
                    'success': True,
                    'message': f'You successfully mined {ore}!',
                    'data': {
                        'item': ore
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'You swing your pickaxe but find nothing valuable.',
                    'data': {}
                })
        
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown action: {action}',
                'data': {}
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error performing action: {str(e)}',
            'data': {}
        })

@api_bp.route("/inventory", methods=['GET'])
def get_inventory():
    player = current_app.config['PLAYER']
    
    inventory_items = getattr(player, 'inventory', [])
    items = []
    
    for i, item in enumerate(inventory_items):
        items.append({
            'id': str(i),
            'name': item.get('name', ''),
            'type': item.get('type', 'item'),
            'quantity': item.get('quantity', 1),
            'description': item.get('description', ''),
            'value': item.get('value', 0),
            'stats': item.get('stats', {}),
            'rarity': item.get('rarity', 'common')
        })
    
    return jsonify(items)

@api_bp.route("/inventory/use", methods=['POST'])
def use_item():
    data = request.get_json()
    item_id = data.get('item_id', '')
    
    player = current_app.config['PLAYER']
    
    try:
        item_index = int(item_id)
        if 0 <= item_index < len(player.inventory):
            item = player.inventory[item_index]
            if item.get('type') == 'potion':
                if 'health' in item.get('effects', {}):
                    health_restore = item['effects']['health']
                    player.health = min(player.max_health, player.health + health_restore)
                    player.inventory.pop(item_index)
                    return jsonify({
                        'success': True,
                        'message': f'You used {item["name"]} and restored {health_restore} health!'
                    })
                elif 'mana' in item.get('effects', {}):
                    mana_restore = item['effects']['mana']
                    player.mana = min(player.max_mana, player.mana + mana_restore)
                    player.inventory.pop(item_index)
                    return jsonify({
                        'success': True,
                        'message': f'You used {item["name"]} and restored {mana_restore} mana!'
                    })
            
            return jsonify({
                'success': False,
                'message': f'{item["name"]} cannot be used.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Item not found in inventory.'
            })
    except (ValueError, IndexError):
        return jsonify({
            'success': False,
            'message': 'Invalid item ID.'
        })

@api_bp.route("/merchant/buy", methods=['POST'])
def buy_item():
    data = request.get_json()
    item_id = data.get('item_id', '')
    quantity = data.get('quantity', 1)
    player = current_app.config['PLAYER']
    merchant_inventory = current_app.config['MERCHANT_INVENTORY']

    item = None
    for merchant_item in merchant_inventory:
        if merchant_item.get('id') == item_id:
            item = merchant_item
            break
    
    if not item:
        return jsonify({
            'success': False,
            'message': 'Item not found in shop.'
        })
    
    total_cost = item.get('price', 0) * quantity
    
    if player.gold < total_cost:
        return jsonify({
            'success': False,
            'message': f'Not enough gold! Need {total_cost}, but you have {player.gold}.'
        })
    
    if item.get('quantity', 0) < quantity:
        return jsonify({
            'success': False,
            'message': f'Not enough items in stock! Only {item.get("quantity", 0)} available.'
        })

    player.gold -= total_cost
    for _ in range(quantity):
        player.inventory.append({
            'name': item['name'],
            'type': item.get('type', 'item'),
            'description': item.get('description', ''),
            'value': item.get('price', 0),
            'effects': item.get('effects', {})
        })
    
    item['quantity'] -= quantity
    
    return jsonify({
        'success': True,
        'message': f'Successfully purchased {quantity}x {item["name"]} for {total_cost} gold!'
    })

@api_bp.route("/merchant/sell", methods=['POST'])
def sell_item():
    data = request.get_json()
    item_id = data.get('item_id', '')
    quantity = data.get('quantity', 1)
    
    player = current_app.config['PLAYER']
    
    try:
        item_index = int(item_id)
        if 0 <= item_index < len(player.inventory):
            item = player.inventory[item_index]
            sell_value = item.get('value', 0) // 2  
            
            player.gold += sell_value
            player.inventory.pop(item_index)
            
            return jsonify({
                'success': True,
                'message': f'Sold {item["name"]} for {sell_value} gold!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Item not found in inventory.'
            })
    except (ValueError, IndexError):
        return jsonify({
            'success': False,
            'message': 'Invalid item ID.'
        })

def handle_forest_action(player, action, data):
    try:
        if action == 'explore':
            return handle_forest_explore(player)
        elif action == 'hunt':
            return handle_forest_hunt(player)
        elif action == 'gather':
            return handle_forest_gather(player)
        elif action == 'search_treasure':
            return handle_forest_treasure_hunt(player)
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown forest action: {action}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error in forest action: {str(e)}'
        })

def handle_forest_explore(player):
    success_chance = 0.6 + (player.level * 0.05)
    
    if random.random() < success_chance:
        discoveries = [
            {
                'name': 'Ancient Map Fragment',
                'type': 'treasure',
                'description': 'A piece of an old treasure map',
                'value': 50,
                'experience': 25
            },
            {
                'name': 'Rare Herb Bundle',
                'type': 'consumable', 
                'description': 'A collection of rare healing herbs',
                'value': 30,
                'health_restore': 40,
                'experience': 15
            },
            {
                'name': 'Forest Crystal',
                'type': 'gem',
                'description': 'A mysterious crystal found deep in the woods',
                'value': 75,
                'experience': 30
            }
        ]
        
        found_item = random.choice(discoveries)
        player.inventory.append({
            'name': found_item['name'],
            'type': found_item['type'],
            'description': found_item['description'],
            'value': found_item['value']
        })

        exp_gain = found_item.get('experience', 10)
        player.experience += exp_gain
        player.check_level_up()
        
        return jsonify({
            'success': True,
            'message': f'You discovered a {found_item["name"]}! (+{exp_gain} experience)',
            'data': {
                'item': found_item,
                'experience': exp_gain,
                'player': player.to_dict()
            }
        })
    else:
        outcomes = [
            'You hear rustling in the bushes but find nothing.',
            'You discover old animal tracks leading deeper into the forest.',
            'You find a small clearing with wildflowers.',
            'You discover an old abandoned campsite.'
        ]
        
        return jsonify({
            'success': True,
            'message': random.choice(outcomes)
        })

def handle_forest_hunt(player):
    if player.health < player.max_health * 0.3:
        return jsonify({
            'success': False,
            'message': 'You are too injured to safely hunt. Rest first!'
        })

    success_chance = 0.5 + (player.level * 0.1) + (player.health / player.max_health * 0.2)
    health_cost = random.randint(5, 15)
    player.health = max(1, player.health - health_cost)
    
    if random.random() < success_chance:
        creatures = [
            {
                'name': 'Forest Rabbit',
                'gold': random.randint(5, 10),
                'experience': random.randint(10, 15),
                'loot': {'name': 'Rabbit Hide', 'value': 8}
            },
            {
                'name': 'Wild Boar', 
                'gold': random.randint(15, 25),
                'experience': random.randint(20, 30),
                'loot': {'name': 'Boar Tusk', 'value': 20}
            },
            {
                'name': 'Forest Wolf',
                'gold': random.randint(20, 35),
                'experience': random.randint(25, 40), 
                'loot': {'name': 'Wolf Pelt', 'value': 30}
            }
        ]
        
        if player.level <= 2:
            creature = creatures[0]  
        elif player.level <= 5:
            creature = random.choice(creatures[:2]) 
        else:
            creature = random.choice(creatures)  

        player.gold += creature['gold']
        player.experience += creature['experience'] 
        player.check_level_up()
        player.inventory.append({
            'name': creature['loot']['name'],
            'type': 'material',
            'description': f'Material obtained from hunting {creature["name"].lower()}',
            'value': creature['loot']['value']
        })
        
        return jsonify({
            'success': True,
            'message': f'You successfully hunted a {creature["name"]}! (+{creature["gold"]} gold, +{creature["experience"]} exp)',
            'data': {
                'creature': creature,
                'health_lost': health_cost,
                'player': player.to_dict()
            }
        })
    else:t
        return jsonify({
            'success': False,
            'message': f'The hunt was unsuccessful. You lost {health_cost} health from the effort.',
            'data': {
                'health_lost': health_cost,
                'player': {
                    'health': player.health
                }
            }
        })

def handle_forest_gather(player):
    mana_cost = 5
    if player.mana < mana_cost:
        return jsonify({
            'success': False,
            'message': 'You are too tired to gather materials effectively. Rest first!'
        })
    
    player.mana = max(0, player.mana - mana_cost)
    materials = [
        {
            'name': 'Oak Wood',
            'type': 'material',
            'description': 'Strong wood suitable for crafting',
            'value': 5,
            'quantity': random.randint(2, 4)
        },
        {
            'name': 'Wild Berries',
            'type': 'consumable', 
            'description': 'Sweet berries that restore health',
            'value': 3,
            'health_restore': 15,
            'quantity': random.randint(3, 6)
        },
        {
            'name': 'Healing Herbs',
            'type': 'consumable',
            'description': 'Medicinal herbs with healing properties', 
            'value': 12,
            'health_restore': 25,
            'quantity': random.randint(1, 3)
        },
        {
            'name': 'Pine Resin',
            'type': 'material',
            'description': 'Sticky resin useful for crafting',
            'value': 8,
            'quantity': random.randint(1, 2)
        }
    ]
    
    gathered_items = random.sample(materials, random.randint(1, 3))
    total_value = 0
    
    for item in gathered_items:
        for _ in range(item['quantity']):
            player.inventory.append({
                'name': item['name'],
                'type': item['type'],
                'description': item['description'],
                'value': item['value']
            })
            total_value += item['value']

    exp_gain = random.randint(5, 10)
    player.experience += exp_gain
    player.check_level_up()
    
    item_names = [f"{item['quantity']}x {item['name']}" for item in gathered_items]
    
    return jsonify({
        'success': True,
        'message': f'You gathered: {", ".join(item_names)} (+{exp_gain} exp)',
        'data': {
            'items': gathered_items,
            'total_value': total_value,
            'experience': exp_gain,
            'mana_cost': mana_cost,
            'player': player.to_dict()
        }
    })

def handle_forest_treasure_hunt(player):
    if player.health < player.max_health * 0.5:
        return jsonify({
            'success': False,
            'message': 'Treasure hunting is too dangerous in your current condition!'
        })
    
    mana_cost = 20
    if player.mana < mana_cost:
        return jsonify({
            'success': False,
            'message': 'You need more energy to conduct a thorough treasure search!'
        })
    
    player.mana = max(0, player.mana - mana_cost)
    danger_roll = random.random()
    
    if danger_roll < 0.3: 
        health_loss = random.randint(15, 30)
        player.health = max(1, player.health - health_loss)
        
        dangers = [
            'You triggered an ancient trap!',
            'Wild wolves attacked during your search!',
            'You fell into a hidden pit!',
            'Poisonous plants affected you!'
        ]
        
        return jsonify({
            'success': False,
            'message': f'{random.choice(dangers)} You lost {health_loss} health.',
            'data': {
                'health_lost': health_loss,
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })
    
    success_chance = 0.4 + (player.level * 0.08)
    
    if random.random() < success_chance:
        treasures = [
            {
                'name': 'Ancient Gold Coins',
                'type': 'treasure',
                'description': 'Old coins from a forgotten civilization',
                'gold_value': random.randint(50, 100),
                'experience': 50
            },
            {
                'name': 'Enchanted Ring',
                'type': 'accessory',
                'description': 'A ring that pulses with magical energy',
                'value': 150,
                'stats': {'intelligence': 2},
                'experience': 75
            },
            {
                'name': 'Rare Gemstone',
                'type': 'gem',
                'description': 'A precious stone that gleams with inner light',
                'value': 200,
                'experience': 60
            },
            {
                'name': 'Ancient Scroll',
                'type': 'treasure',
                'description': 'A scroll containing ancient knowledge',
                'value': 80,
                'experience': 100
            }
        ]
        
        found_treasure = random.choice(treasures)
        
        if 'gold_value' in found_treasure:
            player.gold += found_treasure['gold_value']
            message = f'You found {found_treasure["name"]}! (+{found_treasure["gold_value"]} gold)'
        else:
            player.inventory.append({
                'name': found_treasure['name'],
                'type': found_treasure['type'],
                'description': found_treasure['description'],
                'value': found_treasure['value'],
                'stats': found_treasure.get('stats', {})
            })
            message = f'You found {found_treasure["name"]}! (Worth {found_treasure["value"]} gold)'
        
        exp_gain = found_treasure['experience']
        player.experience += exp_gain
        player.check_level_up()
        
        return jsonify({
            'success': True,
            'message': f'{message} (+{exp_gain} exp)',
            'data': {
                'treasure': found_treasure,
                'experience': exp_gain,
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })
    else:
        return jsonify({
            'success': True,
            'message': 'You searched thoroughly but found no treasure this time.',
            'data': {
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })

def handle_mine_action(player, action, data):   
    try:
        if action == 'shallow_mining':
            return handle_shallow_mining(player)
        elif action == 'deep_mining':
            return handle_deep_mining(player)
        elif action == 'gem_hunting':
            return handle_gem_hunting(player)
        elif action == 'abandoned_exploration':
            return handle_abandoned_exploration(player)
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown mine action: {action}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error in mine action: {str(e)}'
        })

def handle_smithy_action(player, action, data):
    try:
        if action == 'craft':
            return handle_smithy_craft(player, data)
        elif action == 'repair':
            return handle_smithy_repair(player, data)
        elif action == 'upgrade':
            return handle_smithy_upgrade(player, data)
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown smithy action: {action}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error in smithy action: {str(e)}'
        })

def handle_shallow_mining(player):
    mana_cost = 10
    if player.mana < mana_cost:
        return jsonify({
            'success': False,
            'message': 'You are too tired to mine effectively!'
        })
    
    player.mana = max(0, player.mana - mana_cost)
    success_chance = 0.8
    
    if random.random() < success_chance:
        ores = [
            {
                'name': 'Copper Ore',
                'type': 'material',
                'description': 'Common copper ore suitable for basic crafting',
                'value': 8,
                'quantity': random.randint(2, 4)
            },
            {
                'name': 'Iron Ore',
                'type': 'material',
                'description': 'Sturdy iron ore for weapon crafting',
                'value': 12,
                'quantity': random.randint(1, 3)
            },
            {
                'name': 'Coal',
                'type': 'material',
                'description': 'Fuel for forges and smelting',
                'value': 5,
                'quantity': random.randint(3, 6)
            },
            {
                'name': 'Stone',
                'type': 'material',
                'description': 'Solid building stone',
                'value': 3,
                'quantity': random.randint(4, 8)
            }
        ]
        
        mined_ore = random.choice(ores)
        total_value = 0
        for _ in range(mined_ore['quantity']):
            player.inventory.append({
                'name': mined_ore['name'],
                'type': mined_ore['type'],
                'description': mined_ore['description'],
                'value': mined_ore['value']
            })
            total_value += mined_ore['value']
        
        exp_gain = random.randint(8, 15)
        player.experience += exp_gain
        player.check_level_up()
        
        return jsonify({
            'success': True,
            'message': f'You mined {mined_ore["quantity"]}x {mined_ore["name"]}! (+{exp_gain} exp)',
            'data': {
                'ore': mined_ore,
                'total_value': total_value,
                'experience': exp_gain,
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': 'You worked hard but found only worthless rock.',
            'data': {
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })

def handle_deep_mining(player):
    if player.level < 3:
        return jsonify({
            'success': False,
            'message': 'You are not experienced enough for deep mining! (Requires level 3+)'
        })
    
    if player.health < player.max_health * 0.4:
        return jsonify({
            'success': False,
            'message': 'Deep mining is too dangerous in your current condition!'
        })

    mana_cost = 25
    if player.mana < mana_cost:
        return jsonify({
            'success': False,
            'message': 'Deep mining requires significant energy!'
        })
    
    player.mana = max(0, player.mana - mana_cost)
    danger_roll = random.random()
    
    if danger_roll < 0.25: 
        health_loss = random.randint(20, 35)
        player.health = max(1, player.health - health_loss)
        
        dangers = [
            'The tunnel collapsed partially!',
            'You encountered dangerous gas pockets!',
            'Sharp rocks caused injuries!',
            'You got lost in the deep tunnels!'
        ]
        
        return jsonify({
            'success': False,
            'message': f'{random.choice(dangers)} You lost {health_loss} health.',
            'data': {
                'health_lost': health_loss,
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })
    
    success_chance = 0.6 + (player.level * 0.05)
    
    if random.random() < success_chance:
        deep_ores = [
            {
                'name': 'Silver Ore',
                'type': 'material',
                'description': 'Precious silver ore from the deep mines',
                'value': 25,
                'quantity': random.randint(1, 3)
            },
            {
                'name': 'Gold Ore',
                'type': 'material',
                'description': 'Rare gold ore gleaming in the darkness',
                'value': 50,
                'quantity': random.randint(1, 2)
            },
            {
                'name': 'Mithril Ore',
                'type': 'material',
                'description': 'Legendary mithril, lighter than silver but stronger than steel',
                'value': 100,
                'quantity': 1
            },
            {
                'name': 'Rare Crystals',
                'type': 'gem',
                'description': 'Magical crystals found only in the deepest mines',
                'value': 75,
                'quantity': random.randint(1, 2)
            }
        ]

        if player.level >= 7:
            found_ore = random.choice(deep_ores)
        elif player.level >= 5:
            found_ore = random.choice(deep_ores[:3])
        else:
            found_ore = random.choice(deep_ores[:2])
        
        total_value = 0
        for _ in range(found_ore['quantity']):
            player.inventory.append({
                'name': found_ore['name'],
                'type': found_ore['type'],
                'description': found_ore['description'],
                'value': found_ore['value']
            })
            total_value += found_ore['value']
        
        exp_gain = random.randint(30, 50)
        player.experience += exp_gain
        player.check_level_up()
        
        return jsonify({
            'success': True,
            'message': f'Deep mining success! You found {found_ore["quantity"]}x {found_ore["name"]}! (+{exp_gain} exp)',
            'data': {
                'ore': found_ore,
                'total_value': total_value,
                'experience': exp_gain,
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })
    else:
        return jsonify({
            'success': True,
            'message': 'The deep tunnels yielded nothing valuable this time.',
            'data': {
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })

def handle_gem_hunting(player):
    mana_cost = 15
    if player.mana < mana_cost:
        return jsonify({
            'success': False,
            'message': 'Gem hunting requires careful focus and energy!'
        })
    
    player.mana = max(0, player.mana - mana_cost)
    success_chance = 0.4 + (player.level * 0.06)
    
    if random.random() < success_chance:
        gems = [
            {
                'name': 'Quartz Crystal',
                'type': 'gem',
                'description': 'Clear crystal with magical properties',
                'value': 20,
                'rarity': 'common'
            },
            {
                'name': 'Amethyst',
                'type': 'gem',
                'description': 'Beautiful purple gem that enhances magical abilities',
                'value': 45,
                'stats': {'intelligence': 1},
                'rarity': 'uncommon'
            },
            {
                'name': 'Emerald',
                'type': 'gem',
                'description': 'Vibrant green gem that boosts vitality',
                'value': 80,
                'stats': {'vitality': 1},
                'rarity': 'rare'
            },
            {
                'name': 'Ruby',
                'type': 'gem',
                'description': 'Fiery red gem that increases strength',
                'value': 120,
                'stats': {'strength': 1},
                'rarity': 'rare'
            },
            {
                'name': 'Diamond',
                'type': 'gem',
                'description': 'The hardest and most valuable gem',
                'value': 200,
                'stats': {'all_stats': 1},
                'rarity': 'legendary'
            }
        ]

        if player.level >= 8:
            found_gem = random.choice(gems)
        elif player.level >= 5:
            found_gem = random.choice(gems[:4])
        elif player.level >= 3:
            found_gem = random.choice(gems[:3])
        else:
            found_gem = random.choice(gems[:2])
        
        player.inventory.append({
            'name': found_gem['name'],
            'type': found_gem['type'],
            'description': found_gem['description'],
            'value': found_gem['value'],
            'stats': found_gem.get('stats', {}),
            'rarity': found_gem['rarity']
        })
        
        exp_gain = random.randint(20, 35)
        player.experience += exp_gain
        player.check_level_up()
        
        return jsonify({
            'success': True,
            'message': f'You found a {found_gem["rarity"]} {found_gem["name"]}! (+{exp_gain} exp)',
            'data': {
                'gem': found_gem,
                'experience': exp_gain,
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })
    else:
        return jsonify({
            'success': True,
            'message': 'You searched carefully but found no gems this time.',
            'data': {
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })

def handle_abandoned_exploration(player):
    if player.level < 4:
        return jsonify({
            'success': False,
            'message': 'The abandoned shafts are too dangerous for inexperienced miners!'
        })
    
    if player.health < player.max_health * 0.6:
        return jsonify({
            'success': False,
            'message': 'You need to be in better health to explore the abandoned areas!'
        })

    mana_cost = 30
    if player.mana < mana_cost:
        return jsonify({
            'success': False,
            'message': 'Exploring abandoned shafts requires tremendous energy and focus!'
        })
    
    player.mana = max(0, player.mana - mana_cost)
    outcome_roll = random.random()
    
    if outcome_roll < 0.4:  
        health_loss = random.randint(25, 40)
        player.health = max(1, player.health - health_loss)
        
        dangers = [
            'Ancient traps were still active!',
            'The floor gave way to a deeper pit!',
            'Toxic gases from old mining operations affected you!',
            'Unstable supports caused a partial collapse!',
            'You encountered aggressive creatures that made the tunnels their home!'
        ]
        
        return jsonify({
            'success': False,
            'message': f'{random.choice(dangers)} You lost {health_loss} health.',
            'data': {
                'health_lost': health_loss,
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })
    
    elif outcome_roll < 0.7: 
        treasures = [
            {
                'name': 'Masterwork Pickaxe',
                'type': 'tool',
                'description': 'A perfectly balanced pickaxe left by a master miner',
                'value': 150,
                'stats': {'mining_efficiency': 2}
            },
            {
                'name': 'Miner\'s Lucky Charm',
                'type': 'accessory',
                'description': 'An old charm that brings luck in mining',
                'value': 100,
                'stats': {'luck': 2}
            },
            {
                'name': 'Ancient Miner\'s Map',
                'type': 'treasure',
                'description': 'A map showing secret veins and passages',
                'value': 200,
                'gold_bonus': 100
            },
            {
                'name': 'Cache of Rare Ores',
                'type': 'treasure',
                'description': 'A hidden stash of valuable ores',
                'ores': [
                    {'name': 'Platinum Ore', 'value': 80, 'quantity': 2},
                    {'name': 'Mythril Shard', 'value': 120, 'quantity': 1}
                ]
            }
        ]
        
        found_treasure = random.choice(treasures)
        
        if 'gold_bonus' in found_treasure:
            player.gold += found_treasure['gold_bonus']
            message = f'You found {found_treasure["name"]}! (+{found_treasure["gold_bonus"]} gold)'
        elif 'ores' in found_treasure:
            total_value = 0
            for ore in found_treasure['ores']:
                for _ in range(ore['quantity']):
                    player.inventory.append({
                        'name': ore['name'],
                        'type': 'material',
                        'description': f'Rare {ore["name"].lower()} from an ancient cache',
                        'value': ore['value']
                    })
                    total_value += ore['value']
            message = f'You found {found_treasure["name"]}! (Total value: {total_value} gold)'
        else:
            player.inventory.append({
                'name': found_treasure['name'],
                'type': found_treasure['type'],
                'description': found_treasure['description'],
                'value': found_treasure['value'],
                'stats': found_treasure.get('stats', {})
            })
            message = f'You found {found_treasure["name"]}!'
        
        exp_gain = random.randint(50, 80)
        player.experience += exp_gain
        player.check_level_up()
        
        return jsonify({
            'success': True,
            'message': f'{message} (+{exp_gain} exp)',
            'data': {
                'treasure': found_treasure,
                'experience': exp_gain,
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })
    
    else:
        return jsonify({
            'success': True,
            'message': 'You explored the abandoned shafts thoroughly but found nothing of value.',
            'data': {
                'mana_cost': mana_cost,
                'player': player.to_dict()
            }
        })

def handle_smithy_craft(player, data):
    item_id = data.get('itemId', '')
    item_name = data.get('itemName', '')
    item_type = data.get('itemType', '')
    crafting_system = current_app.config.get('CRAFTING_SYSTEM')
    if not crafting_system:
        return jsonify({
            'success': False,
            'message': 'Crafting system not available.'
        })
    
    if item_id in crafting_system.recipes:
        recipe = crafting_system.recipes[item_id]
        can_craft, message = crafting_system.can_craft_recipe(item_id, player)
        
        if not can_craft:
            return jsonify({
                'success': False,
                'message': f'Master Grimbrand says: "{message}"'
            })
        
        result = crafting_system.craft_item(item_id, player)
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'Master Grimbrand has crafted a {recipe["name"]} for you!',
                'data': {
                    'item': result['item'],
                    'player': player.to_dict()
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Crafting failed: {result["message"]}'
            })
    
    else:
        frontend_recipes = {
            'steel_sword': {
                'name': 'Steel Sword',
                'cost': 200,
                'materials': ['Iron Ore', 'Coal'],
                'material_costs': {'Iron Ore': 3, 'Coal': 2},
                'stats': {'strength': 8},
                'type': 'weapon'
            },
            'battle_axe': {
                'name': 'Battle Axe', 
                'cost': 250,
                'materials': ['Iron Ore', 'Wood'],
                'material_costs': {'Iron Ore': 4, 'Wood': 2},
                'stats': {'strength': 10, 'dexterity': -2},
                'type': 'weapon'
            },
            'chainmail': {
                'name': 'Chainmail Armor',
                'cost': 180,
                'materials': ['Iron Ore', 'Leather'],
                'material_costs': {'Iron Ore': 5, 'Leather': 2},
                'stats': {'vitality': 6},
                'type': 'armor'
            },
            'plate_armor': {
                'name': 'Plate Armor',
                'cost': 300,
                'materials': ['Steel Ingot', 'Leather'],
                'material_costs': {'Steel Ingot': 3, 'Leather': 3},
                'stats': {'vitality': 10, 'dexterity': -3},
                'type': 'armor'
            }
        }
        
        if item_id not in frontend_recipes:
            return jsonify({
                'success': False,
                'message': 'Master Grimbrand says: "I don\'t know how to craft that item."'
            })
        
        recipe = frontend_recipes[item_id]
        if player.gold < recipe['cost']:
            return jsonify({
                'success': False,
                'message': f'Master Grimbrand says: "You need {recipe["cost"]} gold for this item, but you only have {player.gold}."'
            })

        has_materials = True
        missing_materials = []
        
        for material, needed in recipe['material_costs'].items():
            player_count = sum(1 for item in player.inventory if material.lower() in item.get('name', '').lower())
            if player_count < needed:
                has_materials = False
                missing_materials.append(f"{needed}x {material}")
        
        if not has_materials:
            return jsonify({
                'success': False,
                'message': f'Master Grimbrand says: "You need these materials: {", ".join(missing_materials)}."'
            })
        
        player.gold -= recipe['cost']
        for material, needed in recipe['material_costs'].items():
            removed = 0
            for i in range(len(player.inventory) - 1, -1, -1):
                if removed >= needed:
                    break
                if material.lower() in player.inventory[i].get('name', '').lower():
                    player.inventory.pop(i)
                    removed += 1

        crafted_item = {
            'name': recipe['name'],
            'type': recipe['type'],
            'description': f'A masterfully crafted {recipe["name"].lower()}',
            'value': recipe['cost'] // 2,
            'stats': recipe['stats']
        }
        
        player.inventory.append(crafted_item)
        exp_gain = random.randint(20, 40)
        player.experience += exp_gain
        player.check_level_up()
        
        return jsonify({
            'success': True,
            'message': f'Master Grimbrand has crafted a {recipe["name"]} for you! (+{exp_gain} exp)',
            'data': {
                'item': crafted_item,
                'experience': exp_gain,
                'player': player.to_dict()
            }
        })

def handle_smithy_repair(player, data):
    item_id = data.get('itemId', '')
    item_name = data.get('itemName', '')
    
    target_item = None
    for item in player.inventory:
        if item.get('name') == item_name or str(item.get('id', '')) == str(item_id):
            target_item = item
            break
    
    if not target_item:
        return jsonify({
            'success': False,
            'message': 'Master Grimbrand says: "I can\'t find that item in your belongings."'
        })
    
    if target_item.get('type') not in ['weapon', 'armor']:
        return jsonify({
            'success': False,
            'message': 'Master Grimbrand says: "I can only repair weapons and armor."'
        })

    base_cost = 20
    item_value = target_item.get('value', 50)
    repair_cost = base_cost + (item_value // 10)
    
    if player.gold < repair_cost:
        return jsonify({
            'success': False,
            'message': f'Master Grimbrand says: "Repairing this {target_item["name"]} will cost {repair_cost} gold."'
        })

    player.gold -= repair_cost

    if 'condition' not in target_item:
        target_item['condition'] = 100
    else:
        target_item['condition'] = min(100, target_item['condition'] + random.randint(40, 60))
    
    target_item['value'] = target_item.get('value', 50) + random.randint(2, 8)
    exp_gain = random.randint(5, 15)
    player.experience += exp_gain
    player.check_level_up()
    
    return jsonify({
        'success': True,
        'message': f'Master Grimbrand has repaired your {target_item["name"]}! It\'s good as new. (+{exp_gain} exp)',
        'data': {
            'item': target_item,
            'cost': repair_cost,
            'experience': exp_gain,
            'player': player.to_dict()
        }
    })

def handle_smithy_upgrade(player, data):
    item_id = data.get('itemId', '')
    item_name = data.get('itemName', '')
    target_item = None
    for item in player.inventory:
        if item.get('name') == item_name or str(item.get('id', '')) == str(item_id):
            target_item = item
            break
    
    if not target_item:
        return jsonify({
            'success': False,
            'message': 'Master Grimbrand says: "I can\'t find that item in your belongings."'
        })

    if target_item.get('type') not in ['weapon', 'armor']:
        return jsonify({
            'success': False,
            'message': 'Master Grimbrand says: "I can only upgrade weapons and armor."'
        })

    current_level = target_item.get('upgrade_level', 0)
    if current_level >= 5:
        return jsonify({
            'success': False,
            'message': 'Master Grimbrand says: "This item has reached its maximum upgrade level."'
        })

    base_cost = 50
    item_value = target_item.get('value', 50)
    upgrade_cost = base_cost + (item_value // 5) + (current_level * 25)
    
    if player.gold < upgrade_cost:
        return jsonify({
            'success': False,
            'message': f'Master Grimbrand says: "Upgrading this {target_item["name"]} will cost {upgrade_cost} gold."'
        })

    material_needed = 'Iron Ore' if current_level < 3 else 'Steel Ingot'
    has_material = any(material_needed.lower() in item.get('name', '').lower() for item in player.inventory)
    
    if not has_material:
        return jsonify({
            'success': False,
            'message': f'Master Grimbrand says: "I need {material_needed} to upgrade this item."'
        })
    
    player.gold -= upgrade_cost
    for i, item in enumerate(player.inventory):
        if material_needed.lower() in item.get('name', '').lower():
            player.inventory.pop(i)
            break

    target_item['upgrade_level'] = current_level + 1
    target_item['value'] = int(target_item.get('value', 50) * 1.2)
    if '+' not in target_item['name']:
        target_item['name'] += f' +{target_item["upgrade_level"]}'
    else:
        target_item['name'] = target_item['name'].split('+')[0].strip() + f' +{target_item["upgrade_level"]}'

    stats = target_item.get('stats', {})
    for stat, value in stats.items():
        if isinstance(value, (int, float)):
            stats[stat] = int(value * 1.1) + 1
    target_item['stats'] = stats
    
    exp_gain = random.randint(15, 30)
    player.experience += exp_gain
    player.check_level_up()
    
    return jsonify({
        'success': True,
        'message': f'Master Grimbrand has upgraded your {target_item["name"]}! It\'s significantly more powerful now. (+{exp_gain} exp)',
        'data': {
            'item': target_item,
            'cost': upgrade_cost,
            'experience': exp_gain,
            'player': player.to_dict()
        }
    })