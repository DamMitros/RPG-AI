from flask import Blueprint, jsonify, request, current_app

player_bp = Blueprint('player', __name__)

@player_bp.route("/player", methods=['GET'])
def get_player():
  player = current_app.config['PLAYER']
  return jsonify(player.to_dict())

@player_bp.route("/player", methods=['PUT'])
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

@player_bp.route("/inventory", methods=['GET'])
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
