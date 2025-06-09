import torch, time, re, yaml, random
from transformers import AutoModelForCausalLM, AutoTokenizer
from ai.dialog.tracker import ConversationTracker
from ai.dialog.config_loader import ConfigLoader
from ai.dialog.engine_utils import (
  clean_response, build_conversation_prompt, extract_character_response,
  responses_too_similar, extract_alternative_response
)

class DialogEngine:
  def __init__(self):
    torch.set_float32_matmul_precision('high')
    self.model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    self.device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {self.device}")
    
    self.conversation_tracker = ConversationTracker()
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

    if torch.__version__ >= "2.0" and self.device == "cuda":
      self.model = torch.compile(self.model)

    self.conversation_history = {}
    self.config_loader = ConfigLoader() 
    self.load_config()

  def load_config(self):
    config = self.config_loader.load_config()
    self.characters = config.get("characters", {})
    self.locations = config.get("locations", {})
    self.rules = config.get("rules", [])
    self.world_lore = config.get("world_lore", {})
    self.quest_hooks = config.get("quest_hooks", [])

  def reset_conversation(self, session_id="default", character=None):
    if character:
      key = f"{session_id}_{character}"
      self.conversation_history[key] = []
    else:
      keys_to_reset = [k for k in self.conversation_history.keys() if k.startswith(f"{session_id}_")]
      for key in keys_to_reset:
        self.conversation_history[key] = []

  def get_npc_response(self, user_input, character="tavern_keeper", session_id="default", player_stats=None):
    start_time = time.time()
    history_key = f"{session_id}_{character}"
    if history_key not in self.conversation_history:
      self.conversation_history[history_key] = []

    prompt = build_conversation_prompt(
      user_input, character, session_id, player_stats,
      self.characters, self.world_lore, self.conversation_history
    )
    
    if prompt.startswith("DIRECT_RESPONSE:"):
      response = prompt[15:] 
      self.conversation_tracker.log_interaction(
        user_input=user_input,
        bot_response=response,
        character=character,
        session_id=session_id,
        player_stats=player_stats
      )
      return response
      
    if "Character not found" in prompt:
      return prompt

    try:
      inputs = self.tokenizer(
        prompt,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
      ).to(self.model.device)

      with torch.no_grad():
        output = self.model.generate(
          **inputs,
          max_new_tokens=80,      # ograniczenie długości odpowiedzi
          temperature=0.7,        # kreatywność/losowość odpowiedzi
          top_k=40,              # top-k najbardziej prawdopodobnych tokenów
          top_p=0.85,            # suma prawdopodobieństw tokenów
          repetition_penalty=1.2, # kara za powtarzanie się
          do_sample=True,
          no_repeat_ngram_size=3,
          pad_token_id=self.tokenizer.eos_token_id,
          eos_token_id=self.tokenizer.eos_token_id,
          use_cache=True,
          early_stopping=False 
        )

      full_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
      
      print(f"[DEBUG] Generated full text: {full_text}")

      input_text = self.tokenizer.decode(inputs.input_ids[0], skip_special_tokens=True)
      if full_text.startswith(input_text):
        generated_only = full_text[len(input_text):].strip()
        print(f"[DEBUG] Generated content only: '{generated_only}'")
        if generated_only.strip():
          character_name = self.characters[character]['name']
          response = extract_character_response(generated_only, character_name, character)
        else:
          character_name = self.characters[character]['name']
          response = extract_character_response(full_text, character_name, character)
      else:
        character_name = self.characters[character]['name']
        response = extract_character_response(full_text, character_name, character)
      history_key = f"{session_id}_{character}"
      recent_responses = [turn['npc'] for turn in self.conversation_history.get(history_key, [])[-5:]]
      
      if response and any(responses_too_similar(response, prev_resp) for prev_resp in recent_responses):
        print(f"[DEBUG] Detected repetitive response: '{response}', trying alternative extraction")
        alternative_response = extract_alternative_response(full_text, character_name, response)
        if alternative_response and not any(responses_too_similar(alternative_response, prev_resp) for prev_resp in recent_responses):
          response = alternative_response
          print(f"[DEBUG] Found alternative response: '{response}'")
        else:
          print(f"[DEBUG] Could not find alternative, will use fallback")
          response = None

      if response and len(response) > 150:
        match = re.search(r'^[^.!?]*[.!?]', response)
        if match:
          response = match.group(0).strip()

      if not response or len(response.strip()) < 5:
        print(f"[DEBUG] Response seems corrupted: '{response}', using fallback")

        history_key = f"{session_id}_{character}"
        recent_responses = [turn['npc'] for turn in self.conversation_history.get(history_key, [])[-3:]]
        character_fallback_pools = {
          "blacksmith": [
            "Aye, what brings ye to me forge? The steel grows cold while we speak...",
            "Need something forged, stranger? I work with honest steel and fire.",
            "Ye want a blade that sings, or one that survives?",
            "The forge is hot today... what would ye have me craft?",
            "Dammit, another interruption... what ye need, stranger?"
          ],
          "tavern_keeper": [
            "Welcome to the Tawny Lion, friend! What news from the roads?",
            "What can I get for ye today, friend? Ale's fresh and the stew's hot.",
            "Dammit all, another stranger... what brings ye to our troubled village?",
            "Back in my day, travelers brought better stories...",
            "I heard that... no, ye tell me first - what news do ye bring?"
          ],
          "mysterious_stranger": [
            "Indeed... the shadows whisper of strange happenings...",
            "The depths below... hold many secrets...",
            "Time reveals all truths... if ye dare to listen...",
            "I am nobody... just another wanderer in these dark times...",
            "The mine... it remembers what was buried there..."
          ],
          "merchant": [
            "Good day, traveler! Perhaps ye seek wares from distant lands?",
            "I've got a special offer for you... straight from the city!",
            "The price? Well, for you... I might consider a fair deal.",
            "These goods won't last long... what catches your eye?",
            "Trade has been... difficult lately. What do ye need?"
          ],
          "tavern_regular": [
            "Well now, another stranger... what brings ye to our troubled village?",
            "Let me tell you what I heard... but first, what news do ye bring?",
            "Back in my day, this place was different... much different.",
            "Another face I don't recognize... these are strange times indeed.",
            "Ye look like ye've traveled far... what tales do ye carry?"
          ]
        }
        
        fallback_pool = character_fallback_pools.get(character, [
          "Aye, what would ye have of me, stranger?",
          "What brings ye to these troubled lands?",
          "Speak, traveler... what do ye seek?",
          "I've little time for idle chatter... what ye need?",
          "These are dark times... what would ye know?"
        ])
        
        available_fallbacks = [f for f in fallback_pool if f not in recent_responses]
        if not available_fallbacks:
          available_fallbacks = fallback_pool  
        
        response = available_fallbacks[0]  
      
      if response and (len(response.split()) <= 1 or 
                     any(bad in response.lower() for bad in ['charlie', 'irish', 'biker', 'grunting'])):
        print(f"[DEBUG] Response seems corrupted: '{response}', using fallback")
        character_fallbacks = {
          "blacksmith": "Aye, I am Anja Ironbite. What brings ye to me forge?",
          "tavern_keeper": "I'm Bartek, keeper of this tavern. What can I do for ye?",
          "mysterious_stranger": "Names... are for those who trust easily...",
          "merchant": "Good day! I'm Erik, merchant of fine goods. How may I serve ye?",
          "tavern_regular": "I'm just an old villager... but what brings ye here, stranger?"
        }
        response = character_fallbacks.get(character, "Aye, what would ye have of me, stranger?")
      
      print(f"[DEBUG] Extracted response: '{response}'")
      if response and not response.endswith(('.', '!', '?', '...')):
        if len(response.split()) > 3:
          response += "."
        else:
          response += "..."

      response = clean_response(response, character, self.characters)
      conversation_data = {
        'user': user_input,
        'npc': response,
        'character': character,
        'session_id': session_id,
        'player_stats': player_stats,
        'response_time': time.time() - start_time
      }

      self.conversation_history[history_key].append({
        'user': user_input,
        'npc': response
      })

      self.conversation_tracker.log_interaction(
        user_input=user_input,
        bot_response=response,
        character=character,
        session_id=session_id,
        player_stats=player_stats
      )

      print(f"Response time: {time.time() - start_time:.2f} seconds")
      return response

    except Exception as e:
      error_response = f"(Model error: {str(e)})"
      self.conversation_tracker.log_interaction(
        user_input=user_input,
        bot_response=error_response,
        character=character,
        session_id=session_id,
        player_stats=player_stats,
        error=str(e)
      )
      return error_response

  def get_conversation_stats(self, session_id=None):
    return self.conversation_tracker.get_conversation_stats(session_id)
  
  def get_quality_report(self, session_id=None):
    return self.conversation_tracker.generate_quality_report(session_id)
  
  def process_message(self, message, session_id="default", context=None):
    character = context.get('character', 'tavern_keeper') if context else 'tavern_keeper'
    player_stats = context.get('player_stats') if context else None
    
    response_text = self.get_npc_response(
      user_input=message,
      character=character,
      session_id=session_id,
      player_stats=player_stats
    )
    
    return {
      'response': response_text,
      'character': character,
      'session_id': session_id,
      'options': []  
    }
  
  def set_generation_params(self, **params):
    self.generation_params = {
      'temperature': params.get('temperature', 0.7),
      'top_k': params.get('top_k', 25),
      'top_p': params.get('top_p', 0.85),
      'repetition_penalty': params.get('repetition_penalty', 1.2),
      'max_new_tokens': params.get('max_new_tokens', 80)
    }
  
  def get_generation_params(self):
    return getattr(self, 'generation_params', {
      'temperature': 0.7,
      'top_k': 25,
      'top_p': 0.85,
      'repetition_penalty': 1.2,
      'max_new_tokens': 80 
    })