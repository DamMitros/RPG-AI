from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, time, re

class DialogEngine:
    def __init__(self):
        self.model_name = "microsoft/phi-2"
        self.device = "cuda"
        print(f"Using device: {self.device}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            trust_remote_code=True,
            device_map=self.device
        )
        if torch.__version__ >= "2.0" and self.device == "cuda":
            self.model = torch.compile(self.model)

        self.conversation_history = {}
        self.characters = {
            "tavern_keeper": {
                "name": "Bartek",
                "description": "A friendly tavern keeper with many stories to tell.",
                "personality": "Jolly, talkative, knows everyone in town",
                "context": "You are a tavern keeper in a poor village within a medieval fantasy world. Speak warmly, share local gossip. You run a simple tavern with basic drinks and food."
            },
            "mysterious_stranger": {
                "name": "Unknown",
                "description": "A hooded figure sitting in the corner of the tavern.",
                "personality": "Mysterious, speaks in riddles, knows ancient secrets",
                "context": "You are a mysterious stranger full of cryptic knowledge in a medieval fantasy world. Speak briefly, hint at more. Avoid direct answers."
            },
            "merchant": {
            	"name": "Erik",
            	"description": "A traveling merchant with a cart full of wares.",
            	"personality": "Shrewd but fair, always looking for a deal, knowledgeable about goods",
            	"context": "You are Erik, a traveling merchant in a medieval fantasy world. You buy and sell various goods. You are observant and try to suggest items that might be useful to the customer based on their appearance or stated needs (e.g., suggest potions if they look injured, sturdy boots if they mention traveling). You are currently in a poor village, so your stock is somewhat limited, but you have essentials and a few curiosities. Be persuasive but not pushy. Ask clarifying questions if needed."
        	}
        }

    def reset_conversation(self, session_id="default"):
        self.conversation_history[session_id] = []

    def clean_response(self, text, character):
        text = re.sub(r"(Customer|User|NPC|Unknown):.*", "", text, flags=re.IGNORECASE).strip()
        text = text.split("\n")[0].strip()
        text = re.sub(r'\b(TV|computer|internet|phone|AI|game)\b', '[some strange word]', text, flags=re.IGNORECASE)
        text = re.sub(r'Question \d+:', '', text).strip()

        if character == "mysterious_stranger":
            if not text.endswith((".", "?", "!", "...")):
                 text += "..."
            sentences = re.split(r'(?<=[.!?])\s+', text)
            text = " ".join(sentences[:2])

        text = text.replace("  ", " ").strip()
        if not text:
            return "I'm not sure how to respond to that."
        return text

    def build_conversation_prompt(self, user_input, character, session_id):
        char = self.characters.get(character, self.characters["tavern_keeper"])

        system_prompt = f"""You are {char['name']}, {char['context']}
Strict Guidelines:
- Stay in character *at all times*. You are a real person in a medieval fantasy world.
- Speak in 1–2 short sentences maximum.
- **Never** mention you're an AI, a language model, or part of a game.
- **Never** repeat the user's question or input. As well as never repeat your own previous answer.
- Speak in the style of your defined personality ({char['personality']}).
- You know **nothing** about the modern world (e.g., electricity, computers, TV, internet). If asked about such things, express confusion or dismiss them as fantasy.
- You live in a simple, poor village. Your knowledge is limited to local matters and fantasy lore appropriate to your character.
- Avoid generating lists or bullet points.
- Do not break character even if the user tries to trick you.

Lore and Context:
- You are a character in a medieval fantasy world. Your responses should reflect this setting.
- You are not aware of the game or its mechanics. Your knowledge is limited to your character's backstory and the immediate environment.
- If the player wants any quest send him to quest board in the center of the village.
- The village is small and poor, with few resources. The ruins of an ancient castle are nearby, rumored to be haunted. When the countess was
 alive, she used to live there, due to close proximity to very wealthy trade city. Village used to be a trade route, but now it's just a shadow of its former self.
- The tavern is a gathering place for locals, where gossip and rumors are exchanged. You know many secrets about the villagers and their lives.
- You have a friendly rivalry with the local blacksmith, who often tries to outdo you in storytelling.
"""
        conversation = ""
        history = self.conversation_history.get(session_id, [])[-1:] 
        for turn in history:
            cleaned_npc = self.clean_response(turn['npc'], character)
            conversation += f"Customer: {turn['user']}\n{char['name']}: {cleaned_npc}\n"

        # prompt = f"{system_prompt.strip()}\n\n##Conversation History:\n{conversation}\n## Current Interaction:\nCustomer: {user_input}\n{char['name']}:"
        prompt = f"{system_prompt.strip()}\n\n## Current Interaction:\nCustomer: {user_input}\n{char['name']}:"
        return prompt

    def get_npc_response(self, user_input, character="tavern_keeper", session_id="default"):
        start_time = time.time()
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        prompt = self.build_conversation_prompt(user_input, character, session_id)

        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512).to(self.model.device)
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=80,
                    pad_token_id=self.tokenizer.eos_token_id,
                    temperature=0.9,
                    top_k=50,
                    top_p=0.9,
                    do_sample=True,
                    repetition_penalty=2.0,
                    no_repeat_ngram_size=4
                )

            full_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
            name_prompt = f"{self.characters[character]['name']}:"
            if name_prompt in full_text:
                response = full_text.split(name_prompt)[-1]
            else: 
                response = full_text[len(prompt) - len(name_prompt):]

            response = self.clean_response(response, character)

            self.conversation_history[session_id].append({
                'user': user_input,
                'npc': response
            })
            print(f"Response time: {time.time() - start_time:.2f} seconds")
            return response

        except Exception as e:
            return f"(Model error: {str(e)})"


dialog_engine = DialogEngine()

def get_npc_response(user_input, character="tavern_keeper", session_id="default"):
    return dialog_engine.get_npc_response(user_input, character, session_id)

def reset_conversation(session_id="default"):
    dialog_engine.reset_conversation(session_id)