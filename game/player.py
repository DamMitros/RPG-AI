class Player:
  def __init__(self, name):
    self.name = name
    self.level = 1
    self.experience = 0
    self.gold = 100
    self.inventory = []
    self.skills = []
    self.health = 100
    self.max_health = 100
    self.mana = 100
    self.max_mana = 100
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
    self.completed_quest_ids = set()
    self.completed_quest_types = {}
    self.experience_thresholds = {
        1: 0, 2: 100, 3: 250, 4: 450, 5: 700,
        6: 1000, 7: 1350, 8: 1750, 9: 2200, 10: 2700
    }
    self.equipment = {
        'weapon': None,  
        'armor': None,     
        'helmet': None,    
        'boots': None,     
        'gloves': None,  
        'ring': None,       
        'tool': None       
    }
    self.base_strength = self.strength
    self.base_agility = self.agility
    self.base_intelligence = self.intelligence
    self.base_charisma = self.charisma
    self.base_armor = self.armor

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
        self.max_health += 20
        self.health += 20 
        self.max_mana += 15
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
    
  def mark_quest_completed(self, quest_id, quest_type=None):
    if not hasattr(self, 'completed_quest_ids'):
      self.completed_quest_ids = set()
    if not hasattr(self, 'completed_quest_types'):
      self.completed_quest_types = {}
      
    self.completed_quest_ids.add(quest_id)
    if quest_type:
      if quest_type not in self.completed_quest_types:
        self.completed_quest_types[quest_type] = 0
      self.completed_quest_types[quest_type] += 1
  
  def has_completed_quest(self, quest_id):
    if not hasattr(self, 'completed_quest_ids'):
      self.completed_quest_ids = set()
    return quest_id in self.completed_quest_ids
    
  def get_completed_quest_count_by_type(self, quest_type):
    if not hasattr(self, 'completed_quest_types'):
      self.completed_quest_types = {}
    return self.completed_quest_types.get(quest_type, 0)
  
  def equip_item(self, item):
    item_type = item.get('type')
    if item_type and item_type in self.equipment:
      self.equipment[item_type] = item
      self.update_stats_based_on_equipment()
      return True
    return False

  def unequip_item(self, item_type):
    if item_type in self.equipment:
      self.equipment[item_type] = None
      self.update_stats_based_on_equipment()
      return True
    return False

  def update_stats_based_on_equipment(self):
    self.strength = self.base_strength
    self.agility = self.base_agility
    self.intelligence = self.base_intelligence
    self.charisma = self.base_charisma
    self.armor = self.base_armor

    for item in self.equipment.values():
      if item:
        self.strength += item.get('strength', 0)
        self.agility += item.get('agility', 0)
        self.intelligence += item.get('intelligence', 0)
        self.charisma += item.get('charisma', 0)
        self.armor += item.get('armor', 0)
        if 'damage' in item:
          if not hasattr(self, 'damage_bonus'):
            self.damage_bonus = 0
          self.damage_bonus += item.get('damage', 0)
        
        if 'mining_bonus' in item:
          if not hasattr(self, 'mining_bonus'):
            self.mining_bonus = 0
          self.mining_bonus += item.get('mining_bonus', 0)
  
  def get_total_damage(self):
    base_damage = self.strength // 2
    weapon_damage = 0
    
    if hasattr(self, 'equipment') and self.equipment.get('weapon'):
      weapon_damage = self.equipment['weapon'].get('damage', 0)
    
    bonus_damage = getattr(self, 'damage_bonus', 0)
    return base_damage + weapon_damage + bonus_damage
    
  def get_total_armor(self):
    return self.armor

  def to_dict(self):
    return {
      'name': self.name,
      'level': self.level,
      'health': self.health,
      'maxHealth': self.max_health,
      'mana': self.mana,
      'maxMana': self.max_mana,
      'experience': self.experience,
      'gold': self.gold,
      'inventory': self.inventory,
      'equippedItems': getattr(self, 'equipment', {}), 
      'stats': {
        'strength': self.strength,
        'dexterity': self.agility,  
        'intelligence': self.intelligence,
        'vitality': self.charisma, 
      },
      'damage': self.get_total_damage(),
      'totalArmor': self.get_total_armor()
    }

  def __repr__(self):
    return f"Player({self.name}, Level: {self.level}, Gold: {self.gold})"