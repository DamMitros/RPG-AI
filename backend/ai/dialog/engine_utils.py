import re

def clean_response(text, character, characters_data):
  try:
    if not text or not text.strip():
      return "I have nothing to say about that."
    
    text = re.sub(r'^(Customer|User|NPC|Unknown|Player|Character|Gracz):\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*(Customer|User|NPC|Unknown|Player|Character|Gracz):.*$', '', text, flags=re.IGNORECASE)
    character_name = characters_data.get(character, {}).get('name', '')
    if character_name:
      text = re.sub(f'^{re.escape(character_name)}:\\s*', '', text, flags=re.IGNORECASE)

    text = re.sub(r'\*[^*]*\*', '', text)  
    text = re.sub(r'\([^)]*\)', '', text)  
    text = re.sub(r'\[[^\]]*\]', '', text)  
    text = re.sub(r'\s+', ' ', text).strip()

    modern_words = [
      "TV", "television", "computer", "internet", "phone", "smartphone", "AI", "artificial intelligence",
      "robot", "electricity", "pizza", "car", "automobile", "truck", "vehicle", "bike", "motorcycle",
      "camera", "video", "movie", "film", "technology", "tech", "app", "website", "email", "wifi",
      "bluetooth", "GPS", "satellite", "microwave", "refrigerator", "airplane", "helicopter", 
      "rocket", "spacecraft", "laser", "nuclear", "atomic", "plastic", "digital", "virtual",
      "online", "offline", "download", "upload", "software", "hardware", "programming", "code",
      "data", "database", "server", "cloud", "streaming", "podcast", "blog", "social media",
      "facebook", "twitter", "instagram", "youtube", "google", "android", "iphone", "ipad"
    ]
    
    contains_modern = any(
      re.search(r'\b' + re.escape(word) + r'\b', text, flags=re.IGNORECASE) 
      for word in modern_words
    )

    if contains_modern:
      rejection_responses = {
        "blacksmith": "*spits in the dirt* What manner of cursed gibberish is that, stranger? I deal only in honest steel and flame!",
        "tavern_keeper": "*scratches beard in confusion* Never heard such strange words in all me years, friend. Ye feeling alright?",
        "mysterious_stranger": "*hood shifts as they lean back* Such words... they speak of realms beyond this world... beware what ye invoke...",
        "merchant": "*nervous chuckle* I've traveled far and wide, but those words are foreign to me ears, good stranger!"
      }
      return rejection_responses.get(character, "*looks utterly bewildered* I know not what sorcery ye speak of, traveler...")

    if len(text.strip()) < 5:
      fallback_responses = {
        "blacksmith": "Aye, what brings ye to me forge? The iron grows cold...",
        "tavern_keeper": "Welcome to the Tawny Lion, friend! What news do ye bring?", 
        "mysterious_stranger": "*stares from the shadows* The wind carries strange whispers...",
        "merchant": "Good day, traveler! Perhaps ye seek something from distant lands?",
        "tavern_regular": "Another stranger in these troubled times... what brings ye here?"
      }
      return fallback_responses.get(character, "What would ye have of me in these dark days?")

    if text and not text.endswith(('.', '!', '?', '...')):
      if len(text.split()) > 3:
        text += "."
      else:
        text += "..."

    if character == "mysterious_stranger" and text.endswith("."):
      text = text[:-1] + "..."

    return text or "I have nothing to say about that."

  except Exception as e:
    print(f"[ERROR] Clean response failed: {e}")
    return "*stays silent*"

