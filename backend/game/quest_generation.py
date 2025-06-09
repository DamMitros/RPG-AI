import time, yaml, os

class QuestGeneration:
  def __init__(self):
    self.quest_templates = {}
    self._load_quest_templates()
    
  def _load_quest_templates(self):
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'quest_templates.yaml')
    
    try:
      with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        
      if 'quest_templates' in config:
        self.quest_templates = config['quest_templates']
        
    except FileNotFoundError:
      print(f"Warning: Quest templates configuration file not found at {config_path}")
    except yaml.YAMLError as e:
      print(f"Error parsing quest templates configuration: {e}")

  def _pre_generate_quests(self):
    print("Pre-generating initial quest pool...")
    self.quest_generator.clean_old_quests()

    for level in range(1, 4):  
      new_quests = self.quest_generator.get_all_available_quests(level, max_quests=1)
      for quest in new_quests:
        self.generated_quests_cache[quest["id"]] = quest
    
    template_quests = self._generate_quick_template_quests()
    for quest in template_quests:
      self.generated_quests_cache[quest["id"]] = quest
        
    print(f"Pre-generated {len(self.generated_quests_cache)} quests")
    
  def _generate_quick_template_quests(self):
    templates = []
    current_time = time.time()
    
    for template_id, template_data in self.quest_templates.items():
      quest = template_data.copy()
      quest["id"] = f"template_{template_id}_{int(current_time)}"
      quest["completed_by"] = []
      quest["generated"] = True
      quest["generated_at"] = current_time
      
      if "completion_requirements" not in quest and "steps" in quest:
        quest["completion_requirements"] = [step["action"] for step in quest["steps"]]
      
      templates.append(quest)
      current_time += 1 
    
    return templates
    
  def refresh_generated_quests(self, player_level=1, force=False):
    current_time = time.time()

    if force or (current_time - self.last_quest_generation) > 1800:  
      print("Generating new AI quests...")

      self.quest_generator.clean_old_quests()
      new_quests = self.quest_generator.get_all_available_quests(player_level, max_quests=5)
      for quest in new_quests:
        self.generated_quests_cache[quest["id"]] = quest
      
      self.last_quest_generation = current_time
      print(f"Generated {len(new_quests)} new quests")
        
  def manual_refresh_quests(self, player_level=1):
    print("Manually refreshing quest pool...")
    current_time = time.time()
    
    self.quest_generator.clean_old_quests()
    new_quests = self.quest_generator.get_all_available_quests(player_level, max_quests=3)
    
    for quest in new_quests:
      self.generated_quests_cache[quest["id"]] = quest
    
    self.last_quest_generation = current_time
    print(f"Manually generated {len(new_quests)} new quests")
    return len(new_quests)
    
  def maintain_quest_pool(self, player_level=1):
    current_available = len([q for q in self.generated_quests_cache.values() 
                            if q.get('reward_gold', 0) > 0]) 
    if current_available < 8:
      additional_quests = self.quest_generator.get_all_available_quests(
        player_level, max_quests=3
      )
      for quest in additional_quests:
        self.generated_quests_cache[quest["id"]] = quest
      print(f"Maintained quest pool: added {len(additional_quests)} quests")
        
  def quick_generate_quests(self, player_level=1, count=3):
    print(f"Quick-generating {count} template quests...")
    new_quests = self.quest_generator.get_template_quests_only(player_level, count)
    
    for quest in new_quests:
      self.generated_quests_cache[quest["id"]] = quest
        
    print(f"Quick-generated {len(new_quests)} quests")
    return new_quests