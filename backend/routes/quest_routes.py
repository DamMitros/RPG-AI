from flask import Blueprint, jsonify, request, current_app

quest_bp = Blueprint('quest', __name__)

@quest_bp.route("/quests/available", methods=['GET'])
def get_available_quests():
  quest_system = current_app.config['QUEST_SYSTEM']
  player = current_app.config['PLAYER']
  generated_quests = quest_system.get_available_quests(player)
  active_quests = quest_system.get_player_active_quests(player)
  available_quests = []
  for quest in generated_quests:
    available_quests.append({
      'id': quest.get('id', ''),
      'title': quest.get('title', ''),
      'description': quest.get('description', ''),
      'type': quest.get('type', 'delivery'),
      'reward': {
        'gold': quest.get('reward_gold', 0),
        'experience': quest.get('reward_exp', 0),
        'items': quest.get('reward_items', [])
      },
      'requirements': quest.get('requirements', {}),
      'status': 'available'
    })
  
  return jsonify({
    'quests': available_quests,
    'active_quests': [
      {
        'id': quest.get('id', ''),
        'title': quest.get('title', ''),
        'description': quest.get('description', ''),
        'type': quest.get('type', 'delivery'),
        'reward': {
          'gold': quest.get('reward_gold', 0),
          'experience': quest.get('reward_exp', 0),
          'items': quest.get('reward_items', [])
        },
        'requirements': quest.get('requirements', {}),
        'status': 'active',
        'progress': quest.get('progress', {})
      }
      for quest in active_quests
    ]
  })

@quest_bp.route("/quests/active", methods=['GET'])
def get_active_quests():
  quest_system = current_app.config['QUEST_SYSTEM']
  player = current_app.config['PLAYER']
  active_quests = quest_system.get_player_active_quests(player)
  
  formatted_quests = []
  for quest in active_quests:
    objectives = []
    steps = quest.get('steps', [])
    progress = quest.get('progress', [])

    if not steps and progress:
      for i, prog in enumerate(progress):
        objectives.append({
          'id': f"{quest.get('id', '')}-progress-{i}",
          'description': prog.get('description', ''),
          'completed': prog.get('completed', False),
          'is_current': prog.get('is_current', i == quest.get('current_step', 0))
        })
    else:
      for i, step in enumerate(steps):
        objectives.append({
          'id': f"{quest.get('id', '')}-step-{i}",
          'description': step.get('description', step.get('action', '')),
          'completed': step.get('completed', False),
          'is_current': i == quest.get('current_step', 0)
        })
    
    formatted_quests.append({
      'id': quest.get('id', ''),
      'title': quest.get('title', ''),
      'description': quest.get('description', ''),
      'type': quest.get('type', 'delivery'),
      'reward': {
        'gold': quest.get('reward_gold', 0),
        'experience': quest.get('reward_exp', 0),
        'items': quest.get('reward_items', [])
      },
      'requirements': quest.get('requirements', {}),
      'status': 'active',
      'progress': quest.get('progress', {}),
      'current_step': quest.get('current_step', 0),
      'steps': quest.get('steps', []),
      'objectives': objectives
    })
  
  return jsonify({
    'success': True,
    'quests': formatted_quests
  })

@quest_bp.route("/quests/generate", methods=['POST'])
def generate_quest():
  quest_system = current_app.config['QUEST_SYSTEM']
  player = current_app.config['PLAYER']
  data = request.get_json()
  
  quest_type = data.get('type', None)  
  difficulty = data.get('difficulty', None)  
  
  try:
    quest_system = current_app.config['QUEST_SYSTEM']
    new_quest = quest_system.quest_generator.generate_quest(quest_type=quest_type, player_level=player.level)
    
    if new_quest:
      return jsonify({
        'success': True,
        'quest': {
          'id': new_quest.get('id', ''),
          'title': new_quest.get('title', ''),
          'description': new_quest.get('description', ''),
          'type': new_quest.get('type', 'delivery'),
          'reward': {
            'gold': new_quest.get('reward_gold', 0),
            'experience': new_quest.get('reward_exp', 0),
            'items': new_quest.get('reward_items', [])
          },
          'requirements': new_quest.get('requirements', {}),
          'status': 'available',
          'steps': new_quest.get('steps', [])
        }
      })
    else:
      return jsonify({
        'success': False,
        'message': 'Failed to generate quest'
      })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'Error generating quest: {str(e)}'
    })

