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

  def __repr__(self):
    return f"Player({self.name}, Level: {self.level}, Gold: {self.gold})"