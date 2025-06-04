class CraftingSystem:
    def __init__(self):
        self.recipes = {
            "iron_sword": {
                "name": "Iron Sword",
                "description": "A sturdy iron sword, sharp and reliable",
                "materials": [
                    {"id": "iron_ingot", "name": "Iron Ingot", "quantity": 3},
                    {"id": "leather_wrap", "name": "Leather Wrap", "quantity": 1}
                ],
                "gold_cost": 25,
                "level_required": 1,
                "crafting_time": "2 hours",
                "result": {
                    "id": "iron_sword",
                    "name": "Iron Sword",
                    "description": "A sturdy iron sword, sharp and reliable",
                    "type": "weapon",
                    "damage": 15,
                    "sell_value": 35
                }
            },
            "steel_dagger": {
                "name": "Steel Dagger",
                "description": "A quick, lightweight blade perfect for stealth",
                "materials": [
                    {"id": "steel_ingot", "name": "Steel Ingot", "quantity": 1},
                    {"id": "leather_wrap", "name": "Leather Wrap", "quantity": 1}
                ],
                "gold_cost": 15,
                "level_required": 1,
                "crafting_time": "1 hour",
                "result": {
                    "id": "steel_dagger",
                    "name": "Steel Dagger",
                    "description": "A quick, lightweight blade perfect for stealth",
                    "type": "weapon",
                    "damage": 8,
                    "sell_value": 20
                }
            },
            "mining_pickaxe": {
                "name": "Reinforced Mining Pickaxe",
                "description": "A heavy-duty pickaxe for breaking through tough rocks",
                "materials": [
                    {"id": "iron_ingot", "name": "Iron Ingot", "quantity": 2},
                    {"id": "oak_handle", "name": "Oak Handle", "quantity": 1}
                ],
                "gold_cost": 20,
                "level_required": 1,
                "crafting_time": "1.5 hours",
                "result": {
                    "id": "mining_pickaxe",
                    "name": "Reinforced Mining Pickaxe",
                    "description": "A heavy-duty pickaxe for breaking through tough rocks",
                    "type": "tool",
                    "mining_bonus": 2,
                    "sell_value": 25
                }
            },
            "leather_armor": {
                "name": "Studded Leather Armor",
                "description": "Light but protective leather armor with metal studs",
                "materials": [
                    {"id": "thick_leather", "name": "Thick Leather", "quantity": 4},
                    {"id": "iron_studs", "name": "Iron Studs", "quantity": 2}
                ],
                "gold_cost": 30,
                "level_required": 2,
                "crafting_time": "3 hours",
                "result": {
                    "id": "leather_armor",
                    "name": "Studded Leather Armor",
                    "description": "Light but protective leather armor with metal studs",
                    "type": "armor",
                    "armor": 5,
                    "sell_value": 40
                }
            },
            "iron_chainmail": {
                "name": "Iron Chainmail",
                "description": "Flexible iron chainmail offering good protection",
                "materials": [
                    {"id": "iron_ingot", "name": "Iron Ingot", "quantity": 5},
                    {"id": "chain_links", "name": "Chain Links", "quantity": 3}
                ],
                "gold_cost": 50,
                "level_required": 3,
                "crafting_time": "4 hours",
                "result": {
                    "id": "iron_chainmail",
                    "name": "Iron Chainmail",
                    "description": "Flexible iron chainmail offering good protection",
                    "type": "armor",
                    "armor": 10,
                    "sell_value": 70
                }
            }
        }
        self.available_materials = {
            "iron_ingot": {"name": "Iron Ingot", "price": 8, "description": "Raw iron ready for forging"},
            "steel_ingot": {"name": "Steel Ingot", "price": 12, "description": "High-quality steel ingot"},
            "leather_wrap": {"name": "Leather Wrap", "price": 3, "description": "Leather strips for weapon grips"},
            "oak_handle": {"name": "Oak Handle", "price": 5, "description": "Sturdy oak wood handle"},
            "thick_leather": {"name": "Thick Leather", "price": 6, "description": "Heavy leather hide for armor"},
            "iron_studs": {"name": "Iron Studs", "price": 4, "description": "Small iron studs for armor"},
            "chain_links": {"name": "Chain Links", "price": 7, "description": "Pre-made iron chain links"}
        }
    
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