@quest_bp.route("/quests/refresh", methods=['POST'])
def refresh_quests():
  quest_system = current_app.config['QUEST_SYSTEM']
  player = current_app.config['PLAYER']
  
  try:
    new_quest_count = quest_system.manual_refresh_quests(player.level)
    available_quests = quest_system.get_available_quests(player)
    active_quests = quest_system.get_player_active_quests(player)
    
    formatted_available = []
    for quest in available_quests:
      formatted_available.append({
        'id': quest.get('id', ''),
        'title': quest.get('title', ''),
        'description': quest.get('description', ''),
        'type': quest.get('type', 'delivery'),
        'reward': {
          'gold': quest.get('reward_gold', 0),
          'experience': quest.get('reward_exp', 0),
          'items': quest.get('reward_items', [])
        },
        'requirements': quest.get('requirements', {}),
        'status': 'available'
      })
    
    return jsonify({
      'success': True,
      'message': f'Generated {new_quest_count} new quests',
      'quests': formatted_available,
      'active_quests': [
        {
          'id': quest.get('id', ''),
          'title': quest.get('title', ''),
          'description': quest.get('description', ''),
          'type': quest.get('type', 'delivery'),
          'reward': {
            'gold': quest.get('reward_gold', 0),
            'experience': quest.get('reward_exp', 0),
            'items': quest.get('reward_items', [])
          },
          'requirements': quest.get('requirements', {}),
          'status': 'active',
          'progress': quest.get('progress', {})
        }
        for quest in active_quests
      ]
    })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'Error refreshing quests: {str(e)}'
    })

@quest_bp.route("/quests/<quest_id>/accept", methods=['POST'])
def accept_quest(quest_id):
  quest_system = current_app.config['QUEST_SYSTEM']
  player = current_app.config['PLAYER']
  
  try:
    success = quest_system.accept_quest(quest_id, player)
    if success:
      active_quests = quest_system.get_player_active_quests(player)
      accepted_quest = next((q for q in active_quests if q.get('id') == quest_id), None)
      
      if accepted_quest:
        objectives = []
        steps = accepted_quest.get('steps', [])
        for i, step in enumerate(steps):
          objectives.append({
            'id': f"{accepted_quest.get('id', '')}-step-{i}",
            'description': step.get('description', step.get('action', '')),
            'completed': step.get('completed', False),
            'is_current': i == accepted_quest.get('current_step', 0)
          })
        
        return jsonify({
          'success': True,
          'message': 'Quest accepted successfully',
          'id': accepted_quest.get('id', ''),
          'title': accepted_quest.get('title', ''),
          'description': accepted_quest.get('description', ''),
          'type': accepted_quest.get('type', 'delivery'),
          'reward': {
            'gold': accepted_quest.get('reward_gold', 0),
            'experience': accepted_quest.get('reward_exp', 0),
            'items': accepted_quest.get('reward_items', [])
          },
          'requirements': accepted_quest.get('requirements', {}),
          'status': 'active',
          'progress': accepted_quest.get('progress', {}),
          'current_step': accepted_quest.get('current_step', 0),
          'steps': accepted_quest.get('steps', []),
          'objectives': objectives
        })
      else:
        return jsonify({
          'success': False,
          'message': 'Quest accepted but could not retrieve details'
        })
    else:
      return jsonify({
        'success': False,
        'message': 'Failed to accept quest'
      })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'Error accepting quest: {str(e)}'
    })

@quest_bp.route("/quests/<quest_id>/abandon", methods=['POST'])
def abandon_quest(quest_id):
  quest_system = current_app.config['QUEST_SYSTEM']
  player = current_app.config['PLAYER']
  
  try:
    success = quest_system.abandon_quest(quest_id, player)
    if success:
      return jsonify({
        'success': True,
        'message': 'Quest abandoned successfully'
      })
    else:
      return jsonify({
        'success': False,
        'message': 'Failed to abandon quest'
      })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'Error abandoning quest: {str(e)}'
    })

@quest_bp.route("/quests/<quest_id>/progress", methods=['GET'])
def get_quest_progress(quest_id):
  quest_system = current_app.config['QUEST_SYSTEM']
  player = current_app.config['PLAYER']
  
  try:
    quest = quest_system.get_quest_by_id(player, quest_id)
    if quest:
      return jsonify({
        'success': True,
        'quest': {
          'id': quest.get('id', ''),
          'title': quest.get('title', ''),
          'progress': quest.get('progress', {}),
          'current_step': quest.get('current_step', 0),
          'steps': quest.get('steps', []),
          'status': quest.get('status', 'active')
        }
      })
    else:
      return jsonify({
        'success': False,
        'message': 'Quest not found'
      })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'Error getting quest progress: {str(e)}'
    })

