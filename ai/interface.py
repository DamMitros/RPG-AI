from ai.dialog_engine import DialogEngine

dialog_engine = DialogEngine()

def get_npc_response(user_input, character="tavern_keeper", session_id="default"):
    return dialog_engine.get_npc_response(user_input, character, session_id)

def reset_conversation(session_id="default"):
    dialog_engine.reset_conversation(session_id)