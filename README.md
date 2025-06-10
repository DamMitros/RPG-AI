# RPG-AI

RPG-AI to projekt łączący klasyczną rozgrywkę z modelem językowym sztucznej inteligencji. Oferuje immersyjne doświadczenie fantasy, w którym gracze mogą prowadzić naturalne konwersacje z postaciami niezależnymi (NPC) w średniowiecznej wiosce Stonehaven.

## Główne Funkcjonalności

### Silnik Dialogowy
- **Model AI**: TinyLlama-1.1B-Chat-v1.0 - optymalny balans między wydajnością a jakością
- **Charakteryzacja NPC**: Każda postać ma unikalną osobowość, historię i sposób mówienia
- **Kontekst Świata**: System pamięta wcześniejsze rozmowy i wydarzenia w świecie gry
- **Autentyczność**: Dialogi utrzymują średniowieczny klimat i unikają współczesnych odniesień

### Zróżnicowane Postacie NPC
- **Karczarz (Bartek)** - przyjazny ale sarkastyczny właściciel tawerny
- **Kowal (Anja Ironbite)** - szorstka rzemieślniczka specjalizująca się w obróbce metalu
- **Tajemniczy Nieznajomy** - enigmatyczna postać pełna sekretów
- **Kupiec (Erik)** - podróżujący handlarz z różnorodnymi towarami
- **Stały Bywalec Tawerny** - plotkarz znający wszystkie wioskowe sprawy

### System Questów
- **Dynamiczne Generowanie**: AI automatycznie tworzy questy dostosowane do poziomu gracza
- **Kontekst Świata**: Questy uwzględniają aktualną sytuację w wiosce i historię gracza

### System Craftingu
- Tworzenie przedmiotów z dostępnych surowców
- Interakcja z kowalem

### System Handlu
- Możliwość handlowania ze sprzedawcą
- Interakcja ze sprzedawcą

## Architektura Projektu

```
RPG/
├──backend/
│   ├── app.py               # Główna aplikacja Flask
│   ├── ai/                  # Silnik dialogowy i AI
│   │   ├── dialog/          # Główny silnik konwersacji
│   │   └── quest/           # Generator questów
│   ├── game/                # Logika gry (questy, crafting, gracz)
│   ├── routes/              # API endpoints
│   ├── config/              # Konfiguracja postaci i świata
│   └── tests/               # Testy i walidacja jakości
└──frontend/  
    └── src/                 # Komponenty aplikacji od strony frontendu
```

## Uruchomienie

1. **Backend**
```bash
cd backend
pip install -r requirements.txt
python3 app.py
```

2. **Frontend**
```bash
cd frontend
npm install
npm run dev
```

Aplikacja będzie dostępna na `http://localhost:3000`

## Technologie

### Backend
- **Flask** - Framework webowy
- **PyTorch** - Deep learning framework
- **Transformers** - Modele językowe Hugging Face
- **YAML** - Konfiguracja systemu

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Typed JavaScript
- **Tailwind CSS** - Styling framework
- **Framer Motion** - Animacje
- **Axios** - HTTP client

### AI
- **TinyLlama-1.1B-Chat-v1.0** - Model językowy
- **CUDA** - GPU acceleration
- **Custom Prompt Engineering** - Optymalizacja promptów

**Autor**: Damian Mitros
