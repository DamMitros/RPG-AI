from flask import Blueprint, jsonify, request, current_app

shop_bp = Blueprint('shop', __name__)

@shop_bp.route("/shop/items", methods=['GET'])
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

@shop_bp.route("/merchant/buy", methods=['POST'])
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

@shop_bp.route("/merchant/sell", methods=['POST'])
def sell_item():
  data = request.get_json()
  item_id = data.get('item_id', '')
  quantity = data.get('quantity', 1)
  
  player = current_app.config['PLAYER']
  
  print(f"Selling item - ID: {item_id}, Type: {type(item_id)}")
  print(f"Inventory size: {len(player.inventory)}")
  
  try:
    if isinstance(item_id, str) and item_id.isdigit():
      item_index = int(item_id)
    elif isinstance(item_id, int):
      item_index = item_id
    else:
      return jsonify({
        'success': False,
        'message': f'Invalid item ID format: {item_id}'
      })
      
    if 0 <= item_index < len(player.inventory):
      item = player.inventory[item_index]
      sell_value = max(1, item.get('value', 0) // 2)  
      
      player.gold += sell_value
      player.inventory.pop(item_index)
      
      return jsonify({
        'success': True,
        'message': f'Sold {item["name"]} for {sell_value} gold!'
      })
    else:
      return jsonify({
        'success': False,
        'message': f'Item not found in inventory. Index: {item_index}, Inventory size: {len(player.inventory)}'
      })
  except (ValueError, IndexError) as e:
    return jsonify({
      'success': False,
      'message': f'Invalid item ID: {str(e)}'
    })