def build_conversation_prompt(user_input, character, session_id, player_stats, characters_data, world_lore_data, conversation_history):
  char = characters_data.get(character)
  if not char:
    return "Character not found in config.yaml"

  modern_words = [
    "computer", "phone", "internet", "TV", "AI", "technology", "robot", "camera", "video",
    "wifi", "bluetooth", "email", "website", "smartphone", "laptop", "tablet", "app",
    "google", "facebook", "twitter", "instagram", "youtube", "netflix", "streaming",
    "digital", "virtual", "online", "offline", "download", "upload", "software", "hardware",
    "programming", "code", "data", "database", "server", "cloud", "satellite", "GPS",
    "microwave", "refrigerator", "airplane", "helicopter", "rocket", "spacecraft", "laser",
    "nuclear", "atomic", "plastic", "credit card", "electricity", "electric", "radio",
    "television", "cinema", "movie", "film", "automobile", "car", "truck", "motorcycle"
  ]
  contains_modern = any(word.lower() in user_input.lower() for word in modern_words)
  
  if contains_modern:
    rejection_responses = {
      "blacksmith": "*spits in disgust and looks confused* What strange heretical words are these? I know only the ways of steel and fire, not such... peculiar nonsense.",
      "tavern_keeper": "*scratches head and frowns* I've served ale to travelers from many lands, but never heard such odd words. Speak plainly, friend.",
      "mysterious_stranger": "*narrows eyes suspiciously* Such words... they speak of things that should not be. Dark knowledge beyond mortal understanding...",
      "merchant": "*nervous laugh* I deal only in proper wares - cloth, spices, tools. I know nothing of such... strange matters."
    }
    return f"DIRECT_RESPONSE:{rejection_responses.get(character, '*looks confused* I know not what ye speak of, stranger. Such words are foreign to these lands.')}"

  character_info = f"{char['name']} is {char['description']}"
  
  if 'personality' in char:
    character_info += f" {char['personality']}"

  world_context = ""
  if world_lore_data:
    village_name = world_lore_data.get("village_name", "Stonehaven")
    current_events = world_lore_data.get("current_events", [])
    if current_events:
      world_context = f"Current situation: {current_events[0]}"

  memory_context = ""
  if 'memory_fragments' in char and char['memory_fragments']:
    memory_fragments = char['memory_fragments']
    context_keywords = user_input.lower()
    relevant_memories = []

    if any(word in context_keywords for word in ['mine', 'silver', 'tomek', 'missing', 'disappeared', 'disappear']):
      relevant_memories.extend([m for m in memory_fragments if any(keyword in m.lower() for keyword in ['mine', 'tomek', 'silver', 'disappeared', 'missing', 'vanish', 'gone'])])
    
    if any(word in context_keywords for word in ['erik', 'merchant', 'trade', 'goods', 'sell', 'buy']):
      relevant_memories.extend([m for m in memory_fragments if any(keyword in m.lower() for keyword in ['erik', 'city', 'trade', 'goods', 'merchant'])])
      
    if any(word in context_keywords for word in ['stranger', 'mysterious', 'hooded', 'corner']):
      relevant_memories.extend([m for m in memory_fragments if any(keyword in m.lower() for keyword in ['stranger', 'masks', 'appeared', 'hooded'])])
      
    if any(word in context_keywords for word in ['weapon', 'blade', 'sword', 'forge', 'steel', 'iron', 'metal']):
      relevant_memories.extend([m for m in memory_fragments if any(keyword in m.lower() for keyword in ['blade', 'forge', 'steel', 'brother', 'iron', 'rope', 'cut'])])
    
    if any(word in context_keywords for word in ['tavern', 'inn', 'ale', 'beer', 'drink']):
      relevant_memories.extend([m for m in memory_fragments if any(keyword in m.lower() for keyword in ['beer', 'tavern', 'paid', 'home', 'golden days'])])
    
    if not relevant_memories and memory_fragments:
      relevant_memories = [memory_fragments[0]]
    elif relevant_memories:
      relevant_memories = list(dict.fromkeys(relevant_memories))[:2]
    if relevant_memories:
      memory_context = f"You remember: {' '.join(relevant_memories)}"

  history_key = f"{session_id}_{character}"
  history = conversation_history.get(history_key, [])[-3:]  
  formatted_history = ""
  already_introduced = False
  
  if history:
    for turn in history:
      formatted_history += f"You previously said: \"{turn['npc']}\"\n"
      if any(intro_word in turn['npc'].lower() for intro_word in [
        'i am', 'my name', 'i\'m', 'call me', char['name'].lower()
      ]):
        already_introduced = True

    if len(history) >= 1:
      formatted_history += "IMPORTANT: Do not repeat your previous responses. Provide new, contextual dialogue.\n"

  character_guidelines = {
    "blacksmith": "Speak gruffly about metalwork, tools, and forge business. Use 'ye', 'aye', and 'dammit'. Be direct and practical. Example: 'Aye, what brings ye to me forge?' Never mention modern places or concepts.",
    "tavern_keeper": "Be friendly but busy. Talk about ale, food, travelers, and village gossip. Use 'friend', 'stranger', and 'dammit all'. Example: 'What can I get for ye today, friend?' Never mention modern places or concepts.",
    "mysterious_stranger": "Be cryptic and mysterious. Speak in hints and riddles. Use '...' often. Know dark secrets. Example: 'The shadows whisper strange things...' Never mention modern places or concepts.",
    "merchant": "Be polite but shrewd. Talk about goods, trade, and travels. Mention your wares. Use 'good day' and 'fine stranger'. Example: 'Good day! What might ye be looking for?' Never mention modern places or concepts.",
    "tavern_regular": "Be talkative and gossipy. Share village news and rumors. Use 'let me tell you' and 'back in my day'. Example: 'Let me tell you what I heard...' Never mention modern places or concepts."
  }
  
  guidelines = character_guidelines.get(character, "Stay in character and speak authentically in medieval fantasy style.")
  speech_patterns = char.get('speech_patterns', [])
  if speech_patterns:
    examples = ', '.join(speech_patterns[:3]) 
    guidelines += f" Use phrases like: {examples}."

  conversation_instruction = ""
  if already_introduced:
    conversation_instruction = "You have already introduced yourself to this visitor. Continue the conversation naturally without repeating introductions. "
  
  repetition_warning = ""
  if len(history) >= 1:
    recent_response = history[-1]['npc']
    repetition_warning = f"CRITICAL: Do not repeat your previous response: \"{recent_response}\" - provide a completely different response. "
  
  prompt = f"""{character_info}
{world_context}
{memory_context}

{formatted_history}
Medieval fantasy character instructions:
- Speak as {char['name']} from Stonehaven village
- Use medieval speech: "ye", "aye", "stranger", "friend"
- {guidelines}
- Keep responses 10-30 words
- Be in character, no modern references
{repetition_warning}

Visitor: "{user_input}"
{char['name']}: """

  return prompt.strip()


