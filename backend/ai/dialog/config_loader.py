import yaml

class ConfigLoader:
  def __init__(self):
    pass

  def load_config(self):
    config_files = ["ai/config/config_enhanced.yaml", "ai/config/config.yaml"]
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