from flask import Blueprint
from .player_routes import player_bp, get_player, update_player, get_inventory, use_item
from .dialog_routes import dialog_bp, send_dialog_message, conversation_stats, quality_report, session_stats, get_dialog_history
from .quest_routes import ( quest_bp, get_available_quests, get_active_quests, generate_quest, refresh_quests, 
        accept_quest, abandon_quest, get_quest_progress, get_quest_actions_for_location, perform_quest_action )
from .shop_routes import shop_bp, get_shop_items, buy_item, sell_item
from .forest_routes import forest_bp
from .mine_routes import mine_bp
from .smithy_routes import smithy_bp, get_smithy_recipes
from .action_routes import action_bp, perform_action

api_bp = Blueprint('api', __name__)

def register_all_routes(app):
    app.register_blueprint(player_bp, url_prefix='/api')
    app.register_blueprint(dialog_bp, url_prefix='/api')
    app.register_blueprint(quest_bp, url_prefix='/api')
    app.register_blueprint(shop_bp, url_prefix='/api')
    app.register_blueprint(forest_bp, url_prefix='/api')
    app.register_blueprint(mine_bp, url_prefix='/api')
    app.register_blueprint(smithy_bp, url_prefix='/api')
    app.register_blueprint(action_bp, url_prefix='/api')

api_bp.add_url_rule("/player", "get_player", get_player, methods=['GET'])
api_bp.add_url_rule("/player", "update_player", update_player, methods=['PUT'])
api_bp.add_url_rule("/inventory", "get_inventory", get_inventory, methods=['GET'])
api_bp.add_url_rule("/inventory/use", "use_item", use_item, methods=['POST'])

api_bp.add_url_rule("/dialog", "send_dialog_message", send_dialog_message, methods=['POST'])
api_bp.add_url_rule("/conversation_stats", "conversation_stats", conversation_stats)
api_bp.add_url_rule("/quality_report", "quality_report", quality_report)
api_bp.add_url_rule("/session_stats/<session_id>", "session_stats", session_stats)
api_bp.add_url_rule("/dialog/<session_id>/history", "get_dialog_history", get_dialog_history, methods=['GET'])

api_bp.add_url_rule("/quests/available", "get_available_quests", get_available_quests, methods=['GET'])
api_bp.add_url_rule("/quests/active", "get_active_quests", get_active_quests, methods=['GET'])
api_bp.add_url_rule("/quests/generate", "generate_quest", generate_quest, methods=['POST'])
api_bp.add_url_rule("/quests/refresh", "refresh_quests", refresh_quests, methods=['POST'])
api_bp.add_url_rule("/quests/<quest_id>/accept", "accept_quest", accept_quest, methods=['POST'])
api_bp.add_url_rule("/quests/<quest_id>/abandon", "abandon_quest", abandon_quest, methods=['POST'])
api_bp.add_url_rule("/quests/<quest_id>/progress", "get_quest_progress", get_quest_progress, methods=['GET'])
api_bp.add_url_rule("/quests/actions/<location>", "get_quest_actions_for_location", get_quest_actions_for_location, methods=['GET'])
api_bp.add_url_rule("/quests/action", "perform_quest_action", perform_quest_action, methods=['POST'])

api_bp.add_url_rule("/shop/items", "get_shop_items", get_shop_items, methods=['GET'])
api_bp.add_url_rule("/merchant/buy", "buy_item", buy_item, methods=['POST'])
api_bp.add_url_rule("/merchant/sell", "sell_item", sell_item, methods=['POST'])
api_bp.add_url_rule("/action", "perform_action", perform_action, methods=['POST'])
api_bp.add_url_rule("/smithy/recipes", "get_smithy_recipes", get_smithy_recipes, methods=['GET'])