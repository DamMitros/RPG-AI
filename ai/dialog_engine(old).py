from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, time, re

class DialogEngine:
    def __init__(self):
        torch.set_float32_matmul_precision('high')
        self.model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
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
                "description": "A friendly but salty tavern keeper who’s seen it all.",
                "personality": "Jolly but sharp-tongued, quick with a joke and quicker with a secret.",
                "context": "You run the Tawny Lion Inn, a rough but cozy tavern full of drunks and secrets. You know the village’s dirt and stories better than anyone."
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
                "context": "You are Erik, a traveling merchant in a medieval fantasy world. You buy and sell various goods. You are observant and try to suggest items that might be useful to the customer based on their appearance or stated needs. You're currently in a poor village, so your stock is limited, but you have essentials and a few curiosities. Be persuasive but not pushy."
            }
        }

    def reset_conversation(self, session_id="default"):
        self.conversation_history[session_id] = []

    def clean_response(self, text, character):
        try:
            text = re.sub(r"(Customer|User|NPC|Unknown):.*", "", text, flags=re.IGNORECASE).strip()
            text = re.sub(r'[^\w\s.,;:!?\'\"-]', '', text)
            text = text.split("\n")[0].strip()

            text = re.sub(r'\b(TV|computer|internet|phone|AI|game)\b', '[some strange word]', text, flags=re.IGNORECASE)
            text = re.sub(r'Question\s*\d+:', '', text).strip()

            if character == "mysterious_stranger":
                if not text.endswith((".", "?", "!", "...")):
                    text += "..."
                sentences = re.split(r'(?<=[.!?])\s+', text)
                text = " ".join(sentences[:2])

            text = text.replace("  ", " ").strip()
            return text or "I'm not sure how to respond to that."

        except re.error as regex_err:
            return f"(Regex error: {str(regex_err)})"

    def build_conversation_prompt(self, user_input, character, session_id):
        char = self.characters.get(character, self.characters["tavern_keeper"])
        system_prompt = f"""
You are {char['name']}, {char['context']}
Speak like a down-to-earth medieval villager — salty, quick-witted, and full of tales.
Rules:
- Keep it short and punchy (1-2 sentences).
- No AI talk or modern stuff — treat such words like madness.
- Use slang, local gossip, and humor.
- Never repeat customer.
- Send lost adventurers to quest board.
"""
        conversation = ""
        history = self.conversation_history.get(session_id, [])[-4:]
        for turn in history:
            cleaned_npc = self.clean_response(turn['npc'], character)
            conversation += f"Customer: {turn['user']}\n{char['name']}: {cleaned_npc}\n"

        prompt = f"{system_prompt.strip()}\n\n# Conversation:\n{conversation}Customer: {user_input}\n{char['name']}:"
        if "gossip" in user_input.lower():
            prompt += "\nShare a juicy village gossip full of intrigue and local color."
        return prompt

    def get_npc_response(self, user_input, character="tavern_keeper", session_id="default"):
        start_time = time.time()
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        prompt = self.build_conversation_prompt(user_input, character, session_id)

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
                    max_new_tokens=100,
                    temperature=0.75,
                    top_k=30,
                    top_p=0.85,
                    do_sample=True,
                    repetition_penalty=1.6,
                    no_repeat_ngram_size=4,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    use_cache=True
                )

            full_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
            name_prompt = f"{self.characters[character]['name']}:"
            response = full_text.split(name_prompt)[-1] if name_prompt in full_text else full_text[-100:]

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