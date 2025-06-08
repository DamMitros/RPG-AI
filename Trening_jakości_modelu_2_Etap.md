# Trening Jakości Modelu - II Etap: Wprowadzenie Systemu Treningu i Oceny Jakości

## Idea/Zamysł II Etapu
Drugi etap to dalsze ulepszanie Dialog Engine. Model ma lepiej **udawać średniowiecznego mieszkańca**, chce to osiągnąc przez zautomatyzowany test jakość. Realizacja poprzez:
- Wprowadzenie systemu, który samodzielnie trenuje model i ocenia jego jakość.
- Rozbudowujemy testy, żeby postacie były bardziej spójne.
- Uczymy model, żeby **nie używał współczesnych słów**.
- Optymalizację parametrów modelu dla najlepszej autentyczności dialogów

## Cele II Etapu

### 1. **Automatyczny Trening Modeli**
**Cel:** Stworzenie podstawowego narzędzia do automatycznego testowania i oceny jakości generowanych dialogów.
- Zaprojektowanie i wprowadzenie koncepcji Scenariuszy Testowych.
- Definicja i implementacja wieloaspektowych Metryk Jakości.
- Stworzenie możliwości testowania pojedynczych zestawów parametrów (`Single Parameter Testing`)

### 2. **Wzmocnienie Immersji Fantasy**
**Cel:** Zapewnienie że model konsekwentnie zachowuje się jak mieszkaniec średniowiecznego świata
- **Mechanizm Odrzucania Nowoczesności:** Automatyczne zastępowanie współczesnych terminów sformułowaniami w stylu "[heretical nonsense]".
- **Wzmocnienie Tożsamości Postaci:** Każda postać ma unikalne wzorce mowy i fragmenty wspomnień.
- **Konsystencja Świata:** Model zawsze musi pamiętać, że jest w Stonehaven.

### 3. **Ocena Jakości**
**Cel:** Obiektywna ocena jakości generowanych dialogów

## Implementacja Systemu Treningu

### Struktura Systemu

```
RPGDialogTrainer
├── Scenariusze Testowe (Test Scenarios)
│   ├── Medieval Atmosphere Test
│   ├── Modern Tech Rejection Test
│   ├── Character Consistency Test
│   └── Local Lore Test
├── Metryki Jakości (Quality Metrics)
│   ├── Fantasy Immersion Score (25%)
│   ├── Character Authenticity (30%)
│   ├── Medieval Consistency (25%)
│   ├── Response Length Score (10%)
│   └── Dialogue Naturalness (10%)
└── Optymalizacja Parametrów
    └── Single Parameter Testing
```

### Kluczowe Scenariusze Testowe

#### **1. Medieval Atmosphere Test**
**Postać:** Tavern Keeper (Bartek Mug)  
**Cel:** Sprawdzenie czy model naturalnie wchodzi w atmosferę średniowieczną

**Przykładowe pytania:**
- "Opowiedz mi o kopalni"
- "Co słychać w miasteczku?"
- "Słyszałem o zaginięciach"

**Oczekiwane elementy:** mine, silver, Tomek, tavern, village  
**Zabronione elementy:** computer, internet, phone, AI, technology

#### **2. Modern Tech Rejection Test**
**Postać:** Blacksmith (Anja Ironbite)  
**Cel:** Test odrzucania współczesnych technologii

**Przykładowe pytania:**
- "Czy masz telefon?"
- "Możesz sprawdzić w internecie?"
- "Czy znasz AI?"

**Oczekiwane reakcje:** heretical, nonsense, strange, mad, bizarre  
**Zabronione reakcje:** yes, sure, akceptacja nowoczesnych terminów

#### **3. Character Consistency Test**
**Postać:** Mysterious Stranger  
**Cel:** Sprawdzenie czy model zachowuje unikalną osobowość postaci

**Wzorce charakteru:**
- Kończy zdania wielokropkiem "..."
- Mówi zagadkami
- Odnosi się do cieni i sekretów

### Metryki Jakości (Szczegółowo)

#### **1. Fantasy Immersion Score (25% wagi)**
Sprawdza obecność słów związanych z fantasy:
- **Słowa kluczowe:** mine, tavern, silver, quest, adventure, blade, forge, magic, curse, shadow, whisper, ancient
- **Obliczenie:** min(liczba_słów_fantasy / 3, 1.0)
- **Cel:** Zapewnienie że dialogi brzmi autentycznie w kontekście fantasy

#### **2. Character Authenticity (30% wagi)**
Najważniejsza metryka - sprawdza czy postać zachowuje się zgodnie z charakterystyką:
- **Elementy oczekiwane:** Specyficzne dla każdej postaci (np. zakończenia "..." dla Mysterious Stranger)
- **Elementy zabronione:** Niepasujące do charakteru (np. jasne odpowiedzi od tajemniczej postaci)
- **Obliczenie:** (elementy_oczekiwane / max_oczekiwane) - (elementy_zabronione × 0.5)

#### **3. Medieval Consistency (25% wagi)**
Kluczowa dla immersji - penalizuje jakiekolwiek nowoczesne odniesienia:
- **Słowa penalizowane:** computer, internet, phone, TV, AI, robot, electricity, camera, video, technology
- **Obliczenie:** max(0, 1.0 - (liczba_nowoczesnych_słów × 0.3))
- **Cel:** Zagwarantowanie że postaci nigdy nie wyjdą z roli średniowiecznych mieszkańców

#### **4. Response Length Score (10% wagi)**
Zapewnia odpowiednią długość dialogów RPG:
- **Idealna długość:** 5-25 słów
- **Penalty za zbyt krótkie:** < 5 słów
- **Penalty za zbyt długie:** > 25 słów

#### **5. Dialogue Naturalness (10% wagi)**
Sprawdza naturalność i płynność dialogu:
- **Wskaźniki naturalności:** Interpunkcja, spójniki, naturalne przejścia
- **Cel:** Unikanie "robotycznych" odpowiedzi

## Podsumowanie II Etapu

Drugi etap wprowadza **framework do automatycznego testowania i oceny jakości** generowanych dialogów. Zdefiniowano kluczowe metryki i scenariusze testowe, a także zidentyfikowano wstępne problemy, które będą celem szczegółowej optymalizacji w kolejnych fazach:
- **Zbyt agresywne wykrywanie nowoczesności:** System czasami błędnie wykrywa w inputach elementy nowoczesności.
- **Średniowieczny charakter wypowiedzi:** Model używa czasami nadwyraz współczesne wyrażenia
- **Zbyt ogólne odpowiedzi:** Modelowi zdaża się dawać standardowe odpowiedzi (ignorując input?)
- **Słaba pamieć:** Wspomnienia postaci nie są używane w dialogach

## Efekt końcowy:
Dialog Engine zyskał podstawowy framework do automatycznego treningu i oceny, co pozwoliło na dalszą diagnozę obszarów wymagających poprawy.

## Dalsze założenia:
Kolejny etap skupi się na dopracowaniu ustawień, poprawie autentyczności postaci.