from ai.quest_generator import QuestGenerator
import time, random

class QuestSystem:
    def __init__(self, dialog_engine=None):
        self.quest_generator = QuestGenerator(dialog_engine)
        self.generated_quests_cache = {}
        self.action_locations = {
            "talk_to_bartek": "tavern",
            "investigate_mine": "mine_entrance", 
            "investigate_mine_sounds": "mine_entrance",
            "clear_bandits": "mainPage",  
            "gather_herbs": "mainPage",   
            "talk_to_erik": "tradesman",
            "investigate_items": "tradesman",
            "craft_equipment": "smithy",
            "buy_materials": "tradesman",
            "use_item": "any",
            "mine_ore": "mine_entrance",
            "deliver_item": "any"
        }
        
        self.quests = {
            "missing_miner": {
                "id": "missing_miner",
                "title": "MISSING PERSON - REWARD OFFERED",
                "description": "Tomek the Miner has been missing for three days. Last seen heading toward the old silver mine entrance. Young man, brown hair, wearing mining clothes. His family is desperate for news.",
                "contact": "Bartek at the Tawny Lion Inn",
                "reward_gold": 50,
                "reward_exp": 100,
                "type": "urgent",
                "requirements": [],
                "completion_requirements": ["talk_to_bartek", "investigate_mine"],
                "completed_by": [],
                "time_limit_hours": 48,  
                "steps": [
                    {"action": "talk_to_bartek", "location": "tavern", "description": "Talk to Bartek about missing Tomek", "completed": False},
                    {"action": "investigate_mine", "location": "mine_entrance", "description": "Search the mine entrance for clues", "completed": False}
                ]
            },
            "mine_sounds": {
                "id": "mine_sounds",
                "title": "STRANGE SOUNDS FROM THE MINE",
                "description": "Villagers report hearing unnatural sounds echoing from the abandoned silver mine at night. Brave souls wanted to investigate. Extreme caution advised.",
                "contact": "Village elders",
                "reward_gold": 75,
                "reward_exp": 150,
                "type": "urgent",
                "requirements": ["level >= 2"],
                "completion_requirements": ["investigate_mine_sounds"],
                "completed_by": [],
                "time_limit_hours": 72,  
                "required_items": ["torch", "potion_health_small"],  
                "consumes_items": ["torch"],  
                "steps": [
                    {"action": "buy_materials", "location": "tradesman", "description": "Buy a torch and healing potion from Erik", "completed": False, "required_items": ["torch", "potion_health_small"]},
                    {"action": "investigate_mine_sounds", "location": "mine_entrance", "description": "Investigate the strange sounds at the mine", "completed": False, "consumes_items": ["torch"]}
                ]
            },
            "bandit_trouble": {
                "id": "bandit_trouble",
                "title": "Bandit Troubles on Mountain Paths",
                "description": "Traders report increased bandit activity on the mountain trails leading to Stonehaven. Escort missions and bandit clearing operations needed. Proper weapon recommended.",
                "contact": "Village guard",
                "reward_gold": 40,
                "reward_exp": 80,
                "type": "combat",
                "requirements": [],
                "completion_requirements": ["craft_equipment", "clear_bandits"],
                "completed_by": [],
                "time_limit_hours": 48,  
                "required_items": ["iron_ingot", "leather_wrap"],
                "steps": [
                    {"action": "buy_materials", "location": "tradesman", "description": "Buy materials for weapon crafting", "completed": False, "required_items": ["iron_ingot", "leather_wrap"]},
                    {"action": "craft_equipment", "location": "smithy", "description": "Craft a weapon at Grimbrand's forge", "completed": False, "consumes_items": ["iron_ingot", "leather_wrap"]},
                    {"action": "clear_bandits", "location": "mainPage", "description": "Patrol the village and clear bandit threats", "completed": False}
                ]
            },
            "herb_gathering": {
                "id": "herb_gathering",
                "title": "Herb Gathering for the Village Healer",
                "description": "The village healer needs rare mountain herbs. Knowledge of herbalism helpful but not required. Dangerous areas - come prepared with proper tools.",
                "contact": "Village healer",
                "reward_gold": 25,
                "reward_exp": 40,
                "type": "gathering",
                "requirements": [],
                "completion_requirements": ["craft_equipment", "gather_herbs"],
                "completed_by": [],
                "time_limit_hours": 120,  
                "required_items": ["iron_ingot", "oak_handle"],
                "steps": [
                    {"action": "buy_materials", "location": "tradesman", "description": "Buy materials for gathering tools", "completed": False, "required_items": ["iron_ingot", "oak_handle"]},
                    {"action": "craft_equipment", "location": "smithy", "description": "Craft a mining pickaxe for gathering", "completed": False, "consumes_items": ["iron_ingot", "oak_handle"]},
                    {"action": "gather_herbs", "location": "mainPage", "description": "Search for rare herbs around the village", "completed": False}
                ]
            },
            "investigate_erik": {
                "id": "investigate_erik",
                "title": "Investigate Erik's New Merchandise",
                "description": "Some villagers are concerned about the strange items Erik brought back from his last city trip. Discrete investigation requested.",
                "contact": "Village council",
                "reward_gold": 25,
                "reward_exp": 50,
                "type": "investigation",
                "requirements": [],
                "completion_requirements": ["talk_to_erik", "investigate_items"],
                "completed_by": [],
                "time_limit_hours": 96,  
                "steps": [
                    {"action": "talk_to_erik", "location": "tradesman", "description": "Talk to Erik about his new merchandise", "completed": False},
                    {"action": "investigate_items", "location": "tradesman", "description": "Examine Erik's suspicious items", "completed": False}
                ]
            },
            "mining_expedition": {
                "id": "mining_expedition",
                "title": "MINING EXPEDITION - EXPERIENCED MINERS WANTED",
                "description": "The old silver mine may still have deposits deeper in the tunnels. Need brave souls with proper mining equipment to explore the dangerous depths. Considerable reward for valuable findings.",
                "contact": "Former mine foreman",
                "reward_gold": 100,
                "reward_exp": 200,
                "type": "gathering",
                "requirements": ["level >= 3"],
                "completion_requirements": ["craft_equipment", "mine_ore", "deliver_item"],
                "completed_by": [],
                "time_limit_hours": 96,
                "required_items": ["iron_ingot", "oak_handle", "torch"],
                "consumes_items": ["torch"],
                "steps": [
                    {"action": "buy_materials", "location": "tradesman", "description": "Buy materials for mining equipment", "completed": False, "required_items": ["iron_ingot", "oak_handle", "torch"]},
                    {"action": "craft_equipment", "location": "smithy", "description": "Craft a reinforced mining pickaxe", "completed": False, "consumes_items": ["iron_ingot", "oak_handle"]},
                    {"action": "mine_ore", "location": "mine_entrance", "description": "Mine for valuable ores in the depths", "completed": False, "consumes_items": ["torch"]},
                    {"action": "deliver_item", "location": "tavern", "description": "Report findings to the foreman at the tavern", "completed": False}
                ]
            }
        }

        self.generated_quests_cache = {}
        self.last_quest_generation = 0
        
    def refresh_generated_quests(self, player_level=1, force=False):
        current_time = time.time()

        if force or (current_time - self.last_quest_generation) > 1800:  
            print("Generating new AI quests...")

            self.quest_generator.clean_old_quests()

            new_quests = self.quest_generator.get_all_available_quests(player_level, max_quests=3)
            for quest in new_quests:
                self.generated_quests_cache[quest["id"]] = quest
            
            self.last_quest_generation = current_time
            print(f"Generated {len(new_quests)} new quests")
        
    def get_available_quests(self, player):
        self.refresh_generated_quests(player.level)
        
        available = []

        for quest_id, quest in self.quests.items():
            if player.name not in quest["completed_by"]:
                if self._meets_requirements(quest, player):
                    available.append(quest)

        for quest_id, quest in self.generated_quests_cache.items():
            if player.name not in quest["completed_by"]:
                if self._meets_requirements(quest, player):
                    available.append(quest)
        
        return available
    
    def _meets_requirements(self, quest, player):
        for req in quest["requirements"]:
            if "level >=" in req:
                required_level = int(req.split(">=")[1].strip())
                if player.level < required_level:
                    return False
        return True
        return True
    
    def accept_quest(self, quest_id, player):
        if not hasattr(player, 'active_quests'):
            player.active_quests = []
        if not hasattr(player, 'quest_start_times'):
            player.quest_start_times = {}
        if not hasattr(player, 'quest_progress'):
            player.quest_progress = {}

        quest_found = False
        quest = None
        if quest_id in self.quests:
            quest = self.quests[quest_id]
            quest_found = True
        elif quest_id in self.generated_quests_cache:
            quest = self.generated_quests_cache[quest_id]
            quest_found = True
        
        if quest_found and quest_id not in player.active_quests:
            player.active_quests.append(quest_id)
            player.quest_start_times[quest_id] = time.time()
            
            if 'steps' in quest:
                player.quest_progress[quest_id] = {
                    'completed_steps': [],
                    'current_step': 0,
                    'steps': [step.copy() for step in quest['steps']]
                }
            else:
                player.quest_progress[quest_id] = {
                    'completed_steps': [],
                    'requirements_met': []
                }
            
            return True
        return False
    
    def check_quest_time_limits(self, player):
        if not hasattr(player, 'active_quests') or not hasattr(player, 'quest_start_times'):
            return []
        
        current_time = time.time()
        expired_quests = []
        
        for quest_id in player.active_quests[:]:  
            if quest_id in player.quest_start_times:
                quest = self.get_quest_by_id(quest_id)
                if quest and 'time_limit_hours' in quest:
                    time_limit_seconds = quest['time_limit_hours'] * 3600
                    elapsed_time = current_time - player.quest_start_times[quest_id]
                    
                    if elapsed_time > time_limit_seconds:
                        expired_quests.append(quest)
                        player.active_quests.remove(quest_id)
                        player.quest_start_times.pop(quest_id, None)
                        player.quest_progress.pop(quest_id, None)
        
        return expired_quests
    
    def get_quest_time_remaining(self, quest_id, player):
        if not hasattr(player, 'quest_start_times') or quest_id not in player.quest_start_times:
            return None
        
        quest = self.get_quest_by_id(quest_id)
        if not quest or 'time_limit_hours' not in quest:
            return None
        
        current_time = time.time()
        elapsed_time = current_time - player.quest_start_times[quest_id]
        remaining_seconds = (quest['time_limit_hours'] * 3600) - elapsed_time
        
        return max(0, remaining_seconds / 3600)
    
    def perform_action(self, action, location, player, additional_data=None):
        if not hasattr(player, 'active_quests') or not hasattr(player, 'quest_progress'):
            return [], []

        expired = self.check_quest_time_limits(player)
        quest_updates = []
        
        for quest_id in player.active_quests:
            quest = self.get_quest_by_id(quest_id)
            if not quest:
                continue
            
            progress = player.quest_progress.get(quest_id, {})

            if 'steps' in quest:
                steps = progress.get('steps', [])
                current_step_index = progress.get('current_step', 0)
                
                if current_step_index < len(steps):
                    current_step = steps[current_step_index]
                    
                    if (current_step['action'] == action and 
                        (current_step['location'] == location or location == "any") and not current_step['completed']):

                        can_complete = True
                        missing_items = []
                        
                        if 'required_items' in current_step:
                            for required_item in current_step['required_items']:
                                if not player.has_item(required_item):
                                    can_complete = False
                                    missing_items.append(required_item)
                        
                        if can_complete:
                            if 'consumes_items' in current_step:
                                for item_id in current_step['consumes_items']:
                                    player.remove_item(item_id)
                            
                            current_step['completed'] = True
                            if 'completed_steps' not in progress:
                                progress['completed_steps'] = []
                            progress['completed_steps'].append(action)
                            progress['current_step'] = current_step_index + 1
                            
                            quest_updates.append({
                                'quest_id': quest_id,
                                'quest_title': quest['title'],
                                'action': action,
                                'step_description': current_step['description'],
                                'step_completed': True,
                                'quest_completed': progress['current_step'] >= len(steps)
                            })
                            
                            if progress['current_step'] >= len(steps):
                                completed_quest = self.complete_quest(quest_id, player)
                                if completed_quest:
                                    quest_updates[-1]['rewards'] = {
                                        'gold': completed_quest['reward_gold'],
                                        'exp': completed_quest['reward_exp']
                                    }
                        else:
                            quest_updates.append({
                                'quest_id': quest_id,
                                'quest_title': quest['title'],
                                'action': action,
                                'step_completed': False,
                                'error': f"Missing required items: {', '.join(missing_items)}"
                            })
            else:
                if action in quest.get('completion_requirements', []):
                    if 'requirements_met' not in progress:
                        progress['requirements_met'] = []
                    if action not in progress['requirements_met']:
                        can_complete = True
                        missing_items = []
                        
                        if 'required_items' in quest:
                            for required_item in quest['required_items']:
                                if not player.has_item(required_item):
                                    can_complete = False
                                    missing_items.append(required_item)
                        
                        if can_complete:
                            if 'consumes_items' in quest:
                                for item_id in quest['consumes_items']:
                                    player.remove_item(item_id)
                            
                            progress['requirements_met'].append(action)
                            
                            quest_updates.append({
                                'quest_id': quest_id,
                                'quest_title': quest['title'],
                                'action': action,
                                'requirement_met': True,
                                'quest_completed': len(progress['requirements_met']) >= len(quest['completion_requirements'])
                            })

                            if len(progress['requirements_met']) >= len(quest['completion_requirements']):
                                completed_quest = self.complete_quest(quest_id, player)
                                if completed_quest:
                                    quest_updates[-1]['rewards'] = {
                                        'gold': completed_quest['reward_gold'],
                                        'exp': completed_quest['reward_exp']
                                    }
                        else:
                            quest_updates.append({
                                'quest_id': quest_id,
                                'quest_title': quest['title'],
                                'action': action,
                                'requirement_met': False,
                                'error': f"Missing required items: {', '.join(missing_items)}"
                            })
        
        return quest_updates, expired
    
    def check_quest_completion(self, quest_id, player):
        quest = self.get_quest_by_id(quest_id)
        if not quest or quest_id not in getattr(player, 'active_quests', []):
            return None
        
        if not hasattr(player, 'quest_progress') or quest_id not in player.quest_progress:
            return None
        
        progress = player.quest_progress[quest_id]

        if 'steps' in quest:
            steps = progress.get('steps', [])
            if len(steps) > 0 and all(step['completed'] for step in steps):
                return self.complete_quest(quest_id, player)

        elif 'completion_requirements' in quest:
            requirements_met = progress.get('requirements_met', [])
            if set(requirements_met) >= set(quest['completion_requirements']):
                return self.complete_quest(quest_id, player)
        
        return None
    
    def get_quest_progress_display(self, quest_id, player):
        quest = self.get_quest_by_id(quest_id)
        if not quest:
            return None
        
        if not hasattr(player, 'quest_progress') or quest_id not in player.quest_progress:
            return None
        
        progress = player.quest_progress[quest_id]
        display_info = []
        
        if 'steps' in quest:
            steps = progress.get('steps', [])
            current_step_index = progress.get('current_step', 0)
            
            for i, step_progress in enumerate(steps):
                step_info = {
                    'description': step_progress['description'],
                    'completed': step_progress['completed'],
                    'is_current': i == current_step_index and not step_progress['completed'],
                    'missing_items': []
                }

                if not step_progress['completed'] and i == current_step_index:
                    if 'required_items' in step_progress:
                        for item in step_progress['required_items']:
                            if not player.has_item(item):
                                step_info['missing_items'].append(item)
                
                display_info.append(step_info)
        
        elif 'completion_requirements' in quest:
            requirements_met = progress.get('requirements_met', [])
            for req in quest['completion_requirements']:
                req_info = {
                    'description': self.get_requirement_description(req),
                    'completed': req in requirements_met,
                    'is_current': req not in requirements_met,
                    'missing_items': []
                }

                if req not in requirements_met:
                    if 'required_items' in quest:
                        for item in quest['required_items']:
                            if not player.has_item(item):
                                req_info['missing_items'].append(item)
                
                display_info.append(req_info)
        
        return display_info
    
    def get_requirement_description(self, requirement):
        descriptions = {
            'talk_to_erik': 'Talk to Erik at the shop',
            'buy_materials': 'Purchase required materials',
            'craft_iron_sword': 'Craft an iron sword',
            'craft_steel_armor': 'Craft steel armor',
            'visit_mine': 'Visit the mine',
            'mine_ore': 'Mine some ore',
            'explore_forest': 'Explore the forest',
            'hunt_wolf': 'Hunt a wolf'
        }
        return descriptions.get(requirement, requirement.replace('_', ' ').title())

    def complete_quest(self, quest_id, player):
        quest = self.get_quest_by_id(quest_id)
        if not quest:
            return None
        
        if hasattr(player, 'active_quests') and quest_id in player.active_quests:
            player.active_quests.remove(quest_id)
        if hasattr(player, 'quest_start_times'):
            player.quest_start_times.pop(quest_id, None)
        if hasattr(player, 'quest_progress'):
            player.quest_progress.pop(quest_id, None)

        quest['completed_by'].append(player.name)

        if 'reward_gold' in quest:
            player.gold += quest['reward_gold']
        if 'reward_exp' in quest:
            player.experience += quest['reward_exp']
            player.check_level_up()
        
        return quest
    
    def get_player_active_quests(self, player):
        if not hasattr(player, 'active_quests'):
            return []
        
        active_quest_details = []
        
        for quest_id in player.active_quests:
            quest = self.get_quest_by_id(quest_id)
            if quest:
                quest_detail = self.get_quest_details_for_player(quest_id, player)
                if quest_detail:
                    active_quest_details.append(quest_detail)
        
        return active_quest_details
    
    def get_quest_by_id(self, quest_id):
        if quest_id in self.quests:
            return self.quests[quest_id]
        elif hasattr(self, 'generated_quests_cache') and quest_id in self.generated_quests_cache:
            return self.generated_quests_cache[quest_id]
        return None
    
    def get_quest_details_for_player(self, quest_id, player):
        quest = self.get_quest_by_id(quest_id)
        if not quest:
            return None
        
        completed_quest = self.check_quest_completion(quest_id, player)
        if completed_quest:
            return None 
        
        quest_detail = {
            'id': quest['id'],
            'title': quest['title'],
            'description': quest['description'],
            'type': quest.get('type', 'standard'),
            'reward_gold': quest.get('reward_gold', 0),
            'reward_exp': quest.get('reward_exp', 0),
            'contact': quest.get('contact', 'Unknown'),
            'time_remaining_hours': self.get_quest_time_remaining(quest_id, player),
            'is_active': quest_id in getattr(player, 'active_quests', [])
        }
        
        progress_display = self.get_quest_progress_display(quest_id, player)
        if progress_display:
            quest_detail['progress'] = progress_display
        
        return quest_detail
        
        return quest_detail
    
    def abandon_quest(self, quest_id, player):
        if not hasattr(player, 'active_quests') or quest_id not in player.active_quests:
            return False

        player.active_quests.remove(quest_id)

        if hasattr(player, 'quest_start_times'):
            player.quest_start_times.pop(quest_id, None)
        if hasattr(player, 'quest_progress'):
            player.quest_progress.pop(quest_id, None)
        
        return True
    
    def get_quest_status_summary(self, player):
        expired = self.check_quest_time_limits(player)
        active_quests = self.get_player_active_quests(player)
        urgent_quests = [q for q in active_quests if q.get('type') == 'urgent']
        combat_quests = [q for q in active_quests if q.get('type') == 'combat']
        
        return {
            'total_active': len(active_quests),
            'urgent_count': len(urgent_quests),
            'combat_count': len(combat_quests),
            'expired_count': len(expired),
            'expired_quests': expired,
            'active_quests': active_quests
        }
    
    def get_available_actions_for_location(self, location, player):
        available_actions = []
        
        if not hasattr(player, 'active_quests'):
            return available_actions
        
        for quest_id in player.active_quests:
            quest = self.get_quest_by_id(quest_id)
            if not quest:
                continue

            if 'steps' in quest and hasattr(player, 'quest_progress') and quest_id in player.quest_progress:
                progress = player.quest_progress[quest_id]
                current_step_index = progress.get('current_step', 0)
                steps = progress.get('steps', [])
                
                if current_step_index < len(steps):
                    current_step = steps[current_step_index]
                    step_location = current_step.get('location', '')
                    
                    if step_location == location and not current_step.get('completed', False):
                        action_info = {
                            'action': current_step.get('action', ''),
                            'description': current_step.get('description', ''),
                            'quest_id': quest_id,
                            'quest_title': quest['title'],
                            'step_index': current_step_index
                        }
                        available_actions.append(action_info)

            elif 'completion_requirements' in quest:
                quest_location = quest.get('location', '')
                if quest_location == location:
                    progress = player.quest_progress.get(quest_id, {})
                    requirements_met = progress.get('requirements_met', [])
                    
                    for requirement in quest['completion_requirements']:
                        if requirement not in requirements_met:
                            if self._can_perform_action_at_location(requirement, location):
                                action_info = {
                                    'action': requirement,
                                    'description': self.get_requirement_description(requirement),
                                    'quest_id': quest_id,
                                    'quest_title': quest['title']
                                }
                                available_actions.append(action_info)
        
        return available_actions
    
    def _can_perform_action_at_location(self, action, location):
        location_actions = {
            'mainPage': ['explore_village', 'rest'],
            'tavern': ['talk_to_barkeep', 'gather_info', 'recruit_help'],
            'tradesman': ['talk_to_erik', 'buy_materials', 'negotiate'],
            'smithy': ['craft_iron_sword', 'craft_steel_armor', 'craft_tools', 'repair_equipment'],
            'mine_entrance': ['visit_mine', 'mine_ore', 'explore_tunnels'],
            'forest': ['hunt_wolf', 'explore_forest', 'gather_herbs'],
            'inventory': ['use_item', 'equip_item']
        }
        
        return action in location_actions.get(location, [])
