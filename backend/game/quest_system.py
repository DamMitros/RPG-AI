import time, random, yaml, os

from ai.quest.generator import QuestGenerator
from game.quest_management import QuestManagement
from game.quest_generation import QuestGeneration
from game.quest_completion import QuestCompletion
from game.quest_progress import QuestProgress
from game.quest_actions import QuestActions

class QuestSystem(QuestManagement, QuestGeneration, QuestCompletion, QuestProgress, QuestActions):
  def __init__(self, dialog_engine=None):
    QuestGeneration.__init__(self)
    
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
      "talk_regular": "tavern",
      "rest": "tavern",

      # Shop actions  
      "buy": "shop",  
      "sell": "shop",  
      "talk": "shop",
      
      # Main Page actions
      "observe_your_surroundings": "mainPage",
      "talk_to_townspeople": "mainPage",
      "follow_a_suspicious_trail": "mainPage",
      "examine_nearby_building": "mainPage",
      
      # Forest actions
      "explore_forest": "forest",
      "hunt_creatures": "forest",
      "gather_materials": "forest",
      "search_treasure": "forest",
      
      # Mine actions
      "shallow_mining": "mine", 
      "deep_mining": "mine",
      "gem_hunting": "mine", 
      "abandoned_exploration": "mine", 
      "talk_mysterious_stranger": "mine", 
      
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
      "seek_information": "any",
    }