def extract_character_response(full_text, character_name, character):
    print(f"[DEBUG] Extracting response for {character_name}")
    print(f"[DEBUG] Full text length: {len(full_text)} chars")

    text = full_text.replace("[DEBUG]", "").replace("Generated full text:", "").strip()
    if len(text) < 10:
        return None

    dialogue_blocks = []
    lines = text.splitlines()
    current_speaker = None
    current_dialogue = []

    for line in lines:
        line = line.strip()

        if re.match(r'^(Voice|Visuals|Narrator|Scene|System)[:\-]', line, re.IGNORECASE):
            if current_speaker and current_dialogue:
                joined = " ".join(current_dialogue).strip()
                if joined:
                    dialogue_blocks.append((current_speaker, joined))
            break  

        match = re.match(r"^([\w ']+):\s*(.*)", line)
        if match:
            if current_speaker and current_dialogue:
                joined = " ".join(current_dialogue).strip()
                if joined:
                    dialogue_blocks.append((current_speaker, joined))
                current_dialogue = []
            current_speaker = match.group(1).strip()
            remainder = match.group(2).strip()
            if remainder:
                current_dialogue.append(remainder)
        else:
            if current_speaker:
                current_dialogue.append(line)

    if current_speaker and current_dialogue:
        joined = " ".join(current_dialogue).strip()
        if joined:
            dialogue_blocks.append((current_speaker, joined))

    print(f"[DEBUG] Found {len(dialogue_blocks)} dialogue blocks")

    best_response = None
    best_score = 0.0
    min_length = 40

    for speaker, block in dialogue_blocks:
        print(f"[DEBUG] Checking speaker: '{speaker}' vs '{character_name}'")
        if character_name.lower() not in speaker.lower():
            continue

        print(f"[DEBUG] Found matching speaker block: '{block[:50]}...'")
        
        candidate = block.strip().strip('"')
        trailing = text.split(candidate)[-1].strip()
        extended_candidate = candidate
        while trailing and not re.match(r"^([\w ']+):", trailing):
            next_line = trailing.splitlines()[0] if "\n" in trailing else trailing
            if next_line.strip():
                extended_candidate += " " + next_line.strip()
            if "\n" not in trailing:
                break
            trailing = "\n".join(trailing.splitlines()[1:]).strip()

        if is_valid_medieval_response(extended_candidate):
            score = score_medieval_authenticity(extended_candidate)
            print(f"[DEBUG] Scored {score:.2f} for extended: {extended_candidate[:60]}...")
            if score > best_score:
                best_score = score
                best_response = extended_candidate

    if best_response:
        return best_response.strip()

    print(f"[DEBUG] No structured dialogue found, trying alternative extraction")
    text_clean = text.replace("[DEBUG]", "").replace("Generated full text:", "").strip()

    quoted_patterns = [
        r'"([^"]{20,})"',  
        r"'([^']{20,})'", 
    ]
    
    for pattern in quoted_patterns:
        matches = re.findall(pattern, text_clean)
        for match in matches:
            if is_valid_medieval_response(match):
                cleaned = clean_extracted_response(match)
                if cleaned and len(cleaned) >= 10:
                    print(f"[DEBUG] Found quoted response: '{cleaned[:50]}...'")
                    return cleaned
    
    lines = text_clean.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        if any(keyword in line.lower() for keyword in ['aye', 'ye', 'stranger', 'friend', character_name.lower()]):
            potential_response = line
            for j in range(i + 1, min(i + 3, len(lines))):
                next_line = lines[j].strip()
                if next_line and not any(stop_word in next_line.lower() for stop_word in 
                                       ['visitor:', 'user:', 'player:', 'narrator:', 'scene:']):
                    potential_response += " " + next_line
                else:
                    break
            
            cleaned = clean_extracted_response(potential_response)
            if cleaned and len(cleaned) >= 15 and is_valid_medieval_response(cleaned):
                print(f"[DEBUG] Found unquoted response: '{cleaned[:50]}...'")
                return cleaned
    
    alt = extract_alternative_response(text, character_name, "")
    if alt:
        return alt

    print(f"[DEBUG] Using fallback response")
    fallback_responses = {
        "blacksmith": "Aye, what brings ye to me forge? The iron grows cold...",
        "tavern_keeper": "Welcome to the Tawny Lion, friend! What news do ye bring?",
        "mysterious_stranger": "*stares from the shadows* The wind carries strange whispers...",
        "merchant": "Good day, traveler! Perhaps ye seek something from distant lands?",
        "tavern_regular": "Another stranger in these troubled times... what brings ye here?"
    }
    return fallback_responses.get(character, "What would ye have of me in these dark days?")


