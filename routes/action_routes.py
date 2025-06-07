from flask import Blueprint, jsonify, request, current_app
import random
from .forest_routes import handle_forest_action
from .mine_routes import handle_mine_action
from .smithy_routes import handle_smithy_action

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
