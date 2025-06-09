import json, os
from datetime import datetime
from collections import Counter

class ConversationTracker:
  def __init__(self, log_file="data/conversation_logs.json"):
    self.log_file = log_file
    self.ensure_directory()
    
  def ensure_directory(self):
    os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    if not os.path.exists(self.log_file):
      with open(self.log_file, 'w') as f:
        json.dump([], f)

  def log_interaction(self, user_input, bot_response, character, session_id, player_stats=None, location="unknown", error=None):
    try:
      with open(self.log_file, 'r') as f:
        logs = json.load(f)
    except:
      logs = []

    if player_stats and 'location' in player_stats:
      location = player_stats['location']
      
    log_entry = {
      "timestamp": datetime.now().isoformat(),
      "session_id": session_id,
      "location": location,
      "character": character,
      "user_input": user_input,
      "bot_response": bot_response,
      "player_stats": player_stats or {},
      "response_length": len(bot_response),
      "input_length": len(user_input),
      "has_error": error is not None,
      "error_message": error,
      "quality_metrics": self._analyze_response_quality(bot_response, character)
    }
    
    logs.append(log_entry)
    if len(logs) > 1000:
      logs = logs[-1000:]
    
    with open(self.log_file, 'w') as f:
      json.dump(logs, f, indent=2)

  def _analyze_response_quality(self, response, character):
    quality = {
      "has_modern_words": any(word in response.lower() for word in ['computer', 'internet', 'phone', 'ai']),
      "appropriate_length": 10 <= len(response) <= 200,
      "has_punctuation": any(p in response for p in '.!?'),
      "character_specific": character in response or (character == "mysterious_stranger" and "..." in response)
    }
    quality["overall_score"] = sum(1 for v in quality.values() if v and isinstance(v, bool)) / 4
    return quality

  def get_quality_report(self, last_n=50):
    try:
      with open(self.log_file, 'r') as f:
        logs = json.load(f)
      
      recent_logs = logs[-last_n:] if logs else []
      
      if not recent_logs:
        return {"error": "No data available"}
      
      total_score = sum(log.get("quality_metrics", {}).get("overall_score", 0) for log in recent_logs)
      avg_quality = total_score / len(recent_logs)
      
      character_stats = {}
      for log in recent_logs:
        char = log.get("character", "unknown")
        if char not in character_stats:
          character_stats[char] = {"count": 0, "total_score": 0}
        character_stats[char]["count"] += 1
        character_stats[char]["total_score"] += log.get("quality_metrics", {}).get("overall_score", 0)
      
      for char in character_stats:
        character_stats[char]["avg_score"] = character_stats[char]["total_score"] / character_stats[char]["count"]
      
      return {
        "period": f"Last {len(recent_logs)} interactions",
        "overall_quality": round(avg_quality, 3),
        "character_breakdown": character_stats,
        "total_interactions": len(logs)
      }
    except:
      return {"error": "Could not analyze data"}

  def get_conversation_stats(self, session_id=None):
    try:
      with open(self.log_file, 'r') as f:
        logs = json.load(f)
      
      if session_id:
        logs = [log for log in logs if log.get("session_id") == session_id]
      
      if not logs:
        return {"error": "No data found", "session_id": session_id}
      
      total_interactions = len(logs)
      avg_response_time = sum(log.get("response_time", 0) for log in logs) / total_interactions if total_interactions > 0 else 0
      
      quality_scores = [log.get("quality_metrics", {}).get("overall_score", 0) for log in logs]
      avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
      
      character_consistency = self._calculate_character_consistency(logs)
      fantasy_immersion = self._calculate_fantasy_immersion(logs)
      
      return {
        "session_id": session_id,
        "total_interactions": total_interactions,
        "avg_response_time": round(avg_response_time, 2),
        "avg_quality": round(avg_quality, 2),
        "character_consistency": round(character_consistency, 2),
        "fantasy_immersion": round(fantasy_immersion, 2),
        "error_rate": sum(1 for log in logs if log.get("has_error", False)) / total_interactions if total_interactions > 0 else 0
      }
    except Exception as e:
      return {"error": f"Could not get stats: {str(e)}"}

  def generate_quality_report(self, session_id=None):
    try:
      with open(self.log_file, 'r') as f:
        logs = json.load(f)
      
      if session_id:
        logs = [log for log in logs if log.get("session_id") == session_id]
      
      if not logs:
        return {"error": "No data available for report"}

      stats = self.get_conversation_stats(session_id)
      character_analysis = {}
      for log in logs:
        char = log.get("character", "unknown")
        if char not in character_analysis:
          character_analysis[char] = {
            "interactions": 0,
            "avg_response_length": 0,
            "quality_scores": []
          }
        character_analysis[char]["interactions"] += 1
        character_analysis[char]["quality_scores"].append(
          log.get("quality_metrics", {}).get("overall_score", 0)
        )

      for char in character_analysis:
        scores = character_analysis[char]["quality_scores"]
        character_analysis[char]["avg_quality"] = round(sum(scores) / len(scores), 2) if scores else 0
        del character_analysis[char]["quality_scores"] 
      common_issues = self._identify_common_issues(logs)
      
      return {
        "report_generated": datetime.now().isoformat(),
        "session_id": session_id or "global",
        "summary": stats,
        "character_analysis": character_analysis,
        "common_issues": common_issues[:5], 
        "recommendations": self._generate_recommendations(logs)
      }
    except Exception as e:
      return {"error": f"Could not generate report: {str(e)}"}

  def _calculate_character_consistency(self, logs):
    consistency_score = 0
    total_checks = 0
    
    for log in logs:
      char = log.get("character", "")
      response = log.get("bot_response", "").lower()

      if char == "mysterious_stranger" and "..." in response:
        consistency_score += 1
      elif char == "tavern_keeper" and any(word in response for word in ["ale", "tavern", "drink"]):
        consistency_score += 1
      elif char == "worried_miner" and any(word in response for word in ["mine", "tomek", "worry"]):
        consistency_score += 1
      elif char == "merchant" and any(word in response for word in ["gold", "trade", "buy", "sell"]):
        consistency_score += 1
      
      total_checks += 1
    
    return (consistency_score / total_checks * 10) if total_checks > 0 else 5

  def _calculate_fantasy_immersion(self, logs):
    fantasy_score = 0
    total_responses = len(logs)
    
    fantasy_keywords = ["tavern", "ale", "mine", "silver", "merchant", "gold", "stonehaven", "village"]
    modern_keywords = ["computer", "internet", "phone", "ai", "technology", "wifi", "wi-fi"]
    
    for log in logs:
      response = log.get("bot_response", "").lower()
      for keyword in fantasy_keywords:
        if keyword in response:
          fantasy_score += 0.5

      for keyword in modern_keywords:
        if keyword in response:
          fantasy_score -= 2

    normalized_score = max(0, min(10, (fantasy_score / total_responses * 2) + 5))
    return normalized_score

  def _identify_common_issues(self, logs):
    issues = []
    
    for log in logs:
      response = log.get("bot_response", "")
      quality = log.get("quality_metrics", {})
      
      if quality.get("has_modern_words", False):
        issues.append("Modern words detected in fantasy setting")
      
      if not quality.get("appropriate_length", True):
        issues.append("Response length inappropriate")
      
      if not quality.get("has_punctuation", True):
        issues.append("Missing punctuation in response")
      
      if log.get("has_error", False):
        issues.append(f"Model error: {log.get('error_message', 'Unknown')}")

    issue_counts = Counter(issues)
    return [issue for issue, count in issue_counts.most_common(10)]

  def _generate_recommendations(self, logs):
    recommendations = []
    
    total_logs = len(logs)
    if total_logs == 0:
      return ["No data available for recommendations"]

    quality_scores = [log.get("quality_metrics", {}).get("overall_score", 0) for log in logs]
    avg_quality = sum(quality_scores) / len(quality_scores)
    
    if avg_quality < 0.7:
      recommendations.append("Consider adjusting model parameters for better response quality")

    error_rate = sum(1 for log in logs if log.get("has_error", False)) / total_logs
    if error_rate > 0.1:
      recommendations.append("High error rate detected - check model stability")
    
    fantasy_score = self._calculate_fantasy_immersion(logs)
    if fantasy_score < 6:
      recommendations.append("Improve fantasy atmosphere in character responses")
    
    if not recommendations:
      recommendations.append("Performance looks good - continue monitoring")
    
    return recommendations

conversation_tracker = ConversationTracker()