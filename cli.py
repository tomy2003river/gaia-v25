"""
CLI version of GAIA v25.
Simple command-line interface for testing without UI.
"""
import sys
import logging
from pathlib import Path

from config import Config
from core import setup_logging
from gaia import GAIACore


def main():
    """Main CLI entry point."""
    # Setup logging
    setup_logging(
        log_level=Config.GAIA_LOG_LEVEL,
        log_file=Config.LOGS_DIR / "gaia_cli.log"
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting GAIA CLI...")
    
    # Validate configuration
    valid, errors = Config.validate()
    if not valid:
        print("❌ Error de configuración:")
        for error in errors:
            print(f"  - {error}")
        print("\nPor favor, configura el archivo .env siguiendo .env.example")
        return 1
    
    # Show configuration
    print("\n" + "="*60)
    print("  GAIA v25 - CLI Mode")
    print("="*60)
    summary = Config.get_summary()
    print(f"✓ Ciudad: {summary['city']}")
    print(f"✓ Idioma: {summary['lang']}")
    print(f"✓ API Key: {'Configurada' if summary['api_key_set'] else 'No configurada'}")
    print("="*60)
    print("\nComandos especiales:")
    print("  /help    - Mostrar ayuda")
    print("  /metrics - Ver métricas")
    print("  /quit    - Salir")
    print("="*60 + "\n")
    
    # Initialize GAIA
    try:
        gaia = GAIACore(Config)
        
        # Main loop
        while True:
            try:
                # Get user input
                user_input = input("\n👤 Tú: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.startswith("/"):
                    if user_input == "/quit":
                        print("\n¡Hasta luego! 👋")
                        break
                    elif user_input == "/help":
                        print_help()
                        continue
                    elif user_input == "/metrics":
                        metrics = gaia.get_metrics()
                        print_metrics(metrics)
                        continue
                    else:
                        print("Comando desconocido. Usa /help para ver comandos disponibles.")
                        continue
                
                # Process message (without TTS in CLI)
                response = gaia.process_message(user_input, speak=False)
                
                # Show response
                if response.success:
                    print(f"\n🤖 GAIA: {response.text}")
                else:
                    print(f"\n❌ Error: {response.text}")
                    if response.error:
                        print(f"   Detalles: {response.error}")
                
            except KeyboardInterrupt:
                print("\n\n¡Hasta luego! 👋")
                break
            except Exception as e:
                logger.error(f"Error in CLI loop: {e}", exc_info=True)
                print(f"\n❌ Error: {e}")
        
        # Shutdown
        gaia.shutdown()
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error fatal: {e}")
        return 1


def print_help():
    """Print help information."""
    help_text = """
╔══════════════════════════════════════════════════════════╗
║                     GAIA v25 - Ayuda                     ║
╚══════════════════════════════════════════════════════════╝

📋 Comandos Especiales:
  /help     - Mostrar esta ayuda
  /metrics  - Ver métricas de uso
  /quit     - Salir de GAIA

🎯 Capacidades:

  🌤️  Clima (Cronos)
       "¿Qué tiempo hace?"
       "¿Cómo está el clima en Madrid?"

  📚 Conocimiento (Apolo)
       "¿Qué sabes de Einstein?"
       "Cuéntame sobre la fotosíntesis"

  🧠 Memoria (Hades)
       "¿De qué hablamos antes?"
       "Dame un resumen"
       "Olvida todo"

  🌿 Naturaleza (Rea)
       "Háblame de los árboles"
       "¿Qué es un ecosistema?"

  💬 General
       "Hola" / "Ayuda" / "Adiós"
"""
    print(help_text)


def print_metrics(metrics):
    """Print telemetry metrics."""
    print("\n" + "="*60)
    print("  📊 Métricas de Uso")
    print("="*60)
    print(f"Total de requests: {metrics.get('total_requests', 0)}")
    print(f"Total de errores: {metrics.get('total_errors', 0)}")
    print(f"Tasa de error: {metrics.get('error_rate', 0):.2%}")
    
    if 'latency_p50' in metrics:
        print(f"\nLatencia:")
        print(f"  • p50: {metrics['latency_p50']:.1f}ms")
        print(f"  • p95: {metrics['latency_p95']:.1f}ms")
        print(f"  • promedio: {metrics['latency_avg']:.1f}ms")
    
    by_intent = metrics.get('by_intent', {})
    if by_intent:
        print(f"\nPor Intent:")
        for intent, data in sorted(by_intent.items(), key=lambda x: -x[1]['count']):
            print(f"  • {intent}: {data['count']} requests, {data['error_rate']:.1%} errores")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    sys.exit(main())
