class QuestProgress:
  def get_quest_progress_display(self, quest_id, player):
    quest = self.get_quest_by_id(quest_id)
    if not quest:
      return None
    
    if not hasattr(player, 'quest_progress') or quest_id not in player.quest_progress:
      return None
    
    progress = player.quest_progress[quest_id]
    display_info = []
    
    if 'steps' in quest:
      steps = progress.get('steps', [])
      current_step_index = progress.get('current_step', 0)
      
      for i, step_progress in enumerate(steps):
        step_info = {
          'description': step_progress['description'],
          'completed': step_progress['completed'],
          'is_current': i == current_step_index and not step_progress['completed'],
          'missing_items': []
        }

        if not step_progress['completed'] and i == current_step_index:
          if 'required_items' in step_progress:
            for item in step_progress['required_items']:
              if not player.has_item(item):
                step_info['missing_items'].append(item)
        
        display_info.append(step_info)
    
    elif 'completion_requirements' in quest:
      requirements_met = progress.get('requirements_met', [])
      for req in quest['completion_requirements']:
        req_info = {
          'description': self.get_requirement_description(req),
          'completed': req in requirements_met,
          'is_current': req not in requirements_met,
          'missing_items': []
        }

        if req not in requirements_met:
          if 'required_items' in quest:
            for item in quest['required_items']:
              if not player.has_item(item):
                req_info['missing_items'].append(item)
        
        display_info.append(req_info)
    
    return display_info
  
  def get_requirement_description(self, requirement):
    descriptions = {
      'talk_to_erik': 'Talk to Erik at the shop',
      'talk_erik': 'Talk to Erik at the shop', 
      'talk_merchant': 'Talk to the merchant at the shop',
      'buy_materials': 'Purchase required materials',
      'craft_iron_sword': 'Craft an iron sword',
      'mine_ore': 'Mine some ore',
      'explore_forest': 'Explore the forest',
      'hunt_wolf': 'Hunt a wolf',
      'observe_your_surroundings': 'Observe your surroundings carefully',
      'observe_surroundings': 'Observe your surroundings carefully',
      'talk_to_townspeople': 'Talk to the local townspeople',
      'follow_suspicious_trail': 'Follow a suspicious trail',
      'examine_nearby_building': 'Examine nearby buildings for clues',
      'examine_buildings': 'Examine nearby buildings for clues',
      'rest': 'Rest at the tavern',
      'talk_to_local': 'Talk to a local patron',
      'talk_innkeeper': 'Talk to the innkeeper',
      'talk_regular': 'Talk to a regular customer',
     'explore_mine': 'Explore the mine',
      'talk_stranger': 'Talk to a mysterious stranger',
      'help_stranger': 'Help a stranger in need',
      'investigate_rumors': 'Investigate local rumors',
      'question_locals': 'Question local residents',
      'seek_information': 'Seek important information',
      'patrol_area': 'Patrol the area for threats',
      'scout_location': 'Scout the location carefully',
      'investigate_disturbance': 'Investigate reported disturbances',
      'search_for_clues': 'Search for important clues',
      'follow_leads': 'Follow promising leads'
    }
    return descriptions.get(requirement, requirement.replace('_', ' ').title())