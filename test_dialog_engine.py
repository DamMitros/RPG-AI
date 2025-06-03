#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, time
from ai.dialog_engine import DialogEngine
from ai.conversation_tracker import conversation_tracker

def test_fantasy_immersion():
    print("TEST 1: Fantasy Immersion Test")
    print("=" * 50)
    
    engine = DialogEngine()
    test_scenarios = [
        {
            "character": "tavern_keeper",
            "message": "Tell me about the mines",
            "player_stats": {"level": 3, "location": "tavern", "gold": 50},
            "expected_keywords": ["mine", "silver", "dangerous", "Tomek"]
        },
        {
            "character": "mysterious_stranger", 
            "message": "Who are you?",
            "player_stats": {"level": 1, "location": "tavern", "gold": 10},
            "expected_keywords": ["stranger", "traveler", "..."]
        },
        {
            "character": "merchant",
            "message": "Have you seen Tomek?",
            "player_stats": {"level": 2, "location": "shop", "gold": 25},
            "expected_keywords": ["Tomek", "missing", "trader", "worried"]
        }
    ]
    
    session_id = "fantasy_test"
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n--- Scenario {i+1}: {scenario['character']} ---")
        print(f"User: {scenario['message']}")
        
        response = engine.get_npc_response(
            user_input=scenario['message'],
            character=scenario['character'],
            session_id=session_id,
            player_stats=scenario['player_stats']
        )
        
        print(f"NPC: {response}")
        
        fantasy_score = 0
        for keyword in scenario['expected_keywords']:
            if keyword.lower() in response.lower():
                fantasy_score += 1
        
        print(f"Fantasy elements found: {fantasy_score}/{len(scenario['expected_keywords'])}")
        time.sleep(1)
    
    return session_id

def test_conversation_tracking():
    print("\n TEST 2: Conversation Tracking Test")  
    print("=" * 50)
    
    engine = DialogEngine()
    session_id = "tracking_test"

    conversations = [
        ("tavern_keeper", "What news from the village?", {"level": 1, "location": "tavern", "gold": 15}),
        ("tavern_keeper", "Tell me about Erik the merchant", {"level": 1, "location": "tavern", "gold": 15}),
        ("mysterious_stranger", "Who goes there?", {"level": 1, "location": "tavern", "gold": 15}),
        ("merchant", "The mine is cursed, isn't it?", {"level": 2, "location": "shop", "gold": 20})
    ]
    
    for character, message, stats in conversations:
        print(f"\nTesting {character}: {message}")
        response = engine.get_npc_response(message, character, session_id, stats)
        print(f"Response: {response}")
    
    stats = engine.get_conversation_stats(session_id)
    print(f"\n📈 Conversation Statistics:")
    print(f"Total interactions: {stats.get('total_interactions', 0)}")
    print(f"Average response time: {stats.get('avg_response_time', 0):.2f}s")
    print(f"Character consistency: {stats.get('character_consistency', 0):.2f}")
    print(f"Fantasy immersion score: {stats.get('fantasy_immersion', 0):.2f}")
    
    return session_id

def test_character_consistency():
    print("\n TEST 3: Character Consistency Test")
    print("=" * 50)
    
    engine = DialogEngine()
    session_id = "consistency_test"

    character = "tavern_keeper"
    messages = [
        "How's business?",
        "What do you serve here?", 
        "Any rooms available?",
        "Tell me gossip",
        "Know anything about the mines?"
    ]
    
    player_stats = {"level": 1, "location": "tavern", "gold": 30}
    
    responses = []
    for msg in messages:
        print(f"\nUser: {msg}")
        response = engine.get_npc_response(msg, character, session_id, player_stats)
        print(f"Tavern Keeper: {response}")
        responses.append(response)
        time.sleep(0.5)
    
    print(f"\n🔍 Consistency Analysis:")
    print(f"Total responses: {len(responses)}")
    
    common_words = ["tavern", "ale", "patron", "drink", "gold"]
    consistency_score = 0
    
    for response in responses:
        for word in common_words:
            if word.lower() in response.lower():
                consistency_score += 1
                
    print(f"Consistency indicators found: {consistency_score}")
    
    return session_id

def test_error_handling():
    print("\n TEST 4: Error Handling Test")
    print("=" * 50)
    
    engine = DialogEngine()
    
    print("Testing non-existent character...")
    response = engine.get_npc_response("Hello", "non_existent_character")
    print(f"Response: {response}")
    
    print("\nTesting very long message...")
    long_message = "Tell me " + "everything " * 50 + "about this place."
    response = engine.get_npc_response(long_message, "tavern_keeper")
    print(f"Response length: {len(response)} characters")
    print(f"Response: {response[:100]}...")

def generate_quality_report():
    print("\n📋 FINAL QUALITY REPORT")
    print("=" * 50)
    
    engine = DialogEngine()
    report = engine.get_quality_report()
    
    print("Global Conversation Quality Report:")
    print(f"Sessions analyzed: {report.get('total_sessions', 0)}")
    print(f"Total interactions: {report.get('total_interactions', 0)}")
    print(f"Average fantasy immersion: {report.get('avg_fantasy_immersion', 0):.2f}/10")
    print(f"Average character consistency: {report.get('avg_character_consistency', 0):.2f}/10") 
    print(f"Response quality: {report.get('response_quality', 0):.2f}/10")

    if 'common_issues' in report:
        print(f"\nCommon Issues:")
        for issue in report['common_issues'][:3]:
            print(f"- {issue}")

def main():
    print("RPG-AI Dialog Engine Enhanced Test Suite")
    print("Testing fantasy immersion and conversation tracking...")
    print("=" * 60)
    
    try:
        test_fantasy_immersion()
        test_conversation_tracking() 
        test_character_consistency()
        test_error_handling()
        generate_quality_report()
        
        print("\n All tests completed successfully!")
        print("Check conversation logs for detailed quality metrics.")
        
    except Exception as e:
        print(f"\n Test failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
