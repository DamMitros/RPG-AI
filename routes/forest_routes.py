from flask import Blueprint, jsonify, request, current_app
import random

forest_bp = Blueprint('forest', __name__)

@forest_bp.route("/forest/action", methods=['POST'])
def forest_action():
	data = request.get_json()
	action = data.get('action', '')
	player = current_app.config['PLAYER']
	
	return handle_forest_action(player, action, data)

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
	else:
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
