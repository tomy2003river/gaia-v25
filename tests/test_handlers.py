"""
Tests for GAIA handlers.
"""
import unittest
from unittest.mock import Mock, MagicMock
from handlers.generic import GenericHandler
from handlers.rea import ReaHandler


class TestGenericHandler(unittest.TestCase):
    """Test generic handler."""
    
    def setUp(self):
        self.handler = GenericHandler()
    
    def test_greeting(self):
        """Test greeting handling."""
        response = self.handler.handle("Hola", {"intent": "GREETING"})
        self.assertTrue(response.success)
        # Check that response contains a greeting-like message
        self.assertTrue(len(response.text) > 0)
    
    def test_farewell(self):
        """Test farewell handling."""
        response = self.handler.handle("Adiós", {"intent": "FAREWELL"})
        self.assertTrue(response.success)
        self.assertEqual(response.intent, "FAREWELL")
    
    def test_help(self):
        """Test help request."""
        response = self.handler.handle("ayuda", {})
        self.assertTrue(response.success)
        self.assertIn("Clima", response.text)
        self.assertIn("Conocimiento", response.text)
    
    def test_unknown(self):
        """Test unknown query."""
        response = self.handler.handle("xyz123 random", {})
        self.assertTrue(response.success)
        self.assertIn("clima", response.text.lower())


class TestReaHandler(unittest.TestCase):
    """Test Rea (nature) handler."""
    
    def setUp(self):
        self.handler = ReaHandler()
    
    def test_known_topic(self):
        """Test handling of known nature topic."""
        response = self.handler.handle("Háblame de los árboles", {})
        self.assertTrue(response.success)
        self.assertIn("árbol", response.text.lower())
    
    def test_unknown_topic(self):
        """Test handling of unknown nature topic."""
        response = self.handler.handle("naturaleza xyz123", {})
        self.assertTrue(response.success)
        self.assertIn("naturaleza", response.text.lower())
    
    def test_empty_message(self):
        """Test handling of empty/vague message."""
        response = self.handler.handle("naturaleza", {})
        self.assertTrue(response.success)


if __name__ == "__main__":
    unittest.main()
