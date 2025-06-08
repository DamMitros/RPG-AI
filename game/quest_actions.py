class QuestActions:
  def perform_action(self, action, location, player, additional_data=None):
    if not hasattr(player, 'active_quests') or not hasattr(player, 'quest_progress'):
      return [], []

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
            (current_step['location'] == location or location == "any") and not current_step['completed']):

            can_complete = True
            missing_items = []
            
            if 'required_items' in current_step:
              for required_item in current_step['required_items']:
                if not player.has_item(required_item):
                  can_complete = False
                  missing_items.append(required_item)
            
            if can_complete:
              if 'consumes_items' in current_step:
                for item_id in current_step['consumes_items']:
                  player.remove_item(item_id)
              
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
              quest_updates.append({
                'quest_id': quest_id,
                'quest_title': quest['title'],
                'action': action,
                'step_completed': False,
                'error': f"Missing required items: {', '.join(missing_items)}"
              })
      else:
        if action in quest.get('completion_requirements', []):
          if 'requirements_met' not in progress:
            progress['requirements_met'] = []
          if action not in progress['requirements_met']:
            can_complete = True
            missing_items = []
            
            if 'required_items' in quest:
              for required_item in quest['required_items']:
                if not player.has_item(required_item):
                  can_complete = False
                  missing_items.append(required_item)
            
            if can_complete:
              if 'consumes_items' in quest:
                for item_id in quest['consumes_items']:
                  player.remove_item(item_id)
              
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
            else:
              quest_updates.append({
                'quest_id': quest_id,
                'quest_title': quest['title'],
                'action': action,
                'requirement_met': False,
                'error': f"Missing required items: {', '.join(missing_items)}"
              })
    
    return quest_updates
  
  def get_available_actions_for_location(self, location, player):
    available_actions = []
    
    if not hasattr(player, 'active_quests'):
      return available_actions
    
    for quest_id in player.active_quests:
      quest = self.get_quest_by_id(quest_id)
      if not quest:
        continue

      if 'steps' in quest and hasattr(player, 'quest_progress') and quest_id in player.quest_progress:
        progress = player.quest_progress[quest_id]
        current_step_index = progress.get('current_step', 0)
        steps = progress.get('steps', [])
        
        if current_step_index < len(steps):
          current_step = steps[current_step_index]
          step_location = current_step.get('location', '')
          
          if step_location == location and not current_step.get('completed', False):
            action_info = {
              'action': current_step.get('action', ''),
              'description': current_step.get('description', ''),
              'quest_id': quest_id,
              'quest_title': quest['title'],
              'step_index': current_step_index
            }
            available_actions.append(action_info)

      elif 'completion_requirements' in quest:
        quest_location = quest.get('location', '')
        if quest_location == location:
          progress = player.quest_progress.get(quest_id, {})
          requirements_met = progress.get('requirements_met', [])
          
          for requirement in quest['completion_requirements']:
            if requirement not in requirements_met:
              if self._can_perform_action_at_location(requirement, location):
                action_info = {
                  'action': requirement,
                  'description': self.get_requirement_description(requirement),
                  'quest_id': quest_id,
                  'quest_title': quest['title']
                }
                available_actions.append(action_info)
    
    return available_actions
  
  def _can_perform_action_at_location(self, action, location):
    action_location = self.action_locations.get(action)
    
    if action_location == "any":
      return True

    location_mapping = {
      'mainPage': 'mainPage',
      'tavern': 'tavern', 
      'shop': 'shop',
      'smithy': 'smithy',
      'forest': 'forest',
      'mine': 'mine_entrance',  
      'mine_entrance': 'mine_entrance'
    }
    
    mapped_location = location_mapping.get(location, location)
    
    return action_location == mapped_location
  
  def get_quest_actions_for_location(self, player, location):
    available_actions = []
    
    if not hasattr(player, 'active_quests'):
      return available_actions
    
    for quest_id in player.active_quests:
      quest = self.get_quest_by_id(quest_id)
      if not quest:
        continue

      if 'steps' in quest and hasattr(player, 'quest_progress') and quest_id in player.quest_progress:
        progress = player.quest_progress[quest_id]
        current_step_index = progress.get('current_step', 0)
        steps = progress.get('steps', [])
        
        if current_step_index < len(steps):
          current_step = steps[current_step_index]
          step_location = current_step.get('location', '')
          
          if step_location == location and not current_step.get('completed', False):
            action_info = {
              'id': f"{quest_id}_{current_step.get('action', '')}",
              'action': current_step.get('action', ''),
              'description': current_step.get('description', ''),
              'quest_id': quest_id,
              'quest_title': quest['title'],
              'step_index': current_step_index,
              'type': 'quest_step',
              'location': location,
              'available': True
            }
            available_actions.append(action_info)

      elif 'completion_requirements' in quest:
        quest_location = quest.get('location', '')
        if quest_location == location:
          progress = player.quest_progress.get(quest_id, {})
          requirements_met = progress.get('requirements_met', [])
          
          for requirement in quest['completion_requirements']:
            if requirement not in requirements_met:
              if self._can_perform_action_at_location(requirement, location):
                action_info = {
                  'id': f"{quest_id}_{requirement}",
                  'action': requirement,
                  'description': self.get_requirement_description(requirement),
                  'quest_id': quest_id,
                  'quest_title': quest['title'],
                  'type': 'quest_requirement',
                  'location': location,
                  'available': True
                }
                available_actions.append(action_info)
    
    return available_actions

  def auto_perform_location_actions(self, location, player):
    quest_updates = []
    
    if not hasattr(player, 'active_quests'):
      return quest_updates
    
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
          step_location = current_step.get('location', '')

          if (step_location == location and not current_step.get('completed', False)):
            action = current_step.get('action', '')

            if action in ['explore_mine', 'enter_mine', 'visit_location']:
              update = self._auto_complete_step(quest_id, quest, current_step, player)
              if update:
                quest_updates.append(update)
    
    return quest_updates