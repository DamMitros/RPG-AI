from ai.quest_generator import QuestGenerator
import time, random

class QuestSystem:
    def __init__(self, dialog_engine=None):
        self.quest_generator = QuestGenerator(dialog_engine)
        self.action_locations = {
            "talk_to_bartek": "tavern",
            "investigate_mine": "mine_entrance", 
            "investigate_mine_sounds": "mine_entrance",
            "clear_bandits": "mainPage",  
            "gather_herbs": "mainPage",   
            "talk_to_erik": "tradesman",
            "investigate_items": "tradesman"
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
                "steps": [
                    {"action": "investigate_mine_sounds", "location": "mine_entrance", "description": "Investigate the strange sounds at the mine", "completed": False}
                ]
            },
            "bandit_trouble": {
                "id": "bandit_trouble",
                "title": "Bandit Troubles on Mountain Paths",
                "description": "Traders report increased bandit activity on the mountain trails leading to Stonehaven. Escort missions and bandit clearing operations needed.",
                "contact": "Village guard",
                "reward_gold": 30,
                "reward_exp": 60,
                "type": "combat",
                "requirements": [],
                "completion_requirements": ["clear_bandits"],
                "completed_by": [],
                "time_limit_hours": 24,  
                "steps": [
                    {"action": "clear_bandits", "location": "mainPage", "description": "Patrol the village and clear bandit threats", "completed": False}
                ]
            },
            "herb_gathering": {
                "id": "herb_gathering",
                "title": "Herb Gathering for the Village Healer",
                "description": "The village healer needs rare mountain herbs. Knowledge of herbalism helpful but not required. Dangerous areas - come prepared.",
                "contact": "Village healer",
                "reward_gold": 15,
                "reward_exp": 30,
                "type": "gathering",
                "requirements": [],
                "completion_requirements": ["gather_herbs"],
                "completed_by": [],
                "time_limit_hours": 120,  
                "steps": [
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
    
    def perform_action(self, action, location, player):
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
                        current_step['location'] == location and 
                        not current_step['completed']):
                        
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
                if action in quest.get('completion_requirements', []):
                    if 'requirements_met' not in progress:
                        progress['requirements_met'] = []
                    if action not in progress['requirements_met']:
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
        
        return quest_updates, expired
    
    def get_available_actions_for_location(self, location, player):
        if not hasattr(player, 'active_quests') or not hasattr(player, 'quest_progress'):
            return []
        
        available_actions = []
        
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
                    
                    if (current_step['location'] == location and 
                        not current_step['completed']):
                        
                        available_actions.append({
                            'quest_id': quest_id,
                            'quest_title': quest['title'],
                            'action': current_step['action'],
                            'description': current_step['description'],
                            'location': location
                        })
        
        return available_actions
    
    def get_quest_by_id(self, quest_id):
        if quest_id in self.quests:
            return self.quests[quest_id]
        elif quest_id in self.generated_quests_cache:
            return self.generated_quests_cache[quest_id]
        return None
    
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
    
    def get_quest_details_for_player(self, quest_id, player):
        quest = self.get_quest_by_id(quest_id)
        if not quest:
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
        
        if hasattr(player, 'quest_progress') and quest_id in player.quest_progress:
            progress = player.quest_progress[quest_id]
            
            if 'steps' in quest:
                steps = progress.get('steps', [])
                total_steps = len(steps)
                completed_steps = sum(1 for step in steps if step['completed'])
                
                quest_detail['progress'] = {
                    'type': 'steps',
                    'completed_steps': completed_steps,
                    'total_steps': total_steps,
                    'percentage': int((completed_steps / total_steps) * 100) if total_steps > 0 else 0,
                    'current_step': steps[progress.get('current_step', 0)] if progress.get('current_step', 0) < len(steps) else None,
                    'all_steps': steps
                }
            else:
                total_requirements = len(quest.get('completion_requirements', []))
                met_requirements = len(progress.get('requirements_met', []))
                
                quest_detail['progress'] = {
                    'type': 'requirements',
                    'met_requirements': met_requirements,
                    'total_requirements': total_requirements,
                    'percentage': int((met_requirements / total_requirements) * 100) if total_requirements > 0 else 0,
                    'remaining_requirements': [req for req in quest.get('completion_requirements', []) 
                                            if req not in progress.get('requirements_met', [])]
                }
        
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
