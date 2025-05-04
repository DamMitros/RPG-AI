# RPG AI Adventure - Dokumentacja Projektu: Silnik Dialogowy NPC

## Cel Badawczy: Wybór i Dostosowanie Modelu Językowego dla Interakcji z NPC

Kluczowym elementem projektu było stworzenie efektywnego silnika dialogowego dla postaci niezależnych (NPC), zaimplementowanego w pliku [`ai/dialog_engine.py`](ai/dialog_engine.py). Wymagało to wyboru odpowiedniego bazowego modelu językowego oraz jego dostosowania.

**Główny Cel:** Znalezienie wstępnie wytrenowanego modelu językowego, który potrafi:
*   Generować wiarygodne dialogi zgodne z charakterem i kontekstem różnych postaci NPC.
*   Ściśle trzymać się przypisanej "roli" (osobowości, wiedzy, ograniczeń).
*   Działać optymalnie pod względem czasu odpowiedzi i wymagań sprzętowych.

**Proces Selekcji i Testowania:**

1.  **Identyfikacja Kandydatów:** Wyszukano potencjalne modele językowe, biorąc pod uwagę ich rozmiar, deklarowaną wydajność i zdolności konwersacyjne. Początkowi kandydaci to:
    *   `microsoft/DialoGPT-small`
    *   `gpt2`
    *   `microsoft/Phi-1.5`
    *   Później dodano: `TinyLlama-1.1B-Chat`, `microsoft/phi-2`

2.  **Integracja i Wstępne Testy:** Każdy model zintegrowano z klasą [`DialogEngine`](ai/dialog_engine.py). Przeprowadzono podstawowe rozmowy z różnymi postaciami NPC zdefiniowanymi w słowniku `characters` ([`ai/dialog_engine.py`](ai/dialog_engine.py)), aby ocenić ich podstawowe możliwości.

3.  **Kryteria Oceny:** Modele oceniano według następujących kryteriów:
    *   **Wczucie się w Rolę:** Jak dobrze model utrzymywał zdefiniowaną osobowość (`name`, `description`, `personality`, `context`).
    *   **Przestrzeganie Instrukcji:** Zdolność do respektowania "Ścisłych Wytycznych" w prompcie systemowym (np. limit zdań, unikanie wzmianek o byciu AI, pozostawanie w kontekście świata gry).
    *   **Jakość Odpowiedzi:** Spójność, trafność, kreatywność i naturalność generowanego dialogu.
    *   **Powtarzalność:** Tendencja do powtarzania tych samych fraz lub odpowiedzi.
    *   **Wydajność:** Szybkość generowania odpowiedzi (czas wnioskowania) i zużycie zasobów (pamięć VRAM/RAM).

4.  **Obserwacje z Wstępnych Testów:**
    *   `microsoft/DialoGPT-small`: Lekki i szybki, jakość dialogów niska, często odbiegał od tematu i roli.
    *   `gpt2`: Podobne problemy jak DialoGPT; trudności z utrzymaniem roli i generowaniem spójnych odpowiedzi w kontekście.
    *   `microsoft/Phi-1.5`: Znacznie lepsza jakość odpowiedzi i trzymanie się roli, ale dłuższy czas generowania.
    *   `TinyLlama-1.1B-Chat`: Wydajność porównywalna do `Phi-1.5`, ale jakość odpowiedzi znacznie gorsza, bliższa `gpt2`.
    *   `microsoft/phi-2`: Najlepsza jakość generowanych dialogów i najlepsze trzymanie się roli, ale najdłuższy czas odpowiedzi (nawet do minuty).

5.  **Inżynieria Promptów i Strojenie Parametrów:** Dla najbardziej obiecujących modeli (`Phi-1.5` i `phi-2`) przeprowadzono iteracyjne udoskonalanie:
    *   **Prompt Systemowy:** Dopracowano instrukcje w metodzie [`build_conversation_prompt`](ai/dialog_engine.py), dodając bardziej szczegółowe wytyczne dotyczące roli, kontekstu, ograniczeń wiedzy i stylu wypowiedzi.
    *   **Parametry Generowania:** Eksperymentowano z parametrami wywołania metody `model.generate` w [`get_npc_response`](ai/dialog_engine.py) (`max_new_tokens`, `temperature`, `top_k`, `top_p`, `repetition_penalty`, `no_repeat_ngram_size`), aby zbalansować kreatywność, spójność i unikanie powtórzeń.

6.  **Ostateczny Wybór:** Model `microsoft/phi-2` został wybrany jako optymalny kompromis. Mimo dłuższego czasu generowania, jego zdolność do podążania za złożonymi instrukcjami promptu i generowania wysokiej jakości, spójnych z rolą odpowiedzi przeważyła nad innymi kandydatami. Dalsze optymalizacje (np. kwantyzacja, lepsze zarządzanie pamięcią) mogą w przyszłości poprawić jego wydajność.

**Identyfikowane Wyzwania i Rozwiązania:**

*   **Wychodzenie z Roli / Wzmianki o byciu AI:** Rozwiązane przez dodanie bardzo ścisłych wytycznych w prompcie systemowym i filtrowanie odpowiedzi w metodzie [`clean_response`](ai/dialog_engine.py).
*   **Powtarzanie Odpowiedzi:** Zminimalizowane przez dostrojenie parametrów `repetition_penalty` i `no_repeat_ngram_size`.
*   **Przestrzeganie Ograniczeń Wiedzy (Świat Gry):** Wymagało szczegółowego opisania kontekstu i ograniczeń w prompcie oraz dodania reguł czyszczących w [`clean_response`](ai/dialog_engine.py) usuwających współczesne terminy.
*   **Balans Kreatywność vs. Ograniczenia:** Ciągły proces dostrajania promptu i parametrów generowania.
*   **Wydajność:** Największe wyzwanie przy modelu `phi-2`. Częściowo zaadresowane przez użycie `torch.compile` i `float16` na GPU. Dalsze potencjalne kroki to kwantyzacja modelu lub eksploracja mniejszych, ale równie zdolnych modeli, jeśli staną się dostępne.
