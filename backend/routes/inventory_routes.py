from flask import Blueprint, jsonify, request, current_app

inventory_bp = Blueprint('inventory', __name__)

def handle_consumable_use(player, item, item_index):
  effects = item.get('effects', {})
  messages = []

  if 'health' in effects:
    health_restore = effects['health']
    old_health = player.health
    player.health = min(player.max_health, player.health + health_restore)
    actual_restore = player.health - old_health
    if actual_restore > 0:
      messages.append(f'restored {actual_restore} health')

  if 'mana' in effects:
    mana_restore = effects['mana']
    old_mana = player.mana
    player.mana = min(player.max_mana, player.mana + mana_restore)
    actual_restore = player.mana - old_mana
    if actual_restore > 0:
      messages.append(f'restored {actual_restore} mana')

  if 'stamina' in effects:
    stamina_restore = effects['stamina']
    old_stamina = getattr(player, 'stamina', 100)
    max_stamina = getattr(player, 'max_stamina', 100)
    player.stamina = min(max_stamina, old_stamina + stamina_restore)
    actual_restore = player.stamina - old_stamina
    if actual_restore > 0:
      messages.append(f'restored {actual_restore} stamina')

  player.inventory.pop(item_index)
  if messages:
    effect_msg = ' and '.join(messages)
    message = f'Used {item["name"]} and {effect_msg}!'
  else:
    message = f'Used {item["name"]}!'
  
  return {
    'success': True,
    'message': message,
    'data': {'player': player.to_dict()}
  }

def handle_equipment_use(player, item, item_index):
  item_type = item.get('type')
  
  if not hasattr(player, 'equipment'):
    player.equipment = {
      'weapon': None, 'armor': None, 'helmet': None,
      'boots': None, 'gloves': None, 'ring': None, 'tool': None
    }

  current_equipped = player.equipment.get(item_type)
  if current_equipped:
    player.inventory.append(current_equipped)
  
  player.equipment[item_type] = item
  player.inventory.pop(item_index)
  player.update_stats_based_on_equipment()
  
  return {
    'success': True,
    'message': f'Equipped {item["name"]}!',
    'data': {'player': player.to_dict()}
  }

def handle_inventory_action(player, action, data):
  try:
    if action == 'use':
      item_id = data.get('itemId', '') or data.get('item_id', '')
      print(f"DEBUG: item_id = {item_id}, type = {type(item_id)}")
      print(f"DEBUG: player.inventory length = {len(player.inventory)}")
      print(f"DEBUG: player.inventory = {player.inventory}")
      
      try:
        item_index = int(item_id)
        print(f"DEBUG: parsed item_index = {item_index}")
        if 0 <= item_index < len(player.inventory):
          item = player.inventory[item_index]
          if item.get('type') in ['potion', 'consumable']:
            return handle_consumable_use(player, item, item_index)
          elif item.get('type') in ['weapon', 'armor', 'helmet', 'boots', 'gloves', 'ring', 'tool']:
            return handle_equipment_use(player, item, item_index)
          else:
            return {
              'success': False,
              'message': f'{item["name"]} cannot be used.',
              'data': {}
            }
        else:
          return {
            'success': False,
            'message': 'Item not found in inventory.',
            'data': {}
          }
      except (ValueError, IndexError) as e:
        print(f"DEBUG: Exception in parsing item_id: {e}")
        return {
          'success': False,
          'message': 'Invalid item ID.',
          'data': {}
        }
        
    elif action == 'unequip':
      equipment_slot = data.get('equipment_slot', '')
      print(f"DEBUG: equipment_slot = {equipment_slot}")
      print(f"DEBUG: hasattr(player, 'equipment') = {hasattr(player, 'equipment')}")
      if hasattr(player, 'equipment'):
        print(f"DEBUG: player.equipment = {player.equipment}")
        print(f"DEBUG: equipped item in slot {equipment_slot} = {player.equipment.get(equipment_slot)}")
      
      if hasattr(player, 'equipment') and equipment_slot in player.equipment:
        equipped_item = player.equipment.get(equipment_slot)
        if equipped_item:
          success = player.unequip_item(equipment_slot)
          
          if success:
            player.inventory.append(equipped_item)
            return {
              'success': True,
              'message': f'Unequipped {equipped_item["name"]}!',
              'data': {'player': player.to_dict()}
            }
          else:
            return {
              'success': False,
              'message': f'Failed to unequip item from {equipment_slot} slot.',
              'data': {}
            }
        else:
          return {
            'success': False,
            'message': f'No item equipped in {equipment_slot} slot.',
            'data': {}
          }
      else:
        print(f"DEBUG: Invalid equipment slot or missing equipment system")
        print(f"DEBUG: hasattr(player, 'equipment') = {hasattr(player, 'equipment')}")
        if hasattr(player, 'equipment'):
          print(f"DEBUG: player.equipment keys = {list(player.equipment.keys())}")
          print(f"DEBUG: equipment_slot '{equipment_slot}' in equipment = {equipment_slot in player.equipment}")
        return {
          'success': False,
          'message': 'No equipment system or invalid slot.',
          'data': {}
        }
    else:
      return {
        'success': False,
        'message': f'Unknown inventory action: {action}',
        'data': {}
      }
  except Exception as e:
    return {
      'success': False,
      'message': f'Error handling inventory action: {str(e)}',
      'data': {}
    }

@inventory_bp.route("/use", methods=['POST'])
def inventory_use_item():
  data = request.get_json()
  player = current_app.config['PLAYER']
  
  result = handle_inventory_action(player, 'use', data)
  return jsonify(result)

@inventory_bp.route("/unequip", methods=['POST'])
def inventory_unequip_item():
  data = request.get_json()
  player = current_app.config['PLAYER']
  
  result = handle_inventory_action(player, 'unequip', data)
  return jsonify(result)
