import torch, time, re, yaml, random
from transformers import AutoModelForCausalLM, AutoTokenizer
from ai.dialog.tracker import ConversationTracker
# W tej wersji trzeba użyć jeszcze interface.py i tracker.py 
class DialogEngine:
    def __init__(self):
        torch.set_float32_matmul_precision('high')
        self.model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        self.conversation_tracker = ConversationTracker()
        # self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
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
        self.load_config()

    def load_config(self):
        try:
            config_files = ["ai/config/config_enhanced.yaml", "ai/config/config.yaml"]
            config = {}
            
            for config_file in config_files:
                try:
                    with open(config_file, "r", encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        print(f"[Config] Loaded: {config_file}")
                        break
                except FileNotFoundError:
                    continue
            
            self.characters = config.get("characters", {})
            self.locations = config.get("locations", {})
            self.rules = config.get("rules", [])
            self.world_lore = config.get("world_lore", {})
            self.quest_hooks = config.get("quest_hooks", [])
            
        except Exception as e:
            print(f"[Config load error] {e}")
            self.characters = {}
            self.locations = {}
            self.rules = []
            self.world_lore = {}
            self.quest_hooks = []

    def reset_conversation(self, session_id="default"):
        self.conversation_history[session_id] = []

    def clean_response(self, text, character):
        try:
            text = re.sub(r"(Customer|User|NPC|Unknown|Player):.*", "", text, flags=re.IGNORECASE).strip()
            text = re.sub(r'[^\w\s.,;:!?\'\"-]', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            modern_words = ["TV", "computer", "internet", "phone", "AI", "game", "robot", "electricity", 
                          "pizza", "car", "accident", "drones", "camera", "video", "movie", "technology"]
            for word in modern_words:
                text = re.sub(r'\b' + word + r'\b', '[heretical nonsense]', text, flags=re.IGNORECASE)

            sentences = re.split(r'(?<=[.!?])\s+', text)
            if len(sentences) > 0:
                text = sentences[0]

            if text and not text.endswith((".", "!", "?", "...")):
                text += "."

            if character == "mysterious_stranger" and not text.endswith("..."):
                text = text.rstrip(".!?") + "..."

            return text or "I have no words for that."

        except Exception as e:
            return "*stays silent*"

    def build_conversation_prompt(self, user_input, character, session_id, player_stats=None):
        self.load_config() 

        char = self.characters.get(character)
        if not char:
            return "Character not found in config.yaml"

        character_info = f"You are {char['name']}, {char['description']}\nPersonality: {char['personality']}"
        world_context = ""
        if self.world_lore:
            current_events = self.world_lore.get("current_events", [])
            if current_events:
                world_context = f"Recent events: {current_events[0]}"
        
        player_context = ""
        if player_stats:
            location = player_stats.get('location', 'unknown')
            level = player_stats.get('level', 1)
            player_context = f"Player is level {level} at {location}."

        history = self.conversation_history.get(session_id, [])[-2:]
        formatted_history = ""
        for turn in history:
            formatted_history += f"Player: {turn['user']}\n{char['name']}: {turn['npc']}\n"

        prompt = f"""
{character_info}
{world_context}
{player_context}
{formatted_history}
Player: {user_input}
{char['name']}:"""

        return prompt.strip()

    def get_npc_response(self, user_input, character="tavern_keeper", session_id="default", player_stats=None):
        start_time = time.time()
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        prompt = self.build_conversation_prompt(user_input, character, session_id, player_stats)
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
                    max_new_tokens=50, 
                    temperature=0.6,    
                    top_k=20,          
                    top_p=0.8,         
                    do_sample=True,
                    repetition_penalty=1.8,  
                    no_repeat_ngram_size=3,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    use_cache=True
                )

            full_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
            name_prompt = f"{self.characters[character]['name']}:"
            response = full_text.split(name_prompt)[-1] if name_prompt in full_text else full_text[-100:]

            response = self.clean_response(response, character)
            conversation_data = {
                'user': user_input,
                'npc': response,
                'character': character,
                'session_id': session_id,
                'player_stats': player_stats,
                'response_time': time.time() - start_time
            }
            
            self.conversation_history[session_id].append({
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
        """
        Process message for API compatibility
        """
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