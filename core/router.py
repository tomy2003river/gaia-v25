"""
Intent classification router for GAIA v25.
Uses rule-based patterns with priority system.
"""
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class IntentRule:
    """Intent classification rule."""
    priority: int
    name: str
    pattern: re.Pattern
    description: str


class IntentRouter:
    """Priority-based intent classifier."""
    
    def __init__(self):
        """Initialize router with predefined rules."""
        self.rules: List[IntentRule] = []
        self._register_default_rules()
    
    def _register_default_rules(self):
        """Register default intent rules."""
        # Priority order: Hades > Cronos > Apolo > Rea > Generic
        
        # Hades: Memory and past events
        self.add_rule(
            priority=90,
            name="HADES",
            pattern=r"\b(ayer|pasado|recuerda|recordar|memoria|antes|historial|dijimos|hablamos)\b",
            description="Memory, past events, recall"
        )
        
        # Cronos: Weather and time
        self.add_rule(
            priority=80,
            name="CRONOS",
            pattern=r"\b(clima|tiempo|temperatura|lluvia|sol|nublado|pronóstico|meteorológico|hace\s+calor|hace\s+frío)\b",
            description="Weather queries"
        )
        
        # Apolo: Knowledge and information
        self.add_rule(
            priority=70,
            name="APOLO",
            pattern=r"\b(qué\s+sabes\s+de|saber\s+de|cuéntame\s+sobre|háblame\s+de|información\s+sobre|apolo|quién\s+es|qué\s+es)\b",
            description="Knowledge and information queries"
        )
        
        # Rea: Nature, animals, plants
        self.add_rule(
            priority=60,
            name="REA",
            pattern=r"\b(naturaleza|animal|planta|ecosistema|flora|fauna|especie|rea|árbol|pájaro|mamífero)\b",
            description="Nature, animals, plants"
        )
        
        # Generic greetings and farewells (low priority)
        self.add_rule(
            priority=10,
            name="GREETING",
            pattern=r"\b(hola|buenos\s+días|buenas\s+tardes|buenas\s+noches|hey|hi)\b",
            description="Greetings"
        )
        
        self.add_rule(
            priority=10,
            name="FAREWELL",
            pattern=r"\b(adiós|chau|hasta\s+luego|nos\s+vemos|bye)\b",
            description="Farewells"
        )
    
    def add_rule(self, priority: int, name: str, pattern: str, description: str):
        """
        Add a classification rule.
        
        Args:
            priority: Rule priority (higher = checked first)
            name: Intent name
            pattern: Regex pattern
            description: Rule description
        """
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        rule = IntentRule(
            priority=priority,
            name=name,
            pattern=compiled_pattern,
            description=description
        )
        self.rules.append(rule)
        
        # Keep rules sorted by priority (descending)
        self.rules.sort(key=lambda r: -r.priority)
        
        logger.debug(f"Added rule: {name} (priority {priority})")
    
    def classify(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Classify a message to an intent.
        
        Args:
            message: User message
            context: Optional context (for future use)
            
        Returns:
            Intent name (e.g., "CRONOS", "APOLO", "GENERIC")
        """
        if not message:
            return "GENERIC"
        
        # Check each rule in priority order
        for rule in self.rules:
            if rule.pattern.search(message):
                logger.info(f"Intent classified: {rule.name} (priority {rule.priority})")
                return rule.name
        
        # No match found
        logger.info("Intent classified: GENERIC (no match)")
        return "GENERIC"
    
    def get_all_intents(self) -> List[str]:
        """Get list of all registered intents."""
        intents = list(set(rule.name for rule in self.rules))
        return sorted(intents)
    
    def get_rules_for_intent(self, intent: str) -> List[IntentRule]:
        """Get all rules for a specific intent."""
        return [rule for rule in self.rules if rule.name == intent]
