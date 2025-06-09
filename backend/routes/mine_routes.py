from flask import Blueprint, jsonify, request, current_app
import random

mine_bp = Blueprint('mine', __name__)

@mine_bp.route("/mine/action", methods=['POST'])
def mine_action():
	data = request.get_json()
	action = data.get('action', '')
	player = current_app.config['PLAYER']
	
	return handle_mine_action(player, action, data)

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
		elif action == 'talk_mysterious_stranger':
			return handle_mysterious_stranger_interaction(player)
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

def handle_mysterious_stranger_interaction(player):
	return jsonify({
		'success': True,
		'message': 'A cloaked figure emerges from the shadows between the mine supports...',
		'data': {
			'character': 'mysterious_stranger',
			'player': player.to_dict()
		}
	})