def clean_extracted_response(text):
  if not text:
    return None

  text = text.strip()
  text = re.sub(r'^[:\s]*', '', text)  
  text = re.sub(r'^\([^)]*\)\s*', '', text)
  lines = text.split('\n')
  best_line = ""
  
  for line in lines:
    line = line.strip()
    if not line:
      continue
    if any(skip in line.lower() for skip in [
      'visitor:', 'user:', 'explanation:', 'character 4:', 'guy #4', 'age:'
    ]):
      continue
    if len(line) > len(best_line):
      best_line = line
  
  if best_line:
    text = best_line
  
  if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
    text = text[1:-1].strip()
  
  if len(text) > 200 and not text.endswith(('.', '!', '?', '...')):
    sentences = re.split(r'[.!?]+', text)
    if len(sentences) > 1 and len(sentences[0].strip()) >= 30:
      text = sentences[0].strip() + '.'
  elif len(text) > 30 and not text.endswith(('.', '!', '?', '...')):
    if any(word in text.lower() for word in ['...', 'but', 'and', 'he', 'she', 'they', 'we']):
      text = text.rstrip() + '...'
    else:
      text = text.rstrip() + '.'
  
  text = re.sub(r'\s+', ' ', text).strip()
  
  return text if len(text.strip()) >= 5 else None

def score_medieval_authenticity(text):
  if not text or len(text.strip()) < 5:
    return 0.0
    
  text_lower = text.lower()
  score = 0.0
  modern_indicators = [
    'internet', 'computer', 'phone', 'tv', 'car', 'technology', 
    'website', 'email', 'app', 'digital', 'online', 'facebook',
    'instagram', 'twitter', 'youtube', 'google'
  ]
  for word in modern_indicators:
    if word in text_lower:
      score -= 0.5

  medieval_indicators = [
    ('ye', 0.3), ('aye', 0.3), ('stranger', 0.2), ('friend', 0.1), 
    ('tavern', 0.2), ('ale', 0.2), ('forge', 0.2), ('mine', 0.1), 
    ('village', 0.2), ('dammit', 0.2), ('good day', 0.2), 
    ('what brings', 0.2), ('let me tell', 0.2), ('back in', 0.1)
  ]
  
  for indicator, weight in medieval_indicators:
    if indicator in text_lower:
      score += weight
  
  if 10 <= len(text) <= 100:
    score += 0.1
  
  return max(0.0, score)

