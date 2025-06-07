"""
Routes package for the RPG-AI application.

This package contains modular route definitions split across multiple files:
- player_routes.py: Player management and inventory routes
- dialog_routes.py: Dialog and conversation routes  
- quest_routes.py: Quest system routes
- shop_routes.py: Shop and merchant routes
- forest_routes.py: Forest location action routes
- mine_routes.py: Mine location action routes
- smithy_routes.py: Smithy crafting routes
- action_routes.py: General action handling routes
- api_routes.py: Main API blueprint that combines all routes
"""

from .api_routes import api_bp

__all__ = ['api_bp']
