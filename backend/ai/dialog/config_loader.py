import yaml, os

class ConfigLoader:
  def __init__(self):
    pass

  def load_config(self):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    
    config_files = [
      os.path.join(backend_dir, "ai/config/config_enhanced.yaml"),
      os.path.join(backend_dir, "ai/config/config.yaml")
    ]
    config = {}
    
    for config_file in config_files:
      try:
        with open(config_file, "r", encoding='utf-8') as f:
          config = yaml.safe_load(f)
          print(f"[Config] Loaded: {config_file}")
          return config 
      except FileNotFoundError:
        continue
    
    print("[Config load error] No config file found. Using empty configuration.")
    return {
      "characters": {},
      "locations": {},
      "rules": [],
      "world_lore": {},
      "quest_hooks": []
    }