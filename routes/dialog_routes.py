from flask import Blueprint, jsonify, request, current_app

dialog_bp = Blueprint('dialog', __name__)

@dialog_bp.route("/dialog", methods=['POST'])
def send_dialog_message():
    dialog_engine = current_app.config['DIALOG_ENGINE']
    data = request.get_json()
    
    session_id = data.get('session_id', 'default')
    message = data.get('message', '')
    context = data.get('context', {})
    response = dialog_engine.process_message(message, session_id, context)
    
    return jsonify({
        'speaker': 'NPC',
        'text': response.get('response', 'Nie rozumiem.'),
        'options': response.get('options', [])
    })

@dialog_bp.route("/conversation_stats")
def conversation_stats():
    dialog_engine = current_app.config['DIALOG_ENGINE']
    stats = dialog_engine.get_conversation_stats()
    return jsonify(stats)

@dialog_bp.route("/quality_report")
def quality_report():
    dialog_engine = current_app.config['DIALOG_ENGINE']
    report = dialog_engine.get_quality_report()
    return jsonify(report)

@dialog_bp.route("/session_stats/<session_id>")
def session_stats(session_id):
    dialog_engine = current_app.config['DIALOG_ENGINE']
    stats = dialog_engine.get_conversation_stats(session_id)
    return jsonify(stats)

@dialog_bp.route("/dialog/<session_id>/history", methods=['GET'])
def get_dialog_history(session_id):
    dialog_engine = current_app.config['DIALOG_ENGINE']
    history = dialog_engine.conversation_history.get(session_id, [])
    messages = []
    for entry in history:
        if isinstance(entry, dict):
            messages.append({
                'speaker': entry.get('speaker', 'Unknown'),
                'text': entry.get('text', ''),
                'timestamp': entry.get('timestamp', None)
            })
        else:
            messages.append({
                'speaker': 'System',
                'text': str(entry),
                'timestamp': None
            })
    
    return jsonify(messages)
