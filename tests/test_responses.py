#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.dialog.engine import DialogEngine

def test_improved_responses():
    print("=== Test Odpowiedzi Dialog Engine ===\n")

    engine = DialogEngine()
    scenarios = [
        ("Hello, what do you do here?", "blacksmith"),
        ("What ales do you have?", "tavern_keeper"),
        ("Tell me about this village", "mysterious_stranger"),
        ("What goods do you sell?", "merchant"),
        
        ("Do you have a computer?", "blacksmith"),
        ("Can I use your WiFi?", "tavern_keeper"),
        ("Have you seen any robots?", "mysterious_stranger"),
        ("Do you accept credit cards?", "merchant"),

        ("What happened to the missing villagers?", "blacksmith"),
        ("Is there a quest I could undertake?", "tavern_keeper"),
        ("What secrets does this village hide?", "mysterious_stranger"),
    ]
    
    session_id = "test_session"
    
    for i, (question, character) in enumerate(scenarios, 1):
        print(f"\n--- Test {i}: {character.upper()} ---")
        print(f"Q: {question}")
        
        response = engine.get_npc_response(
            user_input=question,
            character=character,
            session_id=session_id
        )
        
        print(f"A: {response}")

        issues = []
        if len(response) < 10:
            issues.append("Odpowiedź zbyt krótka")
        if "Player:" in response or "User:" in response:
            issues.append("Zawiera znaczniki dialogowe")
        if any(word in response.lower() for word in ["computer", "wifi", "robot", "credit"]):
            issues.append("Zawiera współczesne słowa")
        if not response.endswith(('.', '!', '?', '...')):
            issues.append("Brak zakończenia zdania")
            
        if issues:
            print(f"Problemy: {', '.join(issues)}")
        else:
            print("Odpowiedź prawidłowa")
    
    print(f"\n=== Test zakończony ===")

if __name__ == "__main__":
    test_improved_responses()
