import torch, json, random, time, re
from transformers import AutoModelForCausalLM, AutoTokenizer

class QuestGenerator:
  def __init__(self, dialog_engine=None):
    if dialog_engine:
      self.model = dialog_engine.model
      self.tokenizer = dialog_engine.tokenizer
      self.device = dialog_engine.device
      self.characters = dialog_engine.characters
      self.world_lore = dialog_engine.world_lore
    else:
      self.model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
      self.device = "cuda" if torch.cuda.is_available() else "cpu"
      
      self.tokenizer = AutoTokenizer.from_pretrained(
        self.model_name,
        local_files_only=True,
        trust_remote_code=True
      )
      if self.tokenizer.pad_token is None:
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
      self.model = AutoModelForCausalLM.from_pretrained(
        self.model_name,
        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
        trust_remote_code=True,
        device_map=self.device,
        local_files_only=True
      )
      
      self.characters = {}
      self.world_lore = {}

    self.quest_types = {
      "investigation": {
        "urgency": ["urgent", "standard", "low"],
        "difficulty": ["easy", "medium", "hard"],
        "keywords": ["investigate", "find", "discover", "uncover", "solve"]
      },
      "delivery": {
        "urgency": ["urgent", "standard"],
        "difficulty": ["easy", "medium"],
        "keywords": ["deliver", "transport", "carry", "bring"]
      },
      "combat": {
        "urgency": ["urgent", "standard"],
        "difficulty": ["medium", "hard", "extreme"],
        "keywords": ["eliminate", "clear", "fight", "defeat", "protect"]
      },
      "gathering": {
        "urgency": ["standard", "low"],
        "difficulty": ["easy", "medium"],
        "keywords": ["collect", "gather", "harvest", "find"]
      },
      "rescue": {
        "urgency": ["urgent"],
        "difficulty": ["medium", "hard"],
        "keywords": ["rescue", "save", "help", "find"]
      }
    }
    
    self.generated_quests = {}
    
  def generate_quest(self, quest_type=None, player_level=1, world_context=None):
    if not quest_type:
      quest_type = random.choice(list(self.quest_types.keys()))
    
    world_info = ""
    if hasattr(self, 'world_lore') and self.world_lore:
      world_info = f"World: {self.world_lore.get('village_name', 'Stonehaven')}\n"
      world_info += f"Background: {self.world_lore.get('background', '')}\n"
      
      if 'current_events' in self.world_lore:
        world_info += "Current events:\n"
        for event in self.world_lore['current_events'][:3]:  
          world_info += f"- {event}\n"

    difficulty = "easy" if player_level <= 2 else "medium" if player_level <= 5 else "hard"
    urgency = random.choice(self.quest_types[quest_type]["urgency"])
    prompt = f"""{world_info}

Generate a {quest_type} quest for a level {player_level} player.
Quest type: {quest_type}
Difficulty: {difficulty}
Urgency: {urgency}

The quest should be a medieval fantasy quest posted on a village notice board.
Format the response as a notice board posting with:
- Title (one line, all caps)
- Description (2-3 sentences)
- Contact person
- Reward amount in gold (10-100 based on difficulty)

Example format:
TITLE: MISSING MERCHANT'S DAUGHTER
Description: A merchant's daughter has vanished while traveling to the next village. Last seen near the old forest road three days ago. Her father fears bandits or worse creatures.
Contact: Marcus the Merchant at the marketplace
Reward: 75 gold pieces

Generate quest:
Title:"""

    try:
      inputs = self.tokenizer(
        prompt,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=400
      ).to(self.device)
      
      with torch.no_grad():
        output = self.model.generate(
          **inputs,
          max_new_tokens=150,
          temperature=0.8,
          top_k=50,
          top_p=0.9,
          do_sample=True,
          repetition_penalty=1.5,
          pad_token_id=self.tokenizer.eos_token_id,
          eos_token_id=self.tokenizer.eos_token_id
        )
      
      full_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
      quest_text = full_text.split("Generate quest:")[-1].strip()
      quest = self.parse_generated_quest(quest_text, quest_type, difficulty, player_level)
      
      if quest:
        quest_id = f"ai_quest_{int(time.time())}_{random.randint(100, 999)}"
        quest["id"] = quest_id
        
        quest["steps"] = self.generate_quest_steps(quest_type, difficulty)
        
        self.generated_quests[quest_id] = quest
        quest["id"] = quest_id
        self.generated_quests[quest_id] = quest
        return quest
      else:
        return self.generate_template_quest(quest_type, player_level)
        
    except Exception as e:
      print(f"Quest generation error: {e}")
      return self.generate_template_quest(quest_type, player_level)

  def parse_generated_quest(self, quest_text, quest_type, difficulty, player_level):
    try:
      lines = quest_text.strip().split('\n')

      title = ""
      description = ""
      contact = ""
      reward = 0
      
      for i, line in enumerate(lines):
        line = line.strip()
        if not line:
          continue
          
        if line.upper().startswith("TITLE:") or (i == 0 and not any(x in line.lower() for x in ["description", "contact", "reward"])):
          title = line.replace("TITLE:", "").replace("Title:", "").strip()
        elif line.lower().startswith("description:"):
          description = line.replace("Description:", "").replace("description:", "").strip()
          for j in range(i+1, len(lines)):
            if lines[j].strip() and not any(x in lines[j].lower() for x in ["contact", "reward"]):
              description += " " + lines[j].strip()
            else:
              break
        elif line.lower().startswith("contact:"):
          contact = line.replace("Contact:", "").replace("contact:", "").strip()
        elif line.lower().startswith("reward:"):
          reward_text = line.replace("Reward:", "").replace("reward:", "").strip()
          
          numbers = re.findall(r'\d+', reward_text)
          if numbers:
            reward = int(numbers[0])

      if not title and not description:
        for line in lines:
          if line.isupper() and len(line) > 5:
            title = line
            break

        remaining_lines = [l for l in lines if l != title and l.strip()]
        if remaining_lines:
          description = " ".join(remaining_lines[:3]) 

      if not title:
        title = f"MYSTERIOUS {quest_type.upper()} QUEST"
      if not description:
        description = f"A {quest_type} quest has appeared. Brave adventurers needed."
      if not contact:
        contact = "Village notice board"
      if reward == 0:
        reward = 20 + (player_level * 10) + (25 if difficulty == "hard" else 15 if difficulty == "medium" else 0)
      
      exp_reward = reward * 2

      completion_requirements = self.get_completion_requirements(quest_type)
      
      quest = {
        "title": title,
        "description": description,
        "contact": contact,
        "reward_gold": reward,
        "reward_exp": exp_reward,
        "type": quest_type,
        "difficulty": difficulty,
        "requirements": [f"level >= {max(1, player_level-1)}"],
        "completion_requirements": completion_requirements,
        "completed_by": [],
        "generated": True,
        "generated_at": time.time(),
        "steps": self.generate_quest_steps(quest_type, difficulty)
      }
      
      return quest
      
    except Exception as e:
      print(f"Quest parsing error: {e}")
      return None

  def get_completion_requirements(self, quest_type):
    requirements_map = {
      "investigation": [
        "observe_your_surroundings", "talk_to_townspeople", "investigate_rumors", "seek_information"
      ],
      "delivery": [
        "talk", "talk_innkeeper", "observe_your_surroundings", "help_stranger"
      ],
      "combat": [
        "follow_a_suspicious_trail", "hunt_creatures", "explore_forest", "rest"
      ],
      "gathering": [
        "talk_to_townspeople", "gather_materials", "shallow_mining", "search_treasure"
      ],
      "rescue": [
        "talk_innkeeper", "shallow_mining", "follow_a_suspicious_trail", "talk_mysterious_stranger"
      ]
    }

    base_requirements = requirements_map.get(quest_type, ["observe_your_surroundings", "talk_to_townspeople"])
    return base_requirements[:2]

  def generate_quest_steps(self, quest_type, difficulty):
    steps_templates = {
      "investigation": [
        {"action": "observe_your_surroundings", "location": "mainPage", "description": "Observe your surroundings for clues"},
        {"action": "talk_to_townspeople", "location": "mainPage", "description": "Talk to townspeople to gather information"},
        {"action": "investigate_rumors", "location": "any", "description": "Investigate local rumors to uncover hidden truths"},
        {"action": "examine_nearby_building", "location": "mainPage", "description": "Examine nearby buildings for evidence"},
        {"action": "talk_innkeeper", "location": "tavern", "description": "Question the tavern keeper about recent events"},
        {"action": "seek_information", "location": "any", "description": "Seek out information from anyone suspicious"}
      ],
      "delivery": [
        {"action": "talk", "location": "shop", "description": "Collect the package from the merchant"},
        {"action": "talk_innkeeper", "location": "tavern", "description": "Deliver the package to the tavern keeper"},
        {"action": "observe_your_surroundings", "location": "mainPage", "description": "Check the area to ensure it's safe for travel"},
        {"action": "talk_to_townspeople", "location": "mainPage", "description": "Ask townspeople for shortcuts or danger zones"},
        {"action": "help_stranger", "location": "any", "description": "Assist a stranger along your delivery route"}
      ],
      "combat": [
        {"action": "follow_a_suspicious_trail", "location": "mainPage", "description": "Follow suspicious tracks to find threats"},
        {"action": "explore_forest", "location": "forest", "description": "Explore the forest depths to locate enemies"},
        {"action": "hunt_creatures", "location": "forest", "description": "Hunt and eliminate hostile creatures"},
        {"action": "talk_to_townspeople", "location": "mainPage", "description": "Ask the locals about the threat's origin"},
        {"action": "rest", "location": "tavern", "description": "Rest and recover before the next battle"}
      ],
      "gathering": [
        {"action": "talk_to_townspeople", "location": "mainPage", "description": "Ask locals where to find required materials"},
        {"action": "gather_materials", "location": "forest", "description": "Gather materials in the forest"},
        {"action": "search_treasure", "location": "forest", "description": "Search for rare treasures in the woods"},
        {"action": "shallow_mining", "location": "mine", "description": "Mine the upper levels for useful items"},
        {"action": "talk", "location": "shop", "description": "Return collected materials to the merchant"},
        {"action": "investigate_rumors", "location": "any", "description": "Look into whispers about hidden resources"}
      ],
      "rescue": [
        {"action": "talk_innkeeper", "location": "tavern", "description": "Ask the tavern keeper for information about the missing person"},
        {"action": "talk_regular", "location": "tavern", "description": "Question tavern patrons for leads"},
        {"action": "follow_a_suspicious_trail", "location": "mainPage", "description": "Follow tracks leading out of town"},
        {"action": "shallow_mining", "location": "mine", "description": "Search the mine entrance for clues"},
        {"action": "abandoned_exploration", "location": "mine", "description": "Explore abandoned mine areas to find the missing person"},
        {"action": "talk_mysterious_stranger", "location": "mine", "description": "Speak with a suspicious stranger hiding in the mine"},
        {"action": "help_stranger", "location": "any", "description": "Help someone in need during the search"}
      ]
    }

    
    base_steps = steps_templates.get(quest_type, [
      {"action": "observe_your_surroundings", "location": "mainPage", "description": "Complete the quest objective"}
    ])

    if difficulty == "easy":
      steps = base_steps[:1]  
    elif difficulty == "medium":
      steps = base_steps[:2]  
    else:  
      steps = base_steps  
    
    for step in steps:
      step["completed"] = False
    
    return steps

  def generate_template_quest(self, quest_type, player_level):
    templates = {
      "investigation": {
        "title": "INVESTIGATE MYSTERIOUS OCCURRENCES",
        "description": "Strange events have been reported in the area. Someone needs to investigate what's causing these disturbances.",
        "contact": "Village elder"
      },
      "delivery": {
        "title": "URGENT DELIVERY NEEDED", 
        "description": "An important package needs to be delivered quickly. The path may be dangerous.",
        "contact": "Local merchant"
      },
      "combat": {
        "title": "CLEAR DANGEROUS CREATURES",
        "description": "Hostile creatures are threatening the village. Experienced fighters needed to eliminate the threat.",
        "contact": "Village guard"
      },
      "gathering": {
        "title": "COLLECT RARE MATERIALS",
        "description": "Rare materials are needed for important village business. Knowledge of the area helpful.",
        "contact": "Village craftsman"
      },
      "rescue": {
        "title": "RESCUE MISSING PERSON",
        "description": "Someone has gone missing and needs to be found quickly. Time is of the essence.",
        "contact": "Worried family member"
      }
    }
    
    template = templates.get(quest_type, templates["investigation"])
    
    quest_id = f"template_{quest_type}_{int(time.time())}"
    reward = 25 + (player_level * 5)
    
    quest = {
      "id": quest_id,
      "title": template["title"],
      "description": template["description"],
      "contact": template["contact"],
      "reward_gold": reward,
      "reward_exp": reward * 2,
      "type": quest_type,
      "difficulty": "medium",
      "requirements": [f"level >= {max(1, player_level-1)}"],
      "completion_requirements": self.get_completion_requirements(quest_type),
      "completed_by": [],
      "generated": True,
      "generated_at": time.time(),
      "steps": self.generate_quest_steps(quest_type, "medium")
    }
    
    self.generated_quests[quest_id] = quest
    return quest

  def get_all_available_quests(self, player_level=1, max_quests=5):
    quests = []
    quest_types = list(self.quest_types.keys())
    
    for i in range(max_quests):
      quest_type = random.choice(quest_types)
      quest = self.generate_quest(quest_type, player_level)
      if quest:
        quests.append(quest)
    
    return quests

  def clean_old_quests(self):
    current_time = time.time()
    old_quest_ids = []
    
    for quest_id, quest in self.generated_quests.items():
      if current_time - quest.get("generated_at", 0) > 86400:
        old_quest_ids.append(quest_id)
    
    for quest_id in old_quest_ids:
      del self.generated_quests[quest_id]
    
    print(f"Cleaned {len(old_quest_ids)} old quests")
