# modules/wcm.py

import json
import os
from datetime import datetime

MEMORY_PATH = "data/context/memory.json"
CONTEXT_WINDOW = 10  # nombre de messages à mémoriser pour le contexte actif

class WilliamContextManager:
    def __init__(self):
        os.makedirs("data/context", exist_ok=True)
        self.memory = self.load_memory()

    def load_memory(self):
        if os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"history": [], "tags": [], "custom_facts": []}

    def save_memory(self):
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4, ensure_ascii=False)

    def update_history(self, user_input, ai_response):
        self.memory["history"].append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "william": ai_response
        })
        self.memory["history"] = self.memory["history"][-CONTEXT_WINDOW:]
        self.save_memory()

    def add_tag(self, tag):
        if tag not in self.memory["tags"]:
            self.memory["tags"].append(tag)
            self.save_memory()

    def add_fact(self, fact):
        self.memory["custom_facts"].append({
            "fact": fact,
            "added": datetime.now().isoformat()
        })
        self.save_memory()

    def get_context_prompt(self):
        """Prépare un contexte textuel pour améliorer la cohérence de la réponse"""
        prompt = ""
        for item in self.memory["history"]:
            prompt += f"Utilisateur : {item['user']}\nWilliam : {item['william']}\n"
        return prompt

    def reset_context(self):
        self.memory["history"] = []
        self.save_memory()

    def get_tags(self):
        return self.memory["tags"]
    
    def get_facts(self):
        return self.memory["custom_facts"]
