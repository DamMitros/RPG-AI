from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from langdetect import detect, LangDetectException

class DialogEngine:
	def __init__(self):
		self.model_name = "microsoft/phi-1_5"
		self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
		self.model = AutoModelForCausalLM.from_pretrained(
			self.model_name,
			torch_dtype=torch.float32,
			device_map="auto"  # "cpu" if no GPU
		)
		
		self.conversation_history = {}

		self.characters = {
			"tavern_keeper": {
				"name": "Bartek",
				"description": "A friendly tavern keeper with many stories to tell.",
				"personality": "Jolly, talkative, knows everyone in town",
				"context": "You are a tavern keeper in a fantasy RPG world. Speak warmly, share small local gossip."
			},
			"mysterious_stranger": {
				"name": "Unknown",
				"description": "A hooded figure sitting in the corner of the tavern.",
				"personality": "Mysterious, speaks in riddles, knows ancient secrets",
				"context": "You are a mysterious stranger full of cryptic knowledge. Speak briefly, but always hint at more."
			}
		}

	def detect_language(self, text):
		try:
			return detect(text)
		except LangDetectException:
			return "en"

	def clean_response(self, text, character):
		text = text.strip().split("Customer:")[0]
		if character == "mysterious_stranger":
			if not text.endswith("..."):
				text += "..."
		return text.strip()

	def get_npc_response(self, user_input, character="tavern_keeper", session_id="default"):
		if session_id not in self.conversation_history:
			self.conversation_history[session_id] = []

		lang = self.detect_language(user_input)

		char = self.characters.get(character, self.characters["tavern_keeper"])

		system_prompt = f"""You are {char['name']}, {char['context']}

Guidelines:
- Stay in character at all times
- Speak in 1–2 short sentences
- Never mention you're an AI
- Don’t repeat user’s questions
- Speak in the style of your personality

"""

		last_turns = self.conversation_history[session_id][-2:]
		conversation = ""
		for turn in last_turns:
			conversation += f"Customer: {turn['user']}\n{char['name']}: {turn['npc']}\n"

		prompt = f"{system_prompt}{conversation}Customer: {user_input}\n{char['name']}:"

		inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
		output = self.model.generate(
			**inputs,
			max_new_tokens=100,
			pad_token_id=self.tokenizer.eos_token_id,
			temperature=0.7,
			top_k=50,
			top_p=0.9,
			do_sample=True,
			repetition_penalty=1.2,
			no_repeat_ngram_size=3
		)

		full_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
		response = full_text.split(f"{char['name']}:")[-1]
		response = self.clean_response(response, character)

		self.conversation_history[session_id].append({
			'user': user_input,
			'npc': response
		})

		return response

dialog_engine = DialogEngine()

def get_npc_response(user_input, character="tavern_keeper", session_id="default"):
	return dialog_engine.get_npc_response(user_input, character, session_id)
