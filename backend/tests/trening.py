# -*- coding: utf-8 -*-

import json, yaml, time, logging, itertools
from datetime import datetime
from typing import Dict, List, Tuple, Any
from ai.dialog.engine import DialogEngine
from ai.dialog.tracker import ConversationTracker

class RPGDialogTrainer:
    def __init__(self):
        self.engine = DialogEngine()
        self.tracker = ConversationTracker()
        self.training_session_id = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.setup_logging()
        self.test_scenarios = self.load_test_scenarios()
        self.parameter_space = {
            'temperature': [0.3, 0.5, 0.7, 0.9],
            'top_k': [10, 20, 30, 50],
            'top_p': [0.6, 0.8, 0.9, 0.95],
            'repetition_penalty': [1.2, 1.5, 1.8, 2.0],
            'max_new_tokens': [30, 50, 80, 100]
        }
        
        self.best_params = None
        self.best_score = 0
        self.training_results = []

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'trening_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_test_scenarios(self) -> List[Dict]:
        return [
            {
                'name': 'medieval_atmosphere_test',
                'description': 'Test zachowania postaci w kontekście średniowiecznym',
                'inputs': [
                    "Tell me about the mine",
                    "What's happening in town?", 
                    "Have you seen anyone suspicious?",
                    "I need weapons",
                    "I heard about disappearances"
                ],
                'character': 'tavern_keeper',
                'expected_elements': ['mine', 'silver', 'Tomek', 'tavern', 'village'],
                'forbidden_elements': ['computer', 'internet', 'phone', 'AI', 'technology']
            },
            {
                'name': 'modern_tech_rejection_test',
                'description': 'Test odrzucania nowoczesnych technologii',
                'inputs': [
                    "Do you have a phone?",
                    "Can you check the internet?",
                    "Turn on the TV",
                    "Take a picture with your phone",
                    "Do you know about AI?"
                ],
                'character': 'blacksmith',
                'expected_elements': ['heretical', 'nonsense', 'strange', 'mad', 'bizarre'],
                'forbidden_elements': ['yes', 'sure', 'phone', 'computer', 'internet']
            },
            {
                'name': 'character_consistency_test',
                'description': 'Test spójności osobowości postaci',
                'inputs': [
                    "Who are you?",
                    "What do you do?", 
                    "What's your story?",
                    "What do you fear?",
                    "What do you think about the mine?"
                ],
                'character': 'mysterious_stranger',
                'expected_elements': ['...', 'shadows', 'secrets', 'depths', 'whisper'],
                'forbidden_elements': ['clearly', 'obviously', 'definitely']
            },
            {
                'name': 'local_lore_test',
                'description': 'Test znajomości lokalnej tradycji i wydarzeń',
                'inputs': [
                    "What do you know about Tomek?",
                    "Tell me about the mine's history",
                    "Who is this mysterious stranger?",
                    "What does Erik sell?",
                    "Is the mine safe?"
                ],
                'character': 'tavern_regular',
                'expected_elements': ['Tomek', 'mine', 'Erik', 'stranger', 'Stonehaven'],
                'forbidden_elements': ['dunno', "don't know", 'whatever']
            }
        ]

    def evaluate_response_quality(self, response: str, scenario: Dict) -> Dict[str, float]:
        scores = {}
        
        fantasy_words = ['mine', 'tavern', 'silver', 'quest', 'adventure', 'blade', 
                        'forge', 'magic', 'curse', 'shadow', 'whisper', 'ancient']
        fantasy_count = sum(1 for word in fantasy_words if word.lower() in response.lower())
        scores['fantasy_immersion'] = min(fantasy_count / 3, 1.0)
        
        expected_found = sum(1 for elem in scenario['expected_elements'] 
                           if elem.lower() in response.lower())
        forbidden_found = sum(1 for elem in scenario['forbidden_elements'] 
                            if elem.lower() in response.lower())
        
        scores['character_authenticity'] = max(0, 
            (expected_found / len(scenario['expected_elements'])) - 
            (forbidden_found * 0.5))
        
        modern_tech_words = ['computer', 'internet', 'phone', 'TV', 'AI', 'robot', 
                           'electricity', 'camera', 'video', 'technology']
        modern_penalty = sum(1 for word in modern_tech_words 
                           if word.lower() in response.lower())
        scores['medieval_consistency'] = max(0, 1.0 - (modern_penalty * 0.3))

        length = len(response.split())
        if 5 <= length <= 25:  
            scores['length_score'] = 1.0
        elif length < 5:
            scores['length_score'] = length / 5
        else:
            scores['length_score'] = max(0, 1.0 - ((length - 25) / 25))
        
        naturalness_indicators = ['.', '!', '?', ',', 'but', 'so', 'however', 'because']
        naturalness_count = sum(1 for indicator in naturalness_indicators 
                              if indicator in response.lower())
        scores['naturalness'] = min(naturalness_count / 4, 1.0)

        weights = {
            'fantasy_immersion': 0.25,
            'character_authenticity': 0.30,
            'medieval_consistency': 0.25,
            'length_score': 0.10,
            'naturalness': 0.10
        }
        
        total_score = sum(scores[key] * weights[key] for key in weights)
        scores['total_score'] = total_score
        
        return scores

    def test_parameter_set(self, params: Dict) -> float:
        self.logger.info(f"Testowanie parametrów: {params}")

        original_params = self.backup_engine_params()
        self.apply_params_to_engine(params)
        
        total_score = 0
        scenario_count = 0
        detailed_results = []
        
        try:
            for scenario in self.test_scenarios:
                scenario_scores = []
                
                for input_text in scenario['inputs']:
                    session_id = f"{self.training_session_id}_{scenario['name']}_{scenario_count}"
                    response = self.engine.get_npc_response(
                        user_input=input_text,
                        character=scenario['character'],
                        session_id=session_id
                    )
                    
                    scores = self.evaluate_response_quality(response, scenario)
                    scenario_scores.append(scores['total_score'])
                    
                    detailed_results.append({
                        'scenario': scenario['name'],
                        'input': input_text,
                        'response': response,
                        'scores': scores,
                        'params': params.copy()
                    })
                    
                    time.sleep(0.1) 

                avg_scenario_score = sum(scenario_scores) / len(scenario_scores)
                total_score += avg_scenario_score
                scenario_count += 1
                
                self.logger.info(f"Scenariusz {scenario['name']}: {avg_scenario_score:.3f}")
        
        finally:
            self.restore_engine_params(original_params)
        
        final_score = total_score / scenario_count if scenario_count > 0 else 0
        self.training_results.append({
            'params': params,
            'score': final_score,
            'detailed_results': detailed_results,
            'timestamp': datetime.now().isoformat()
        })
        
        return final_score

    def backup_engine_params(self) -> Dict:
        return self.engine.get_generation_params()

    def apply_params_to_engine(self, params: Dict):
        self.engine.set_generation_params(**params)
        self.logger.info(f"Applying params: {params}")

    def restore_engine_params(self, params: Dict):
        self.engine.set_generation_params(**params)
        self.logger.info(f"Restoring original params: {params}")

    def grid_search_optimization(self) -> Dict:
        self.logger.info("Rozpoczynanie Grid Search optymalizacji...")
        
        param_names = list(self.parameter_space.keys())
        param_values = list(self.parameter_space.values())
        
        total_combinations = 1
        for values in param_values:
            total_combinations *= len(values)
        
        self.logger.info(f"Testowanie {total_combinations} kombinacji parametrów...")
        
        best_score = 0
        best_params = None
        combination_count = 0
        
        for combination in itertools.product(*param_values):
            combination_count += 1
            params = dict(zip(param_names, combination))
            
            self.logger.info(f"Kombinacja {combination_count}/{total_combinations}")
            
            try:
                score = self.test_parameter_set(params)
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                    self.logger.info(f"Nowy najlepszy wynik: {best_score:.3f} z parametrami: {best_params}")
                
            except Exception as e:
                self.logger.error(f"Błąd podczas testowania parametrów {params}: {e}")
                continue
        
        self.best_params = best_params
        self.best_score = best_score
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'total_tested': combination_count
        }

    def run_focused_training(self, focus_areas: List[str] = None) -> Dict:
        if focus_areas is None:
            focus_areas = ['medieval_consistency', 'character_authenticity']
        
        self.logger.info(f"Uruchamianie treningu skupionego na: {focus_areas}")

        focused_scenarios = []
        for scenario in self.test_scenarios:
            if any(area in scenario['name'] for area in focus_areas):
                focused_scenarios.append(scenario)
        
        if not focused_scenarios:
            focused_scenarios = self.test_scenarios

        focused_param_space = {
            'temperature': [0.5, 0.7],
            'top_k': [20, 30],
            'repetition_penalty': [1.5, 1.8]
        }
        
        self.logger.info("Przeprowadzanie skupionej optymalizacji...")
        
        best_score = 0
        best_params = None
        
        for temp in focused_param_space['temperature']:
            for top_k in focused_param_space['top_k']:
                for rep_penalty in focused_param_space['repetition_penalty']:
                    params = {
                        'temperature': temp,
                        'top_k': top_k,
                        'top_p': 0.8, 
                        'repetition_penalty': rep_penalty,
                        'max_new_tokens': 50  
                    }

                    original_scenarios = self.test_scenarios
                    self.test_scenarios = focused_scenarios
                    
                    try:
                        score = self.test_parameter_set(params)
                        if score > best_score:
                            best_score = score
                            best_params = params.copy()
                    finally:
                        self.test_scenarios = original_scenarios
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'focus_areas': focus_areas
        }

    def generate_training_report(self) -> Dict:
        if not self.training_results:
            return {"error": "Brak wyników treningu do analizy"}

        scores = [result['score'] for result in self.training_results]
        
        report = {
            'training_session': self.training_session_id,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(self.training_results),
                'best_score': max(scores),
                'worst_score': min(scores),
                'average_score': sum(scores) / len(scores),
                'best_params': self.best_params
            },
            'scenario_analysis': self.analyze_scenario_performance(),
            'parameter_impact': self.analyze_parameter_impact(),
            'recommendations': self.generate_recommendations()
        }
        
        report_filename = f"training_report_{self.training_session_id}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Raport zapisany do: {report_filename}")
        return report

    def analyze_scenario_performance(self) -> Dict:
        scenario_scores = {}
        
        for result in self.training_results:
            for detail in result['detailed_results']:
                scenario = detail['scenario']
                if scenario not in scenario_scores:
                    scenario_scores[scenario] = []
                scenario_scores[scenario].append(detail['scores']['total_score'])
        
        analysis = {}
        for scenario, scores in scenario_scores.items():
            analysis[scenario] = {
                'average_score': sum(scores) / len(scores),
                'best_score': max(scores),
                'worst_score': min(scores),
                'sample_count': len(scores)
            }
        
        return analysis

    def analyze_parameter_impact(self) -> Dict:
        impact_analysis = {}
        
        for param_name in self.parameter_space.keys():
            param_scores = {}
            
            for result in self.training_results:
                param_value = result['params'].get(param_name)
                if param_value is not None:
                    if param_value not in param_scores:
                        param_scores[param_value] = []
                    param_scores[param_value].append(result['score'])

            value_averages = {}
            for value, scores in param_scores.items():
                value_averages[value] = sum(scores) / len(scores)
            
            impact_analysis[param_name] = {
                'value_averages': value_averages,
                'best_value': max(value_averages, key=value_averages.get) if value_averages else None
            }
        
        return impact_analysis

    def generate_recommendations(self) -> List[str]:
        recommendations = []
        
        if self.best_score < 0.6:
            recommendations.append("Wyniki poniżej 60% - rozważ rozszerzenie bazy wiedzy o świecie gry")
        
        if self.best_params:
            if self.best_params.get('temperature', 0) > 0.8:
                recommendations.append("Wysoka temperatura może powodować niespójne odpowiedzi")
            
            if self.best_params.get('repetition_penalty', 0) > 2.0:
                recommendations.append("Bardzo wysoka repetition_penalty może ograniczać naturalność dialogu")
        
        recommendations.append("Regularne testowanie na nowych scenariuszach pomoże utrzymać jakość")
        
        return recommendations

    def save_best_configuration(self):
        if self.best_params:
            config = {
                'best_parameters': self.best_params,
                'best_score': self.best_score,
                'training_session': self.training_session_id,
                'timestamp': datetime.now().isoformat(),
                'notes': 'Automatycznie wygenerowane przez system treningu'
            }
            
            filename = f"best_config_{self.training_session_id}.yaml"
            with open(filename, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"Najlepsza konfiguracja zapisana do: {filename}")


