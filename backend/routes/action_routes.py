from flask import Blueprint, jsonify, request, current_app
import random

from .forest_routes import handle_forest_action
from .mine_routes import handle_mine_action
from .smithy_routes import handle_smithy_action
from .inventory_routes import handle_inventory_action

action_bp = Blueprint('action', __name__)

@action_bp.route("/action", methods=['POST'])
def perform_action():
  data = request.get_json()
  location = data.get('location', '')
  action = data.get('action', '')
  
  player = current_app.config['PLAYER']
  quest_system = current_app.config['QUEST_SYSTEM']

  if location == 'forest':
    return handle_forest_action(player, action, data)
  elif location == 'mine':
    return handle_mine_action(player, action, data)
  elif location == 'smithy':
    return handle_smithy_action(player, action, data)
  elif location == 'inventory':
    return handle_inventory_action(player, action, data)
  
  try:
    if action == 'observe_your_surroundings':
      observations = [
        'You notice the villagers whispering about strange sounds from the mine.',
        'The merchant Erik seems nervous, constantly looking over his shoulder.',
        'A hooded figure quickly disappears into an alley between buildings.',
        'You spot fresh wolf tracks leading toward the forest.',
        'The tavern keeper appears to be arguing with someone inside.',
        'Strange lights flicker in the mine entrance at night.'
      ]
      message = random.choice(observations)
      quest_updates = quest_system.perform_action(action, location, player)
      
      return jsonify({
        'success': True,
        'message': message,
        'quest_updates': quest_updates
      })
      
    elif action == 'talk_to_townspeople':
      conversations = [
        'Local: "Have you heard about the missing merchant? He was last seen near the mine..."',
        'Villager: "Erik has been acting strange lately. His goods seem... different."',
        'Farmer: "The wolves in the forest have been more aggressive recently."',
        'Child: "My mama says not to go near the old mine after dark!"',
        'Elder: "In my day, the mine was prosperous. Now it brings only trouble."'
      ]
      message = random.choice(conversations)
      
      quest_updates = quest_system.perform_action(action, location, player)
      
      return jsonify({
        'success': True,
        'message': message,
        'quest_updates': quest_updates
      })
      
    elif action == 'follow_a_suspicious_trail':
      outcomes = [
        'You follow the trail but it disappears at the forest edge.',
        'The tracks lead to an abandoned shack with signs of recent activity.',
        'You discover torn fabric caught on a branch - someone passed this way recently.',
        'The trail leads to the mine entrance where it vanishes into the darkness.',
        'You find evidence of a struggle but no sign of what happened.'
      ]
      message = random.choice(outcomes)
      
      quest_updates = quest_system.perform_action(action, location, player)
      
      return jsonify({
        'success': True,
        'message': message,
        'quest_updates': quest_updates
      })
      
    elif action == 'examine_nearby_building':
      findings = [
        'You notice scratch marks on the tavern door - like claw marks.',
        'The shop has new security measures that weren\'t there before.',
        'Windows in several houses show signs of hasty boarding up.',
        'You find a hidden passage between two buildings.',
        'Strange symbols are carved into the foundation stones.'
      ]
      message = random.choice(findings)
      
      quest_updates = quest_system.perform_action(action, location, player)
      
      return jsonify({
        'success': True,
        'message': message,
        'quest_updates': quest_updates
      })
      
    elif action == 'rest':
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
        
        quest_updates = quest_system.perform_action(action, location, player)
        
        return jsonify({
          'success': True,
          'message': f'You pay {rest_cost} gold and rest comfortably. Your health and mana have been fully restored!',
          'data': {
            'health': player.health,
            'mana': player.mana,
            'gold': player.gold
          },
          'quest_updates': quest_updates
        })
      else:
        player.health = player.max_health
        player.mana = player.max_mana
        
        quest_updates = quest_system.perform_action(action, location, player)
        
        return jsonify({
          'success': True,
          'message': 'You feel refreshed and ready for adventure!',
          'data': {
            'health': player.health,
            'mana': player.mana
          },
          'quest_updates': quest_updates
        })
        
    elif action in ['talk_innkeeper', 'talk_regular']:
      quest_updates = quest_system.perform_action(action, location, player)
      
      return jsonify({
        'success': True,
        'message': 'Conversation initiated.',
        'quest_updates': quest_updates
      })
       
    elif action in ['talk_erik', 'talk_merchant', 'browse_wares', 'buy_item', 'sell_item']:
      quest_updates = quest_system.perform_action(action, location, player)
      
      return jsonify({
        'success': True,
        'message': 'Shop action completed.',
        'quest_updates': quest_updates
      })

    elif action in ['talk_blacksmith', 'repair_equipment', 'upgrade_equipment', 'craft_weapon', 'craft_armor']:
      quest_updates = quest_system.perform_action(action, location, player)
      
      return jsonify({
        'success': True,
        'message': 'Smithy action completed.',
        'quest_updates': quest_updates
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
      
      quest_updates = quest_system.perform_action(action, location, player)
      
      return jsonify({
        'success': True,
        'message': message,
        'data': {
          'gold': player.gold
        },
        'quest_updates': quest_updates
      })
      
    else:
      quest_updates = quest_system.perform_action(action, location, player)
      
      if quest_updates:
        return jsonify({
          'success': True,
          'message': f'Quest action "{action}" completed.',
          'quest_updates': quest_updates
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

def handle_inventory_action(player, action, data):
  try:
    if action == 'use':
      item_id = data.get('itemId', '') or data.get('item_id', '')
      
      try:
        item_index = int(item_id)
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
      except (ValueError, IndexError):
        return {
          'success': False,
          'message': 'Invalid item ID.',
          'data': {}
        }
        
    elif action == 'unequip':
      slot = data.get('slot', '')
      
      if not hasattr(player, 'equipment') or slot not in player.equipment:
        return {
          'success': False,
          'message': 'No equipment system or invalid slot.',
          'data': {}
        }
      
      if not player.equipment[slot]:
        return {
          'success': False,
          'message': f'No item equipped in {slot} slot.',
          'data': {}
        }

      item = player.equipment[slot]
      player.inventory.append(item)
      player.equipment[slot] = None
      player.update_stats_based_on_equipment()
      
      return {
        'success': True,
        'message': f'Unequipped {item["name"]}!',
        'data': {'player': player.to_dict()}
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
      'message': f'Error in inventory action: {str(e)}',
      'data': {}
    }

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
    new_stamina = min(max_stamina, old_stamina + stamina_restore)
    player.stamina = new_stamina
    actual_restore = new_stamina - old_stamina
    if actual_restore > 0:
      messages.append(f'restored {actual_restore} stamina')

  if 'experience' in effects:
    exp_gain = effects['experience']
    player.add_experience(exp_gain)
    messages.append(f'gained {exp_gain} experience')

  if item.get('quantity', 1) > 1:
    item['quantity'] -= 1
  else:
    player.inventory.pop(item_index)
  
  message = f'Used {item["name"]}'
  if messages:
    message += ' and ' + ', '.join(messages) + '!'
  else:
    message += '!'
  
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
