# main.py
import sys
import os
from datetime import datetime
import argparse

# Ajouter le dossier modules au PATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def main():
    parser = argparse.ArgumentParser(description="Assistant William")
    parser.add_argument("--diagnostic", action="store_true", help="Exécuter un diagnostic système")
    parser.add_argument("--monitor", action="store_true", help="Démarrer la surveillance continue")
    parser.add_argument("--no-diagnostic", action="store_true", help="Ignorer le diagnostic initial")
    parser.add_argument("--voice", action="store_true", help="Activer le mode vocal")
    parser.add_argument("--text-only", action="store_true", help="Mode texte uniquement")
    
    args = parser.parse_args()
    
    print("🤖 Initialisation de William...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Diagnostic système
    if args.diagnostic:
        from william_diagnostics.diagnostic import run_diagnostic
        run_diagnostic()
        return
    
    # Diagnostic initial (sauf si explicitement désactivé)
    if not args.no_diagnostic:
        try:
            from william_diagnostics.diagnostic import run_diagnostic, start_continuous_monitoring
            print("\n🔍 Diagnostic initial...")
            results = run_diagnostic()
            
            # Vérifier les erreurs critiques
            critical_errors = []
            for module, result in results.items():
                if result["status"] == "ERROR" and module in ["filesystem", "wcm"]:
                    critical_errors.append(module)
            
            if critical_errors:
                print(f"❌ Erreurs critiques détectées: {', '.join(critical_errors)}")
                print("Impossible de démarrer William. Vérifiez les logs.")
                return 1
            
            # Démarrer la surveillance continue si demandée
            if args.monitor:
                print("🔄 Démarrage de la surveillance continue...")
                start_continuous_monitoring()
                
        except ImportError:
            print("⚠️ Module de diagnostic non disponible, démarrage sans diagnostic")
        except Exception as e:
            print(f"⚠️ Erreur lors du diagnostic: {e}")
    
    # Démarrer l'assistant
    try:
        from assistant import WilliamAssistant
        
        # Configuration selon les arguments
        config = {
            "voice_enabled": args.voice,
            "text_only": args.text_only,
            "diagnostic_enabled": not args.no_diagnostic
        }
        
        william = WilliamAssistant(config)
        william.run()
        
    except KeyboardInterrupt:
        print("\n👋 Arrêt de William...")
        
        # Arrêter la surveillance si active
        try:
            from william_diagnostics.diagnostic import stop_continuous_monitoring
            stop_continuous_monitoring()
        except ImportError:
            pass
            
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        
        # Log de l'erreur
        try:
            import traceback
            with open("william_diagnostics/logs/crash.log", "a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.now().isoformat()}] CRASH:\n")
                f.write(traceback.format_exc())
                f.write("\n" + "="*50 + "\n")
        except:
            pass
        
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