@quest_bp.route("/quests/actions/<location>", methods=['GET'])
def get_quest_actions_for_location(location):
  quest_system = current_app.config['QUEST_SYSTEM']
  player = current_app.config['PLAYER']
  
  try:
    quest_actions = quest_system.get_quest_actions_for_location(player, location)
    
    formatted_actions = []
    for action in quest_actions:
      formatted_actions.append({
        'id': action.get('id', ''),
        'action': action.get('action', ''),
        'description': action.get('description', ''),
        'quest_id': action.get('quest_id', ''),
        'quest_title': action.get('quest_title', ''),
        'type': action.get('type', 'quest'),
        'location': location,
        'step_index': action.get('step_index'),
        'available': action.get('available', True)
      })
    
    return jsonify({
      'success': True,
      'actions': formatted_actions
    })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'Error getting quest actions: {str(e)}',
      'actions': []
    })

@quest_bp.route("/quests/action", methods=['POST'])
def perform_quest_action():
  quest_system = current_app.config['QUEST_SYSTEM']
  player = current_app.config['PLAYER']
  data = request.get_json()
  
  action = data.get('action', '')
  location = data.get('location', '')
  quest_id = data.get('quest_id', '')
  
  try:
    quest_updates = quest_system.perform_action(action, location, player)
    
    if quest_updates:
      quest_update = next((update for update in quest_updates if update.get('quest_id') == quest_id), None)
      
      if quest_update:
        message = quest_update.get('step_description', quest_update.get('action', ''))
        if quest_update.get('quest_completed'):
          message += f" - Quest completed! Rewards: {quest_update.get('rewards', {})}"
        elif quest_update.get('error'):
          message = quest_update.get('error')
        
        return jsonify({
          'success': True,
          'message': message,
          'quest_completed': quest_update.get('quest_completed', False),
          'rewards': quest_update.get('rewards', {}),
          'player': player.to_dict()
        })
      else:
        any_update = quest_updates[0] if quest_updates else None
        if any_update and any_update.get('step_description'):
          return jsonify({
            'success': True,
            'message': any_update.get('step_description'),
            'quest_completed': any_update.get('quest_completed', False),
            'rewards': any_update.get('rewards', {}),
            'player': player.to_dict()
          })
    
    return jsonify({
      'success': True,
      'message': 'No quest progress made with this action',
      'player': player.to_dict()
    })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'Error performing quest action: {str(e)}'
    })

@quest_bp.route("/quests/debug/completed", methods=['GET'])
def debug_completed_quests():
  player = current_app.config['PLAYER']

  if not hasattr(player, 'completed_quest_ids'):
    player.completed_quest_ids = set()
  if not hasattr(player, 'completed_quest_types'):
    player.completed_quest_types = {}
  
  return jsonify({
    'success': True,
    'completed_quest_ids': list(player.completed_quest_ids),
    'completed_quest_types': player.completed_quest_types,
    'total_completed': len(player.completed_quest_ids)
  })

@quest_bp.route("/quests/debug/reset_completed", methods=['POST'])
def debug_reset_completed():
  player = current_app.config['PLAYER']
  player.completed_quest_ids = set()
  player.completed_quest_types = {}
  
  return jsonify({
    'success': True,
    'message': 'Completed quest tracking has been reset'
  })

@quest_bp.route("/quests/debug/force_regenerate", methods=['POST'])
def debug_force_regenerate():
  quest_system = current_app.config['QUEST_SYSTEM']
  player = current_app.config['PLAYER']

  quest_system.generated_quests_cache = {}
  quest_system.last_quest_generation = 0
  quest_system.refresh_generated_quests(player.level, force=True)
  quest_system.maintain_quest_pool(player.level)
  
  return jsonify({
    'success': True,
    'message': f'Quest pool regenerated with {len(quest_system.generated_quests_cache)} quests',
    'quest_count': len(quest_system.generated_quests_cache)
  })

@quest_bp.route("/quests/pool/status", methods=['GET'])
def get_quest_pool_status():
  quest_system = current_app.config['QUEST_SYSTEM']
  player = current_app.config['PLAYER']
  
  try:
    status = quest_system.check_quest_pool_health(player.level)
    available_quests = quest_system.get_available_quests(player)
    
    return jsonify({
      'success': True,
      'pool_status': status,
      'available_quest_count': len(available_quests),
      'can_refresh': True
    })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'Error checking quest pool: {str(e)}'
    })
