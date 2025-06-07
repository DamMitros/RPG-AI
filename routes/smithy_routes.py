from flask import Blueprint, jsonify, request, current_app
import random

smithy_bp = Blueprint('smithy', __name__)

@smithy_bp.route("/smithy/recipes", methods=['GET'])
def get_smithy_recipes():
    player = current_app.config['PLAYER']
    crafting_system = current_app.config.get('CRAFTING_SYSTEM')
    
    try:
        if not crafting_system:
            fallback_recipes = {
                'iron_sword': {
                    'name': 'Iron Sword',
                    'description': 'A sturdy iron sword',
                    'gold_cost': 50,
                    'level_required': 1,
                    'crafting_time': '2 hours',
                    'materials': [{'name': 'Iron Ingot', 'quantity': 3}],
                    'result': {'type': 'weapon'}
                },
                'steel_dagger': {
                    'name': 'Steel Dagger', 
                    'description': 'A quick blade',
                    'gold_cost': 30,
                    'level_required': 1,
                    'crafting_time': '1 hour',
                    'materials': [{'name': 'Steel Ingot', 'quantity': 1}],
                    'result': {'type': 'weapon'}
                }
            }
            
            recipes_data = []
            for recipe_id, recipe in fallback_recipes.items():
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
                    'can_craft': True,
                    'craft_message': 'Available'
                })
                
            return jsonify({
                'success': True,
                'recipes': recipes_data
            })
        
        available_recipes = crafting_system.get_available_recipes(player.level)
        recipes_data = []
        
        for recipe_id, recipe in available_recipes.items():
            can_craft, craft_message = crafting_system.can_craft(recipe_id, player)
            recipe_with_id = recipe.copy()
            recipe_with_id['id'] = recipe_id
            
            recipe_data = {
                'id': recipe_id,
                'name': recipe_with_id.get('name', 'Unknown Recipe'),
                'description': recipe_with_id.get('description', 'No description'),
                'type': recipe_with_id.get('result', {}).get('type', 'item'),
                'cost': recipe_with_id.get('gold_cost', 0),
                'level_required': recipe_with_id.get('level_required', 1),
                'crafting_time': recipe_with_id.get('crafting_time', '1 hour'),
                'materials': recipe_with_id.get('materials', []),
                'result': recipe_with_id.get('result', {}),
                'can_craft': can_craft,
                'craft_message': craft_message
            }
            recipes_data.append(recipe_data)
        
        return jsonify({
            'success': True,
            'recipes': recipes_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting recipes: {str(e)}'
        })

@smithy_bp.route("/smithy/action", methods=['POST'])
def smithy_action():
    data = request.get_json()
    action = data.get('action', '')
    player = current_app.config['PLAYER']
    
    return handle_smithy_action(player, action, data)

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
