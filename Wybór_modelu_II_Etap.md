# RPG AI Adventure - Dokumentacja Projektu: Finalizacja Wyboru Modelu

## Dodatkowe Testy Kandydatów i Ostateczna Decyzja

Po wstępnych testach podstawowych modeli przeprowadzono dodatkowe eksperymenty z nowszymi kandydatami, koncentrując się na balansie między jakością a wydajnością.

### 7. **Rozszerzone Testy Modeli:**

#### **TinyLlama/TinyLlama-1.1B-Chat-v1.0:**
**Test dialogowy:**
```
Gracz: Hi where am I?
NPC: Ah! The barren land is not that far from here; you're in an ancient ruin town on top of some hills overlooking our small hamlet. Welcome back home after your long journey across mountains with all its troublesome challenges ahead for us humans living there nowadays But we don't mind because everyone knows how hard life was when everything used to be so simple as stone walls surrounding cobbled streets filled up by stalls selling various goods ranging from...
```

**Obserwacje:**
- **Wydajność:** Znacznie lepsza niż `phi-2`, porównywalny czas odpowiedzi do `Phi-1.5`
- **Jakość:** Zaskakująco dobre utrzymywanie kontekstu fantasy i atmosfery
- **Charakteryzacja:** Model wykazuje potencjał do dobrego wcielania się w role, ale wymaga dokładnej charakteryzacji przez prompt engineering
- **Stabilność:** Konsekwentne odpowiedzi, mniejsza tendencja do "gubienia wątku"

#### **microsoft/Phi-3-mini:**
**Status:** Nieudane uruchomienie ze względu na problemy kompatybilności z lokalnym środowiskiem

#### **stabilityai/stablelm-zephyr-3b:**
**Test dialogowy:**
```
Gracz: Hi where am I?
NPC: Greetings! You find yourself at the Tawny Lion, a lively yet humble inn situated within the heart of village. The tavern knows of the place and its secrets better than anyone else.
```

**Obserwacje:**
- **Jakość:** Dobra charakteryzacja, właściwa nazwa tawerny
- **Wydajność:** Akceptowalna, ale wyższe wymagania sprzętowe
- **Ograniczenia:** Większy rozmiar modelu przy marginalnie lepszych wynikach

### 8. **Ostateczna Decyzja: TinyLlama-1.1B-Chat-v1.0**

Po dogłębnej analizie wszystkich kandydatów podjęto decyzję o wyborze modelu `TinyLlama/TinyLlama-1.1B-Chat-v1.0` jako podstawy silnika dialogowego z następujących powodów:

**Uzasadnienie wyboru:**
- **Optymalna wydajność:** Szybkie czasy odpowiedzi przy zachowaniu dobrej jakości
- **Niskie wymagania sprzętowe:** Umożliwia uruchomienie na szerszym spektrum urządzeń
- **Potencjał charakteryzacji:** Model wykazuje dużą plastyczność w dostosowywaniu się do różnych ról poprzez szczegółowe prompt engineering
- **Stabilność:** Konsekwentne zachowanie podczas długich sesji dialogowych

**Strategia implementacji:**
Zamiast polegania wyłącznie na wbudowanych możliwościach modelu, skupiono się na **precyzyjnej charakteryzacji** poprzez:
- Szczegółowe prompty systemowe dla każdej postaci NPC
- Zaawansowane techniki prompt engineering
- Dokładne definiowanie kontekstu i ograniczeń dla każdej roli
- Implementację dodatkowych warstw logiki w [`clean_response`](ai/dialog_engine.py)

### 9. **Planowane Usprawnienia Charakteryzacji**

- Rozbudowa słownika `characters` w [`DialogEngine`](ai/dialog_engine.py) o bardziej szczegółowe profile
- Implementacja dynamicznego dostosowywania promptów na podstawie kontekstu rozmowy
- Dodanie warstwy post-processingu specyficznej dla każdej postaci

**Podsumowanie:** Wybór `TinyLlama-1.1B-Chat-v1.0` reprezentuje strategię "lekki model + zaawansowana charakteryzacja", która zapewnia optymalny balans między wydajnością, elastycznością a jakością interakcji w kontekście gry RPG.