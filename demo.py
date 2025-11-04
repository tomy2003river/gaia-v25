"""
Demo script to showcase GAIA v25 core functionality.
This runs without external dependencies to demonstrate the architecture.
"""

def demo_intent_classification():
    """Demonstrate intent classification."""
    print("="*60)
    print("DEMO: Intent Classification")
    print("="*60)
    
    from core.router import IntentRouter
    
    router = IntentRouter()
    
    test_messages = [
        ("¿Qué tiempo hace?", "CRONOS"),
        ("¿Quién fue Einstein?", "APOLO"),
        ("¿De qué hablamos ayer?", "HADES"),
        ("La naturaleza es bella", "REA"),
        ("Hola", "GREETING"),
    ]
    
    for message, expected in test_messages:
        intent = router.classify(message)
        status = "✓" if intent == expected else "✗"
        print(f"{status} '{message}' → {intent}")
    
    print()


def demo_memory():
    """Demonstrate memory system."""
    print("="*60)
    print("DEMO: Memory System")
    print("="*60)
    
    from core.memory import Memory
    
    memory = Memory(maxlen=10, decay=0.9, persist=False)
    
    # Add some events
    memory.add({"topic": "clima", "content": "Preguntó por el tiempo"})
    memory.add({"topic": "clima", "content": "Temperatura en Madrid"})
    memory.add({"topic": "conocimiento", "content": "Einstein"})
    
    print(f"Total events: {len(memory.events)}")
    
    # Get topics
    topics = memory.get_topics()
    print(f"Top topics: {topics[:3]}")
    
    # Search
    results = memory.search("clima")
    print(f"Search 'clima': {len(results)} results")
    
    print()


def demo_handlers():
    """Demonstrate handler responses."""
    print("="*60)
    print("DEMO: Handlers")
    print("="*60)
    
    from handlers.generic import GenericHandler
    from handlers.rea import ReaHandler
    
    # Generic handler
    generic = GenericHandler()
    response = generic.handle("Hola", {"intent": "GREETING"})
    print(f"Generic: {response.text[:60]}...")
    
    # Rea handler
    rea = ReaHandler()
    response = rea.handle("Háblame de los árboles", {})
    print(f"Rea: {response.text[:60]}...")
    
    print()


def demo_telemetry():
    """Demonstrate telemetry."""
    print("="*60)
    print("DEMO: Telemetry")
    print("="*60)
    
    from core.telemetry import Telemetry
    
    telemetry = Telemetry()
    
    # Log some requests
    telemetry.log_request("CRONOS", 234.5, True)
    telemetry.log_request("APOLO", 567.8, True)
    telemetry.log_request("HADES", 123.4, False, "Test error")
    
    # Get metrics
    metrics = telemetry.get_metrics()
    print(f"Total requests: {metrics['total_requests']}")
    print(f"Total errors: {metrics['total_errors']}")
    print(f"Error rate: {metrics['error_rate']:.1%}")
    print(f"Latency p50: {metrics['latency_p50']:.1f}ms")
    
    print()


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("  GAIA v25 - Architecture Demo")
    print("="*60 + "\n")
    
    try:
        demo_intent_classification()
        demo_memory()
        demo_handlers()
        demo_telemetry()
        
        print("="*60)
        print("✓ All demos completed successfully!")
        print("="*60)
        print("\nTo run the full application:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure .env with your API keys")
        print("  3. Run: python cli.py  OR  python ui/app.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
