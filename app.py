from flask import Flask
from flask_cors import CORS
from game.player import Player
from game.quest_system import QuestSystem
from game.crafting_system import CraftingSystem
from ai.dialog.engine import DialogEngine
import json

from routes.main_routes import main_bp
from routes.location_routes import location_bp
from routes.merchant_routes import merchant_bp
from routes.inventory_routes import inventory_bp
from routes.quest_routes import quest_bp
from routes.api_routes import api_bp

def create_app():
  app = Flask(__name__)
  CORS(app)  
  app.secret_key = 'your_secret_key'

  dialog_engine = DialogEngine()
  quest_system = QuestSystem(dialog_engine)
  crafting_system = CraftingSystem()
  player = Player(name="Demo")
    
  try:
    with open('merchant_inventory.json', 'r') as f:
      merchant_inventory_data = json.load(f)
  except FileNotFoundError:
    merchant_inventory_data = []

  app.config['PLAYER'] = player
  app.config['DIALOG_ENGINE'] = dialog_engine
  app.config['QUEST_SYSTEM'] = quest_system
  app.config['CRAFTING_SYSTEM'] = crafting_system
  app.config['MERCHANT_INVENTORY'] = merchant_inventory_data
    
  app.register_blueprint(main_bp)
  app.register_blueprint(location_bp, url_prefix='/location')
  app.register_blueprint(merchant_bp, url_prefix='/merchant')
  app.register_blueprint(inventory_bp, url_prefix='/inventory')
  app.register_blueprint(quest_bp, url_prefix='/quest')
  app.register_blueprint(api_bp, url_prefix='/api')
    
  return app

if __name__ == "__main__":
  app = create_app()
  app.run(debug=True)