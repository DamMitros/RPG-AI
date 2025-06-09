#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ai.dialog.engine import DialogEngine
import time

def print_separator():
    print("=" * 60)

def print_demo_header(title):
    print(f"\n{title}")
    print("-" * 40)

def demonstrate_character_consistency():
    print_demo_header("CHARACTER CONSISTENCY TEST")
    engine = DialogEngine()
    characters = [
        ("tavern_keeper", "Tell me about the mine"),
        ("blacksmith", "I need a weapon"), 
        ("mysterious_stranger", "What do you know about the disappearances?"),
        ("merchant", "What are you selling?")
    ]
    
    for character, question in characters:
        print(f"\n{character.upper().replace('_', ' ')}")
        print(f"[Question]: {question}")
        
        response = engine.get_npc_response(
            user_input=question,
            character=character,
            session_id=f"demo_{character}"
        )
        
        print(f"[Response]: {response}")
        time.sleep(1)

def demonstrate_modern_tech_rejection():
    print_demo_header("MODERN TECHNOLOGY REJECTION TEST")
    engine = DialogEngine()
    modern_questions = [
        "Do you have a phone?",
        "Can you check the internet?", 
        "Turn on the TV",
        "Do you know about AI?",
        "Take a photo with your camera"
    ]
    
    character = "blacksmith"  
    
    for question in modern_questions:
        print(f"\n [Question]: {question}")
        
        response = engine.get_npc_response(
            user_input=question,
            character=character,
            session_id="demo_modern_rejection"
        )
        
        print(f"[Anja's response]: {response}")

        if any(word in response.lower() for word in ['heretical', 'nonsense', 'strange', 'mad']):
            print("Modern tech properly rejected!")
        else:
            print("Modern tech not properly handled")
        
        time.sleep(1)

def demonstrate_world_knowledge():
    print_demo_header("WORLD KNOWLEDGE TEST")
    engine = DialogEngine()
    lore_questions = [
        ("tavern_keeper", "What happened to Tomek?"),
        ("tavern_regular", "Tell me about Stonehaven"),
        ("merchant", "What's happening in the village?"),
        ("mysterious_stranger", "What lurks in the mine?")
    ]
    
    for character, question in lore_questions:
        print(f"\n{character.upper().replace('_', ' ')}")
        print(f"[Question]: {question}")
        
        response = engine.get_npc_response(
            user_input=question,
            character=character,
            session_id=f"demo_lore_{character}"
        )
        
        print(f"[Response]: {response}")
        
        lore_keywords = ['Tomek', 'mine', 'Stonehaven', 'silver', 'Erik', 'stranger']
        found_keywords = [kw for kw in lore_keywords if kw.lower() in response.lower()]
        
        if found_keywords:
            print(f"Lore elements found: {', '.join(found_keywords)}")
        else:
            print("No lore elements detected")
        
        time.sleep(1)

def demonstrate_conversation_tracking():
    print_demo_header("CONVERSATION TRACKING DEMO")
    engine = DialogEngine()
    session_id = "demo_tracking"

    conversation = [
        "Hello, innkeeper!",
        "What's the situation with the mine?", 
        "Have you seen Tomek recently?",
        "What do you think about the stranger in the corner?"
    ]
    
    print("Having a conversation with the tavern keeper...")
    
    for i, message in enumerate(conversation, 1):
        print(f"\n{i}. Player: {message}")
        
        response = engine.get_npc_response(
            user_input=message,
            character="tavern_keeper",
            session_id=session_id
        )
        
        print(f"   Bartek: {response}")
        time.sleep(1)

    print(f"\nConversation Statistics:")
    stats = engine.get_conversation_stats(session_id)
    print(f"   Total interactions: {stats.get('total_interactions', 0)}")
    print(f"   Average response time: {stats.get('avg_response_time', 0):.2f}s")
    
    quality_report = engine.get_quality_report(session_id)
    if quality_report:
        print(f"   Quality Metrics:")
        print(f"   Fantasy immersion: {quality_report.get('fantasy_score', 0):.1%}")
        print(f"   Character consistency: {quality_report.get('character_score', 0):.1%}")
def main():
    print_separator()
    print("DIALOG ENGINE - DEMONSTRATION")
    print("RPG Medieval Village Setting")
    print_separator()
    
    print("\nThis demo showcases:")
    print("Character consistency and unique personalities")
    print("Automatic rejection of modern technology")
    print("Deep knowledge of the game world (Stonehaven)")
    print("Conversation tracking and quality metrics")
    print("Medieval atmosphere immersion")
    
    input("\nPress Enter to start the demonstration...")
    
    try:
        demonstrate_character_consistency()        
        input("\nPress Enter to continue to modern tech rejection test...")
 
        demonstrate_modern_tech_rejection()
        input("\nPress Enter to continue to world knowledge test...")

        demonstrate_world_knowledge()
        input("\nPress Enter to continue to conversation tracking demo...")

        demonstrate_conversation_tracking()        
        print_separator()
        print("DEMONSTRATION COMPLETED!")
        print("To optimize parameters, run: python trening.py")
        print("To try interactive mode, run: python app.py and cd frontend; npm run dev")
        print_separator()
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo error: {e}")

if __name__ == "__main__":
    main()