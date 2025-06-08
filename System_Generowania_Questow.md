# System Generowania Questów 

## Wprowdzenie

System generowania questów to połączenie modelu językowego `TinyLlama-1.1B-Chat-v1.0` z mechanikami RPG. Model językowy używany jest do dynamicznego tworzenia zadań dopasowanych do poziomu gracza i kontekstu świata gry.

## Architektura Systemu

### Komponenty Główne

#### 1. **QuestGenerator** (`ai/quest/generator.py`)
Główny komponent odpowiedzialny za generowanie questów za pomocą AI:
- **Model bazowy:** `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- **Integracja z DialogEngine:** Współdzielenie zasobów modelu językowego
- **Wielotypowe generowanie:** 5 kategorii questów (investigation, delivery, combat, gathering, rescue)
- **Adaptacyjna trudność:** Dynamiczne dostosowanie do poziomu gracza

#### 2. **QuestSystem** (`game/quest_system.py`)
Centralny system zarządzający questami:
- **Hybrydowe podejście:** Kombinacja questów statycznych (YAML) i generowanych
- **Quest Pool Management:** Automatyczne utrzymywanie puli dostępnych zadań
- **Quest State Management:** Śledzenie postępu i statusu questów

#### 3. **Quest Management Modules**
Wyspecjalizowane moduły obsługujące różne aspekty:
- `QuestManagement`: Zarządzanie stanem questów
- `QuestGeneration`: Logika generowania i odświeżania
- `QuestCompletion`: Obsługa ukończenia i nagród
- `QuestProgress`: Śledzenie postępu zadań
- `QuestActions`: Mapowanie akcji do lokacji

## Mechanizmy Generowania

### Prompt Engineering dla Questów

System używa prompt engineeringu:

```yaml
Quest type: {investigation/delivery/combat/gathering/rescue}
Difficulty: {easy/medium/hard}
Player Level: {1-10}
World Context: Stonehaven village, medieval fantasy

Format response as notice board posting:
- Title (one line, all caps)
- Description (2-3 sentences)
- Contact person
- Reward amount in gold
```

### Przykładowy Typy Questów i Charakterystyki

#### **Investigation Quests**
- **Cechy:** Urgency: urgent/standard/low, Difficulty: easy/medium/hard  
- **Słowa kluczowe:** investigate, find, discover, uncover, solve
- **Typowe kroki:** observe surroundings → talk to townspeople → examine buildings
- **Przykład:** "INVESTIGATE VILLAGE MYSTERIES"

#### **Gathering Quests**
- **Cechy:** Urgency: standard/low, Difficulty: easy/medium
- **Słowa kluczowe:** collect, gather, harvest, find
- **Typowe kroki:** ask locals → gather materials → return items
- **Przykład:** "COLLECT RARE MATERIALS"


## System Zarządzania Pulą Questów

### Strategie Pre-generacji

#### **Inicjalizacja Systemu**
```python
def _pre_generate_quests(self):
    # Generowanie questów dla poziomów 1-3
    for level in range(1, 4):
        new_quests = self.quest_generator.get_all_available_quests(level, max_quests=1)
    
    # Dodanie questów szablonowych
    template_quests = self._generate_quick_template_quests()
```

#### **Automatyczne Odświeżanie**
- **Interwał:** Co 30 minut (1800 sekund)
- **Trigger:** Spadek puli poniżej 8 questów
- **Mechanizm:** Background refresh z `maintain_quest_pool()`

## Mechanizmy Kontroli Jakości

### Parsing i Walidacja

#### **Strukturalna Analiza Tekstu**
```python
def parse_generated_quest(self, quest_text, quest_type, difficulty, player_level):
    # Wyodrębnianie: Title, Description, Contact, Reward
    # Walidacja formatowania
    # Fallback do template'ów przy błędach
```

#### **Template Fallback System**
W przypadku niepowodzenia generowania AI, system automatycznie używa pre-definiowanych szablonów:
- Gwarantowana dostępność questów
- Spójność z mechanikami gry
- Zachowanie standardu jakości

### Quest Steps Generation

#### **Dynamiczne Kroki Zadań**
```python
steps_templates = {
    "investigation": [
        {"action": "observe_your_surroundings", "location": "mainPage"},
        {"action": "talk_to_townspeople", "location": "mainPage"},
        {"action": "examine_nearby_building", "location": "mainPage"}
    ]
}
```

#### **Adaptacja do Trudności**
- **Easy:** 1 krok
- **Medium:** 2 kroki  
- **Hard:** 3+ kroków

## Integracja z World-building

### Kontekst Świata w Generowaniu

#### **World Lore Integration**
```python
world_info = f"World: {self.world_lore.get('village_name', 'Stonehaven')}"
world_info += f"Background: {self.world_lore.get('background', '')}"

# Włączenie bieżących wydarzeń
for event in self.world_lore['current_events'][:3]:
    world_info += f"- {event}"
```

#### **Quest Hooks z Konfiguracji**
```yaml
# ai/config/config_enhanced.yaml  
quest_hooks:
  - "Investigate the strange sounds from the mine"
  - "Find the missing miner Tomek"
  - "Deal with bandits on mountain paths"
```

### Mapowanie Akcji do Lokacji

#### **Action-Location System**
```python  
action_locations = {
    "talk_innkeeper": "tavern",
    "talk_merchant": "shop", 
    "mine_ore": "mine_entrance",
    "explore_deeper": "forest"
}
```

## Metryki i monitoring jakości

### Performance Metrics

#### **Czas Generowania**
- **Średnia:** ~2-3 sekundy per quest
- **Optymalizacja:** Współdzielenie modelu z DialogEngine
- **Cache:** Persistentne przechowywanie wygenerowanych questów

#### **Automatyczne Testy Jakości**
- **Text Length Validation:** Sprawdzanie długości tytułów i opisów
- **Format Compliance:** Walidacja struktury notice board
- **Content Filtering:** Filtrowanie anachronizmów i niespójności

## Wyzwania i Ograniczenia

### Techniczne Problemy

#### **Model Limitations**
- **Kontekst:** TinyLlama 1.1B ma ograniczony kontekst historyczny
- **Consistency:** Potrzeba ciągłej walidacji spójności
- **Creativity vs. Control:** Balansowanie kreatywności z mechanikami gry

#### **Performance Challenges**
- **Memory Management:** Efektywne zarządzanie cache'em questów
- **Generation Time:** Minimalizowanie czasu oczekiwania gracza
- **Resource Sharing:** Współdzielenie modelu między systemami

## Sukcesy Systemu

#### **Hybrydowe Rozwiązanie**
- **Najlepsze z obu światów:** Łączenie statycznych questów z dynamicznym generowaniem
- **Fallback Reliability:** Zawsze dostępne zadania dzięki template system
- **Scalable Design:** Łatwe dodawanie nowych typów questów

Samo generowanie zadań jest tutaj potraktowane jako element dodatkowy, taki aby można było faktycznie korzystać z aplikacji jako mini-gry RPG. Dodaje dodatkowe wykorzystanie modelu językowego, jak i dostosowuje jego możliwości za pomocą prompt engineering. 