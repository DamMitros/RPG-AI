import time

class QuestManagement:
  def _meets_requirements(self, quest, player):
    for req in quest["requirements"]:
      if "level >=" in req:
        required_level = int(req.split(">=")[1].strip())
        if player.level < required_level:
          return False
    return True
  
  def get_available_quests(self, player):
    available = []

    for quest_id, quest in self.quests.items():
      if (player.name not in quest["completed_by"] and 
          not player.has_completed_quest(quest_id)):
        if self._meets_requirements(quest, player):
          available.append(quest)

    for quest_id, quest in self.generated_quests_cache.items():
      if (player.name not in quest["completed_by"] and 
          not player.has_completed_quest(quest_id)):
        quest_type = quest.get('type', 'investigation')
        completed_of_type = player.get_completed_quest_count_by_type(quest_type)
        if completed_of_type < 2 and self._meets_requirements(quest, player):
          available.append(quest)
    
    return available
  
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
  
  def abandon_quest(self, quest_id, player):
    if not hasattr(player, 'active_quests') or quest_id not in player.active_quests:
      return False

    player.active_quests.remove(quest_id)

    if hasattr(player, 'quest_progress'):
      player.quest_progress.pop(quest_id, None)
    
    return True
  
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
      'is_active': quest_id in getattr(player, 'active_quests', []),
      'steps': quest.get('steps', [])
    }

    if hasattr(player, 'quest_progress') and quest_id in player.quest_progress:
      progress = player.quest_progress[quest_id]
      quest_detail['current_step'] = progress.get('current_step', 0)
      
      if 'steps' in progress:
        quest_detail['steps'] = progress['steps']
    
    progress_display = self.get_quest_progress_display(quest_id, player)
    if progress_display:
      quest_detail['progress'] = progress_display
    
    return quest_detail

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