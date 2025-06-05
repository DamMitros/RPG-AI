from ai.quest.generator import QuestGenerator
import time, random
import yaml, os

class QuestSystem:
    def __init__(self, dialog_engine=None):
        self.quest_generator = QuestGenerator(dialog_engine)
        self.generated_quests_cache = {}
        self.last_quest_generation = 0
        self.quests = self._load_static_quests()
        self.action_locations = self._init_action_locations()
        
    def _load_static_quests(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'quests.yaml')
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        return {q['id']: q for q in data.get('quests', [])}

    def _init_action_locations(self):
        return {
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
    
    def perform_action(self, action, location, player, additional_data=None):
        if not hasattr(player, 'active_quests') or not hasattr(player, 'quest_progress'):
            return [], []

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
        
        return quest_updates
    
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

        if hasattr(player, 'quest_progress'):
            player.quest_progress.pop(quest_id, None)
        
        return True
    
    def get_quest_status_summary(self, player):
        active_quests = self.get_player_active_quests(player)
        urgent_quests = [q for q in active_quests if q.get('type') == 'urgent']
        combat_quests = [q for q in active_quests if q.get('type') == 'combat']
        
        return {
            'total_active': len(active_quests),
            'urgent_count': len(urgent_quests),
            'combat_count': len(combat_quests),
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
