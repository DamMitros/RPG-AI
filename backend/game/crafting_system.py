import yaml, os

class CraftingSystem:
	def __init__(self):
		self.recipes = {}
		self.available_materials = {}
		self._load_crafting_config()
	
	def _load_crafting_config(self):
		config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'crafting.yaml')
		
		try:
			with open(config_path, 'r', encoding='utf-8') as file:
				config = yaml.safe_load(file)

			if 'recipes' in config:
				self.recipes = config['recipes']
			if 'materials' in config:
				self.available_materials = config['materials']
				
		except FileNotFoundError:
			print(f"Warning: Crafting configuration file not found at {config_path}")
		except yaml.YAMLError as e:
			print(f"Error parsing crafting configuration: {e}")
	
	def get_available_recipes(self, player_level):
		available = {}
		for recipe_id, recipe in self.recipes.items():
			if player_level >= recipe["level_required"]:
				available[recipe_id] = recipe
		return available
	
	def can_craft(self, recipe_id, player):
		if recipe_id not in self.recipes:
			return False, "Recipe not found"
		
		recipe = self.recipes[recipe_id]

		if player.level < recipe["level_required"]:
			return False, f"Level {recipe['level_required']} required"

		if player.gold < recipe["gold_cost"]:
			return False, f"Need {recipe['gold_cost']} gold"

		missing_materials = []
		for material in recipe["materials"]:
			if not self._has_material(player, material["id"], material["quantity"]):
				missing_materials.append(f"{material['quantity']}x {material['name']}")
		
		if missing_materials:
			return False, f"Missing materials: {', '.join(missing_materials)}"
		
		return True, "Can craft"
	
	def craft_item(self, recipe_id, player):
		can_craft, message = self.can_craft(recipe_id, player)
		
		if not can_craft:
			return False, message
		
		recipe = self.recipes[recipe_id]
		for material in recipe["materials"]:
			self._remove_material(player, material["id"], material["quantity"])
		
		player.gold -= recipe["gold_cost"]
		crafted_item = recipe["result"].copy()
		player.add_item(crafted_item)
		
		return True, f"Successfully crafted {recipe['name']}!"
	
	def _has_material(self, player, material_id, quantity):
		count = sum(1 for item in player.inventory if item["id"] == material_id)
		return count >= quantity
	
	def _remove_material(self, player, material_id, quantity):
		removed = 0
		for i in range(len(player.inventory) - 1, -1, -1):
			if removed >= quantity:
				break
			if player.inventory[i]["id"] == material_id:
				del player.inventory[i]
				removed += 1
	
	def get_material_info(self):
		return self.available_materials
