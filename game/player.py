class Player:
  def __init__(self, name):
    self.name = name
    self.level = 1
    self.experience = 0
    self.gold = 100
    self.inventory = []
    self.skills = []
    self.health = 100
    self.mana = 100
    self.strength = 10
    self.agility = 10
    self.intelligence = 10
    self.charisma = 10
    self.luck = 10
    self.stamina = 10
    self.armor = 0
    self.active_quests = []
    self.completed_quests = []
    self.quest_progress = {}
    self.quest_start_times = {}
    self.experience_thresholds = {
        1: 0, 2: 100, 3: 250, 4: 450, 5: 700,
        6: 1000, 7: 1350, 8: 1750, 9: 2200, 10: 2700
    }

  def add_item(self, item):
    self.inventory.append(item)

  def has_item(self, item_id):
    return any(item["id"] == item_id for item in self.inventory)

  def remove_item(self, item_id):
    for i, item in enumerate(self.inventory):
      if item["id"] == item_id:
        del self.inventory[i]
        return True 
    return False 
  
  def check_level_up(self):
    while self.level < 10 and self.experience >= self.experience_thresholds.get(self.level + 1, float('inf')):
        self.level += 1
        self.health += 20
        self.mana += 15
        self.strength += 2
        self.agility += 2
        self.intelligence += 2
        print(f"Congratulations! {self.name} reached level {self.level}!")
        return True
    return False
  
  def get_experience_to_next_level(self):
    if self.level >= 10:
        return 0
    return self.experience_thresholds[self.level + 1] - self.experience
  
  def add_experience(self, exp):
    self.experience += exp
    return self.check_level_up()
  
  def add_gold(self, amount):
    self.gold += amount

  def __repr__(self):
    return f"Player({self.name}, Level: {self.level}, Gold: {self.gold})"