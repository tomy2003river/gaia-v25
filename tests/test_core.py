"""
Unit tests for GAIA v25 core components.
"""
import unittest
from unittest.mock import Mock, patch
from core.router import IntentRouter
from core.memory import Memory
from core.errors import Response


class TestIntentRouter(unittest.TestCase):
    """Test intent classification."""
    
    def setUp(self):
        self.router = IntentRouter()
    
    def test_cronos_weather(self):
        """Test weather intent classification."""
        messages = [
            "¿Qué tiempo hace?",
            "¿Cómo está el clima?",
            "Pronóstico para mañana",
            "El clima está nublado"
        ]
        for msg in messages:
            self.assertEqual(self.router.classify(msg), "CRONOS")
    
    def test_apolo_knowledge(self):
        """Test knowledge intent classification."""
        messages = [
            "¿Qué sabes de Einstein?",
            "Cuéntame sobre la fotosíntesis",
            "¿Quién es Mozart?",
        ]
        for msg in messages:
            self.assertEqual(self.router.classify(msg), "APOLO")
    
    def test_hades_memory(self):
        """Test memory intent classification."""
        messages = [
            "¿De qué hablamos ayer?",
            "¿Recuerdas lo que dijimos?",
            "Memoria de conversaciones",
        ]
        for msg in messages:
            self.assertEqual(self.router.classify(msg), "HADES")
    
    def test_rea_nature(self):
        """Test nature intent classification."""
        messages = [
            "La naturaleza es bella",
            "Un ecosistema complejo",
            "Fauna y flora del bosque",
        ]
        for msg in messages:
            self.assertEqual(self.router.classify(msg), "REA")
    
    def test_generic_fallback(self):
        """Test generic fallback."""
        msg = "Esto es algo completamente aleatorio xyz123"
        self.assertEqual(self.router.classify(msg), "GENERIC")
    
    def test_greeting(self):
        """Test greeting classification."""
        messages = ["Hola", "Buenos días", "Hey"]
        for msg in messages:
            self.assertEqual(self.router.classify(msg), "GREETING")


class TestMemory(unittest.TestCase):
    """Test memory service."""
    
    def setUp(self):
        self.memory = Memory(maxlen=10, decay=0.9, persist=False)
    
    def test_add_and_retrieve(self):
        """Test adding and retrieving events."""
        self.memory.add({"topic": "clima", "content": "test"})
        self.assertEqual(len(self.memory.events), 1)
        
        recent = self.memory.get_recent(1)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["topic"], "clima")
    
    def test_maxlen_limit(self):
        """Test that memory respects maxlen."""
        for i in range(20):
            self.memory.add({"topic": f"topic_{i}"})
        
        self.assertEqual(len(self.memory.events), 10)
    
    def test_topics_with_decay(self):
        """Test topic scoring with decay."""
        self.memory.add({"topic": "clima"})
        self.memory.add({"topic": "clima"})
        self.memory.add({"topic": "naturaleza"})
        
        topics = self.memory.get_topics()
        # "clima" should have higher score (2 mentions)
        self.assertEqual(topics[0][0], "clima")
    
    def test_search(self):
        """Test memory search."""
        self.memory.add({"topic": "clima", "content": "temperatura en Buenos Aires"})
        self.memory.add({"topic": "conocimiento", "content": "información sobre Einstein"})
        
        results = self.memory.search("Einstein")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["topic"], "conocimiento")
    
    def test_clear(self):
        """Test memory clear."""
        self.memory.add({"topic": "test"})
        self.memory.clear()
        self.assertEqual(len(self.memory.events), 0)


class TestResponse(unittest.TestCase):
    """Test response models."""
    
    def test_successful_response(self):
        """Test successful response creation."""
        response = Response(
            text="Test response",
            intent="CRONOS",
            success=True
        )
        self.assertTrue(response.success)
        self.assertIsNone(response.error)
    
    def test_error_response(self):
        """Test error response creation."""
        response = Response(
            text="Error message",
            intent="CRONOS",
            success=False,
            error="Test error"
        )
        self.assertFalse(response.success)
        self.assertEqual(response.error, "Test error")
    
    def test_to_dict(self):
        """Test response serialization."""
        response = Response(
            text="Test",
            intent="TEST",
            metadata={"key": "value"}
        )
        data = response.to_dict()
        self.assertIn("text", data)
        self.assertIn("intent", data)
        self.assertIn("metadata", data)
        self.assertEqual(data["metadata"]["key"], "value")


if __name__ == "__main__":
    unittest.main()
