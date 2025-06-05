from flask import Blueprint, jsonify, request, current_app
import random

api_bp = Blueprint('api', __name__)

@api_bp.route("/player", methods=['GET'])
def get_player():
  player = current_app.config['PLAYER']
  return jsonify({
    'name': player.name,
    'level': player.level,
    'health': player.health,
    'maxHealth': player.max_health,
    'mana': player.mana,
    'maxMana': player.max_mana,
    'experience': player.experience,
    'gold': player.gold,
    'inventory': [
      {
        'id': str(i),
        'name': item['name'],
        'type': item.get('type', 'item'),
        'quantity': item.get('quantity', 1),
        'description': item.get('description', ''),
        'value': item.get('value', 0)
      }
      for i, item in enumerate(player.inventory)
    ],
    'equippedItems': {
      'weapon': None,
      'armor': None,
      'accessory': None
    },
    'stats': {
      'strength': getattr(player, 'strength', 10),
      'dexterity': getattr(player, 'dexterity', 10),
      'intelligence': getattr(player, 'intelligence', 10),
      'vitality': getattr(player, 'vitality', 10)
    }
  })

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

@api_bp.route("/action", methods=['POST'])
def perform_action():
    data = request.get_json()
    location = data.get('location', '')
    action = data.get('action', '')
    
    player = current_app.config['PLAYER']
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