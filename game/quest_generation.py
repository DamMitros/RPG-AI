import time

class QuestGeneration:
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
    templates = [
      {
        "id": f"template_investigation_{int(time.time())}",
        "title": "INVESTIGATE VILLAGE MYSTERIES",
        "description": "Strange occurrences have been reported around the village. Investigate and report your findings.",
        "contact": "Village Elder",
        "reward_gold": 30,
        "reward_exp": 60,
        "type": "investigation",
        "difficulty": "easy",
        "requirements": ["level >= 1"],
        "completion_requirements": ["observe_your_surroundings", "talk_to_townspeople"],
        "completed_by": [],
        "generated": True,
        "generated_at": time.time(),
        "steps": [
          {"action": "observe_your_surroundings", "location": "mainPage", "description": "Look around for anything unusual", "completed": False},
          {"action": "talk_to_townspeople", "location": "mainPage", "description": "Ask locals about recent events", "completed": False}
        ]
      },
      {
        "id": f"template_delivery_{int(time.time())}_2",
        "title": "URGENT PACKAGE DELIVERY",
        "description": "A package needs to be delivered to the tavern keeper. Handle with care.",
        "contact": "Erik the Merchant",
        "reward_gold": 25,
        "reward_exp": 50,
        "type": "delivery",
        "difficulty": "easy",
        "requirements": ["level >= 1"],
        "completion_requirements": ["talk_erik", "talk_innkeeper"],
        "completed_by": [],
        "generated": True,
        "generated_at": time.time(),
        "steps": [
          {"action": "talk_erik", "location": "shop", "description": "Collect the package from Erik", "completed": False},
          {"action": "talk_innkeeper", "location": "tavern", "description": "Deliver to the innkeeper", "completed": False}
        ]
      }
    ]
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