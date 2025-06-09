#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time, re
from ai.dialog.engine import DialogEngine

class LoreConsistencyTester:
    def __init__(self):
        self.engine = DialogEngine()
        self.test_results = []
        
    def test_character_knowledge(self, character, question, expected_keywords, topic):
        print(f"\nTESTING {character.upper()} - {topic}")
        print(f"Question: {question}")
        
        response = self.engine.get_npc_response(question, character, "lore_test")
        print(f"Response: {response}")
        
        response_lower = response.lower()
        found_keywords = [kw for kw in expected_keywords if kw.lower() in response_lower]
        is_generic = any(generic in response_lower for generic in [
            "what can i get", "what brings ye", "good day", "aye, what", 
            "indeed... most curious", "something has caught", "welcome, friend"
        ])
        
        score = 0
        feedback = []
        
        if found_keywords:
            score += 60
            feedback.append(f"Found lore elements: {', '.join(found_keywords)}")
        else:
            feedback.append("No lore elements detected")
            
        if not is_generic:
            score += 30
            feedback.append("Specific, contextual response")
        else:
            feedback.append("Generic/fallback response")
            
        if len(response.split()) >= 8:
            score += 10
            feedback.append("Adequate response length")
        else:
            feedback.append("Response too short")
            
        result = {
            'character': character,
            'question': question,
            'response': response,
            'topic': topic,
            'score': score,
            'feedback': feedback,
            'found_keywords': found_keywords,
            'is_generic': is_generic
        }
        
        self.test_results.append(result)
        
        print(f"Score: {score}/100")
        for fb in feedback:
            print(f"   {fb}")
            
        return result

    def test_memory_triggers(self):
        print("="*60)
        print("MEMORY FRAGMENTS TEST")
        print("Testing if characters use their memory fragments appropriately")
        print("="*60)
        
        tests = [
            {
                'character': 'tavern_keeper',
                'question': 'Have you seen Tomek lately?',
                'expected_keywords': ['tomek', 'good lad', 'beer', 'paid', 'home', 'come', 'missing', 'vanished'],
                'topic': 'Tomek memories'
            },
            {
                'character': 'tavern_keeper',
                'question': 'Tell me about the mine',
                'expected_keywords': ['mine', 'sounds', 'silver', 'strange', 'golden days', 'flowed'],
                'topic': 'Mine memories'
            },
            {
                'character': 'blacksmith',
                'question': 'What happened to your family?',
                'expected_keywords': ['brother', 'mine', 'pulley', 'rope', 'cut', 'never came back'],
                'topic': 'Brother memories'
            },
            {
                'character': 'blacksmith',
                'question': 'Tell me about that strange ore',
                'expected_keywords': ['ore', 'tomek', 'hissed', 'forge', 'shaped', 'want'],
                'topic': 'Strange ore memories'
            },
            {
                'character': 'mysterious_stranger',
                'question': 'What do you know about the mine?',
                'expected_keywords': ['silver', 'veins', 'natural', 'sealing', 'prison', 'ancient'],
                'topic': 'Ancient secrets'
            },
            {
                'character': 'merchant',
                'question': 'Where did you get these goods?',
                'expected_keywords': ['city', 'silver', 'stonehaven', 'paid well', 'whispers', 'night'],
                'topic': 'Suspicious goods'
            },
            {
                'character': 'tavern_regular',
                'question': 'Tell me about the disappearances',
                'expected_keywords': ['tomek', 'sweet boy', 'dragged', 'mine', 'stranger', 'blink'],
                'topic': 'Village gossip'
            }
        ]
        
        for test in tests:
            self.test_character_knowledge(**test)
            time.sleep(0.5)  

    def test_contextual_responses(self):
        print("\n" + "="*60)
        print("CONTEXTUAL RESPONSES TEST")
        print("Testing character reactions to specific topics")
        print("="*60)
        
        tests = [
            {
                'character': 'tavern_keeper',
                'question': 'What do you think about the Tawny Lion?',
                'expected_keywords': ['tawny lion', 'tavern', 'inn', 'years', 'run', 'mine'],
                'topic': 'Tavern knowledge'
            },
            {
                'character': 'tavern_regular',
                'question': 'What do you think about Erik?',
                'expected_keywords': ['erik', 'weird', 'gleam', 'eyes', 'cursed', 'junk', 'exotic'],
                'topic': 'Character opinions'
            },
            {
                'character': 'blacksmith',
                'question': 'Can you make me a sword?',
                'expected_keywords': ['blade', 'steel', 'forge', 'sing', 'survive', 'remember'],
                'topic': 'Craft knowledge'
            },
            {
                'character': 'mysterious_stranger',
                'question': 'What lurks in the darkness?',
                'expected_keywords': ['ancient', 'stir', 'prison', 'stones', 'scream', 'shadows'],
                'topic': 'Dark hints'
            },
            {
                'character': 'merchant',
                'question': 'What are your best wares?',
                'expected_keywords': ['special', 'city', 'distant', 'amulet', 'wards', 'evil'],
                'topic': 'Trading skills'
            }
        ]
        
        for test in tests:
            self.test_character_knowledge(**test)
            time.sleep(0.5)

    def test_character_consistency(self):
        print("\n" + "="*60)
        print("CHARACTER CONSISTENCY TEST") 
        print("Testing personality consistency across different questions")
        print("="*60)

        character = 'blacksmith'
        questions = [
            "Hello there!",
            "What's your trade?", 
            "Any news from the village?",
            "Can you help me?"
        ]
        
        responses = []
        for question in questions:
            print(f"\nBLACKSMITH")
            print(f"Question: {question}")
            response = self.engine.get_npc_response(question, character, f"consistency_test_{len(responses)}")
            print(f"Response: {response}")
            responses.append(response)
            time.sleep(0.5)

        combined_text = ' '.join(responses).lower()
        blacksmith_indicators = ['ye', 'aye', 'forge', 'steel', 'dammit', 'blade']
        found_indicators = [word for word in blacksmith_indicators if word in combined_text]
        
        consistency_score = (len(found_indicators) / len(blacksmith_indicators)) * 100
        
        print(f"\nConsistency Analysis:")
        print(f"   Found speech patterns: {', '.join(found_indicators)}")
        print(f"   Consistency score: {consistency_score:.1f}%")
        
        self.test_results.append({
            'character': character,
            'test_type': 'consistency',
            'score': consistency_score,
            'found_patterns': found_indicators,
            'responses': responses
        })

    def test_world_knowledge_integration(self):
        print("\n" + "="*60)
        print("WORLD KNOWLEDGE INTEGRATION TEST")
        print("Testing integration of world lore and current events")
        print("="*60)
        
        world_questions = [
            {
                'character': 'tavern_keeper',
                'question': 'What\'s happening in Stonehaven lately?',
                'expected_keywords': ['stonehaven', 'mine', 'noises', 'bandits', 'trails', 'disappeared'],
                'topic': 'Current events knowledge'
            },
            {
                'character': 'mysterious_stranger', 
                'question': 'Tell me about this village',
                'expected_keywords': ['stonehaven', 'mountain', 'silver', 'edge', 'world', 'ancient'],
                'topic': 'Village knowledge'
            },
            {
                'character': 'merchant',
                'question': 'How\'s business in these parts?',
                'expected_keywords': ['trade', 'travelers', 'bandits', 'mountain', 'trails', 'dangerous'],
                'topic': 'Economic situation'
            }
        ]
        
        for test in world_questions:
            self.test_character_knowledge(**test)
            time.sleep(0.5)

    def generate_report(self):
        print("\n" + "="*60)
        print("LORE CONSISTENCY REPORT")
        print("="*60)
        
        if not self.test_results:
            print("No test results to analyze")
            return
            
        scored_tests = [r for r in self.test_results if 'score' in r and 'topic' in r]
        
        if not scored_tests:
            print("No scored tests found")
            return
            
        total_score = sum(r['score'] for r in scored_tests)
        avg_score = total_score / len(scored_tests)
        
        print(f"OVERALL STATISTICS:")
        print(f"   Total tests: {len(scored_tests)}")
        print(f"   Average score: {avg_score:.1f}/100")
        print(f"   Total score: {total_score}/{len(scored_tests) * 100}")
        
        characters = {}
        for result in scored_tests:
            char = result['character']
            if char not in characters:
                characters[char] = []
            characters[char].append(result['score'])
            
        print(f"\n SCORES BY CHARACTER:")
        for char, scores in characters.items():
            avg = sum(scores) / len(scores)
            print(f"   {char}: {avg:.1f}/100 (tests: {len(scores)})")
            
        scored_tests.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n BEST PERFORMANCES:")
        for result in scored_tests[:3]:
            print(f"   {result['character']} - {result['topic']}: {result['score']}/100")
            if result['found_keywords']:
                print(f"      Keywords: {', '.join(result['found_keywords'])}")
                
        print(f"\n NEEDS IMPROVEMENT:")
        for result in scored_tests[-3:]:
            print(f"   {result['character']} - {result['topic']}: {result['score']}/100")
  
        lore_usage = sum(1 for r in scored_tests if r['found_keywords'])
        lore_percentage = (lore_usage / len(scored_tests)) * 100
        
        print(f"\n LORE UTILIZATION:")
        print(f"   Tests with lore elements: {lore_usage}/{len(scored_tests)} ({lore_percentage:.1f}%)")
        
        print(f"\n RECOMMENDATIONS:")
        if avg_score < 50:
            print("System needs major improvements in lore integration")
        elif avg_score < 70:
            print("System shows promise but needs refinement")
        else:
            print("System demonstrates good lore consistency")
            
        if lore_percentage < 50:
            print("Improve memory fragment utilization in responses")
        if any(r['is_generic'] for r in scored_tests):
            print("Reduce generic fallback responses")
            
        return {
            'total_tests': len(scored_tests),
            'average_score': avg_score,
            'lore_utilization': lore_percentage,
            'character_scores': {char: sum(scores)/len(scores) for char, scores in characters.items()}
        }

def main():
    print("DIALOG ENGINE - LORE CONSISTENCY TESTER")
    print("Testing character depth and world knowledge integration")
    print("="*60)
    
    tester = LoreConsistencyTester()
    tester.test_memory_triggers()
    tester.test_contextual_responses() 
    tester.test_character_consistency()
    tester.test_world_knowledge_integration()
    
    report = tester.generate_report()
    
    print(f"\nLORE CONSISTENCY TEST COMPLETED!")
    print(f"Final Score: {report['average_score']:.1f}/100" if report else "Test failed")
    print("="*60)

if __name__ == "__main__":
    main()