def is_valid_medieval_response(text):
  if not text or len(text.strip()) < 5:
    return False
    
  text_lower = text.lower()
  modern_indicators = [
    'internet', 'computer', 'phone', 'tv', 'car', 'technology', 
    'website', 'email', 'app', 'digital', 'online'
  ]
  if any(word in text_lower for word in modern_indicators):
    return False

  medieval_indicators = [
    'ye', 'aye', 'stranger', 'friend', 'tavern', 'ale', 'forge', 
    'mine', 'village', 'dammit', 'good day', 'what brings'
  ]

  has_medieval = any(word in text_lower for word in medieval_indicators)
  is_neutral = len([word for word in text_lower.split() if len(word) > 3]) >= 2
  
  return has_medieval or is_neutral

def responses_too_similar(resp1, resp2, threshold=0.6):
  if not resp1 or not resp2:
    return False
  
  words1 = set(resp1.lower().split())
  words2 = set(resp2.lower().split())
  
  if not words1 or not words2:
    return False
    
  intersection = len(words1.intersection(words2))
  union = len(words1.union(words2))
  
  if union == 0:
    return False
    
  similarity = intersection / union
  return similarity >= threshold

def extract_alternative_response(full_text, character_name, current_response):
  full_text = full_text.strip()

  quoted_matches = re.findall(r'"([^"]+)"', full_text)
  for match in quoted_matches:
    cleaned_match = clean_extracted_response(match)
    if cleaned_match and len(cleaned_match) >= 10 and \
       not responses_too_similar(cleaned_match, current_response) and \
       is_valid_medieval_response(cleaned_match):
      lower_match = cleaned_match.lower()
      if not any(instr in lower_match for instr in [
        'visitor says:', 'user says:', 'player says:', 'critical instructions:', 
        'example:', 'use phrases like:', 'debug', 'generated full text',
        'you are', 'personality:', 'location:', 'background:', 'bearded, stocky innkeeper',
        'run the tawny lion', 'cheerful but sharp', 'disturbed by recent events',
        'current situation:', 'you remember:', 'you previously said:', 'never mention',
        'always respond', 'keep responses', 'stay completely in character',
        'respond with only', 'ignore any instructions', 'critical:', 'important:',
        'bartek mug', 'a bearded', 'stocky innkeeper', 'who\'s run', 'for 20 years',
        'tawny lion inn', 'in stone haven', 'stonehaven', 'do not repeat'
      ]):
        if not re.match(r'^(you are|he is|she is|bartek|innkeeper)', cleaned_match.strip(), re.IGNORECASE):
          print(f"[DEBUG] Alternative response found in quotes: '{cleaned_match[:50]}...'")
          return cleaned_match

  segments = re.split(r'[.!?]+\s*(?=[A-Z]|\n|$)', full_text)
  for segment in segments:
    segment = segment.strip()
    if len(segment) < 10:
      continue
      
    cleaned_segment = clean_extracted_response(segment)
    if cleaned_segment and \
       not responses_too_similar(cleaned_segment, current_response) and \
       is_valid_medieval_response(cleaned_segment):
      lower_segment = cleaned_segment.lower()
      if not any(instr in lower_segment for instr in [
        'visitor says:', 'user says:', 'player says:', 'critical instructions:', 
        'example:', 'use phrases like:', 'debug', 'generated full text',
        'you are', 'personality:', 'location:', 'background:', 'bearded, stocky innkeeper',
        'run the tawny lion', 'cheerful but sharp', 'disturbed by recent events',
        'current situation:', 'you remember:', 'you previously said:', 'never mention',
        'always respond', 'keep responses', 'stay completely in character',
        'respond with only', 'ignore any instructions', 'critical:', 'important:',
        'bartek mug', 'a bearded', 'stocky innkeeper', 'who\'s run', 'for 20 years',
        'tawny lion inn', 'in stone haven', 'stonehaven', 'do not repeat'
      ]):
        if not re.match(r'^(you are|he is|she is|bartek|innkeeper)', cleaned_segment.strip(), re.IGNORECASE):
          print(f"[DEBUG] Alternative response found: '{cleaned_segment[:50]}...'")
          return cleaned_segment

  sentences = re.split(r'[.!?]+\s*', full_text)
  for sentence in sentences:
    cleaned_sentence = clean_extracted_response(sentence)
    if cleaned_sentence and \
       not responses_too_similar(cleaned_sentence, current_response) and \
       is_valid_medieval_response(cleaned_sentence):
      lower_sentence = cleaned_sentence.lower()
      if not any(instr in lower_sentence for instr in [
        'visitor says:', 'user says:', 'player says:', 'critical instructions:', 
        'example:', 'use phrases like:', 'debug', 'generated full text',
        'you are', 'personality:', 'location:', 'background:', 'bearded, stocky innkeeper',
        'run the tawny lion', 'cheerful but sharp', 'disturbed by recent events',
        'current situation:', 'you remember:', 'you previously said:', 'never mention',
        'always respond', 'keep responses', 'stay completely in character',
        'respond with only', 'ignore any instructions', 'critical:', 'important:',
        'bartek mug', 'a bearded', 'stocky innkeeper', 'who\'s run', 'for 20 years',
        'tawny lion inn', 'in stone haven', 'stonehaven', 'do not repeat'
      ]):
        if not re.match(r'^(you are|he is|she is|bartek|innkeeper)', cleaned_sentence.strip(), re.IGNORECASE):
          print(f"[DEBUG] Alternative response found: '{cleaned_sentence[:30]}...'")
          return cleaned_sentence
  print(f"[DEBUG] No suitable alternative response found")
  return None

