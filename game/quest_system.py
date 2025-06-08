import time, random, yaml, os

from ai.quest.generator import QuestGenerator
from game.quest_management import QuestManagement
from game.quest_generation import QuestGeneration
from game.quest_completion import QuestCompletion
from game.quest_progress import QuestProgress
from game.quest_actions import QuestActions

class QuestSystem(QuestManagement, QuestGeneration, QuestCompletion, QuestProgress, QuestActions):
  def __init__(self, dialog_engine=None):
    self.quest_generator = QuestGenerator(dialog_engine)
    self.generated_quests_cache = {}
    self.last_quest_generation = 0
    self.quests = self._load_static_quests()
    self.action_locations = self._init_action_locations()
    self._pre_generate_quests()
    
  def _load_static_quests(self):
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'quests.yaml')
    with open(config_path, 'r') as f:
      data = yaml.safe_load(f)
    return {q['id']: q for q in data.get('quests', [])}

  def _init_action_locations(self):
    return {
      # Tavern actions
      "talk_innkeeper": "tavern",
      "rest": "tavern",
      "talk_to_local": "tavern",
      "talk_regular": "tavern",
      "listen_to_gossip": "tavern",
      "eavesdrop": "tavern",
      "ask_about_legends": "tavern",
      
      # Shop actions  
      "talk_merchant": "shop",  
      "talk_erik": "shop",  
      "buy_materials": "shop",
      "buy_item": "shop",
      "sell_item": "shop",
      "browse_wares": "shop",
      "investigate_items": "shop",
      
      # Main Page actions
      "observe_your_surroundings": "mainPage",
      "observe_surroundings": "mainPage",
      "talk_to_townspeople": "mainPage",
      "question_locals": "mainPage",
      "follow_suspicious_trail": "mainPage",
      "examine_nearby_building": "mainPage",
      "examine_buildings": "mainPage",
      "clear_bandits": "mainPage",
      "gather_herbs": "mainPage",
      "explore_village": "mainPage",
      "investigate_rumors": "mainPage",
      "patrol_area": "mainPage",
      "scout_location": "mainPage",
      "investigate_disturbance": "mainPage",
      "search_for_clues": "mainPage",
      "help_stranger": "mainPage",
      
      # Forest actions
      "explore_deeper": "forest",
      "hunt_creatures": "forest",
      "gather_materials": "forest",
      "hunt": "forest",
      "explore": "forest",
      "gather": "forest",
      "search_for_treasure": "forest",
      "check_traps": "forest",
      "track_animals": "forest",
      "study_tracks": "forest",
      
      # Mine actions
      "mine_ore": "mine_entrance",
      "shallow_mining": "mine_entrance",
      "deep_mining": "mine_entrance",
      "gem_hunting": "mine_entrance",
      "explore_mine": "mine_entrance",
      
      # Smithy actions
      "craft_equipment": "smithy",
      "talk_blacksmith": "smithy",
      "repair_equipment": "smithy",
      "upgrade_equipment": "smithy",
      "craft_weapon": "smithy",
      "craft_armor": "smithy",
      
      # Dialog actions
      "talk_stranger": "any",
      "help_stranger": "any", 
      "investigate_rumors": "any",
      "question_locals": "mainPage",
      "seek_information": "any",
    }