def main():
    print("=== SYSTEM TRENINGU DIALOG ENGINE v2.0 ===")
    print("Trening dla średniowiecznej gry RPG")
    print("=" * 50)
    
    trainer = RPGDialogTrainer()
    
    try:
        print("\nDostępne opcje treningu:")
        print("1. Pełny Grid Search (czasochłonne)")
        print("2. Trening skupiony (szybszy)")
        print("3. Test pojedynczego zestawu parametrów")
        
        choice = input("\nWybierz opcję (1-3): ").strip()
        
        if choice == "1":
            print("\nUruchamianie pełnego Grid Search...")
            results = trainer.grid_search_optimization()
            print(f"\nNajlepsze parametry: {results['best_params']}")
            print(f"Najlepszy wynik: {results['best_score']:.3f}")
            
        elif choice == "2":
            focus_areas = input("\nPodaj obszary fokusa (oddzielone przecinkami) lub Enter dla domyślnych: ").strip()
            if focus_areas:
                focus_list = [area.strip() for area in focus_areas.split(',')]
            else:
                focus_list = None
            
            print("\nUruchamianie treningu skupionego...")
            results = trainer.run_focused_training(focus_list)
            print(f"\nNajlepsze parametry: {results['best_params']}")
            print(f"Najlepszy wynik: {results['best_score']:.3f}")
            
        elif choice == "3":
            print("\nTestowanie domyślnych parametrów...")
            default_params = {
                'temperature': 0.6,
                'top_k': 20,
                'top_p': 0.8,
                'repetition_penalty': 1.8,
                'max_new_tokens': 50
            }
            score = trainer.test_parameter_set(default_params)
            print(f"\nWynik dla domyślnych parametrów: {score:.3f}")
            
        else:
            print("Nieprawidłowa opcja!")
            return
        
        print("\nGenerowanie raportu...")
        report = trainer.generate_training_report()

        trainer.save_best_configuration()
        
        print(f"\nTrening zakończony!")
        print(f"Raport dostępny w: training_report_{trainer.training_session_id}.json")
        
    except KeyboardInterrupt:
        print("\n\nTrening przerwany przez użytkownika")
    except Exception as e:
        print(f"\nBłąd podczas treningu: {e}")
        trainer.logger.error(f"Krytyczny błąd: {e}")


if __name__ == "__main__":
    main()