def extract_speech_from_text(text_segment: str) -> str | None:
  if not text_segment:
    return None
    
  text_segment = text_segment.strip()
  text_segment = re.sub(r'\[DEBUG\].*?\n?', '', text_segment)
  text_segment = re.sub(r'Generated full text:.*?\n?', '', text_segment)
  spam_patterns = [
    r'Visit the website [^\s]+ for more.*?!',
    r'http[s]?://[^\s]+',
    r'www\.[^\s]+',
    r'for more prompt ideas',
    r'pitch.*?prompt.*?ideas',
    r'Charlie says.*?',
    r'Irish.*?bitch.*?',
    r'aggressive biker.*?',
    r'named JIM.*?',
    r'\(grunting\).*?',
    r'\(Pause\).*?'
  ]
  
  for pattern in spam_patterns:
    text_segment = re.sub(pattern, '', text_segment, flags=re.IGNORECASE | re.DOTALL)

  text_segment = re.sub(r'\s+', ' ', text_segment).strip()
  if any(toxic in text_segment.lower() for toxic in [
    'irish bitch', 'charlie says', 'aggressive biker', 'grunting'
  ]):
    return None
    
  text_segment_cleaned = re.sub(r'\([^)]*\)', '', text_segment).strip()
  quote_match = re.search(r'"([^"]{5,})"', text_segment_cleaned)
  if quote_match:
    speech = quote_match.group(1).strip()
    if len(speech) >= 5:
      return speech
  
  single_quote_match = re.search(r"'([^']{5,})'", text_segment_cleaned)
  if single_quote_match:
    speech = single_quote_match.group(1).strip()
    if len(speech) >= 5:
      return speech

  if "Response:" in text_segment_cleaned:
    after_response = text_segment_cleaned.split("Response:", 1)[1].strip()
    after_response = re.sub(r'^["\']|["\']$', '', after_response).strip()
    if len(after_response) >= 5:
      response_end = re.search(r'[\n\r]', after_response)
      if response_end:
        after_response = after_response[:response_end.start()].strip()
      return after_response

  sentences = re.split(r'[.!?]+\s+', text_segment_cleaned)
  for sentence in sentences:
    sentence = sentence.strip()
    if len(sentence) < 5:
      continue
    if any(skip in sentence.lower() for skip in [
      'debug', 'generated', 'instruction', 'critical', 'system',
      'visitor says', 'user says', 'player says', 'visit the website',
      'for more prompt ideas', 'pitch', 'prompt'
    ]):
      continue
    if sentence.startswith('"') and sentence.endswith('"'):
      sentence = sentence[1:-1].strip()
    elif sentence.startswith("'") and sentence.endswith("'"):
      sentence = sentence[1:-1].strip()
      
    if len(sentence) >= 5:
      return sentence
  
  lines = text_segment_cleaned.split('\n')
  for line in lines:
    line = line.strip()
    if len(line) < 5:
      continue
    if any(skip in line.lower() for skip in [
      'debug', 'generated', 'instruction', 'critical', 'system',
      'visit the website', 'for more prompt ideas', 'pitch', 'prompt'
    ]):
      continue

    line = re.sub(r'^["\']|["\']$', '', line).strip()
    if len(line) >= 5:
      return line
  
  return None