class QuestCompletion:
  def complete_quest(self, quest_id, player):
    quest = self.get_quest_by_id(quest_id)
    if not quest:
      return None
    
    if hasattr(player, 'active_quests') and quest_id in player.active_quests:
      player.active_quests.remove(quest_id)
    if hasattr(player, 'quest_progress'):
      player.quest_progress.pop(quest_id, None)

    quest['completed_by'].append(player.name)
    player.mark_quest_completed(quest_id, quest.get('type'))

    if 'reward_gold' in quest:
      player.gold += quest['reward_gold']
    if 'reward_exp' in quest:
      player.experience += quest['reward_exp']
      player.check_level_up()
    
    return quest

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

  def _auto_complete_step(self, quest_id, quest, step, player):
    try:
      if 'required_items' in step:
        for required_item in step['required_items']:
          if not player.has_item(required_item):
            return None
      if 'consumes_items' in step:
        for item_id in step['consumes_items']:
          player.remove_item(item_id)
      
      step['completed'] = True
      progress = player.quest_progress.get(quest_id, {})
      
      if 'completed_steps' not in progress:
        progress['completed_steps'] = []
      progress['completed_steps'].append(step['action'])
      progress['current_step'] = progress.get('current_step', 0) + 1
      steps = progress.get('steps', [])
      quest_completed = progress['current_step'] >= len(steps)
      
      update = {
        'quest_id': quest_id,
        'quest_title': quest['title'],
        'action': step['action'],
        'step_description': step['description'],
        'step_completed': True,
        'quest_completed': quest_completed,
        'auto_completed': True
      }

      if quest_completed:
        completed_quest = self.complete_quest(quest_id, player)
        if completed_quest:
          update['rewards'] = {
            'gold': completed_quest['reward_gold'],
            'exp': completed_quest['reward_exp']
          }
      
      return update
      
    except Exception as e:
      print(f"Error auto-completing quest step: {str(e)}")
      return None