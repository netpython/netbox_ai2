#!/usr/bin/env python3
"""
Configuration pour les scripts Netbox CLI
Modifiez ce fichier avec votre URL Netbox et token API
"""

import json
import os
from pathlib import Path

# Configuration par défaut
DEFAULT_CONFIG = {
    "netbox_url": "https://votre-netbox.example.com",
    "api_token": "VOTRE_TOKEN_API_ICI",
    "timeout": 30,
    "verify_ssl": True,
    "items_per_page": 50,
    "max_items": 1000,
    "date_format": "%Y-%m-%d %H:%M:%S"
}

CONFIG_FILE = Path(__file__).parent / "netbox_config.json"

def load_config():
    """Charge la configuration depuis le fichier JSON ou crée un fichier par défaut"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge avec la config par défaut pour les nouvelles clés
                merged_config = DEFAULT_CONFIG.copy()
                merged_config.update(config)
                return merged_config
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Erreur lors du chargement de la configuration: {e}")
            print("Utilisation de la configuration par défaut")
    
    # Créer le fichier de config par défaut
    save_config(DEFAULT_CONFIG)
    print(f"📝 Fichier de configuration créé: {CONFIG_FILE}")
    print("⚠️  Veuillez modifier netbox_config.json avec votre URL et token API")
    return DEFAULT_CONFIG

def save_config(config):
    """Sauvegarde la configuration dans le fichier JSON"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")

def get_config():
    """Retourne la configuration actuelle"""
    return load_config()

def update_config(**kwargs):
    """Met à jour la configuration avec les valeurs fournies"""
    config = load_config()
    config.update(kwargs)
    save_config(config)
    print("✅ Configuration mise à jour")

# Variables d'environnement (optionnel, override le fichier config)
def get_env_config():
    """Récupère la configuration depuis les variables d'environnement"""
    env_config = {}
    
    if os.getenv('NETBOX_URL'):
        env_config['netbox_url'] = os.getenv('NETBOX_URL')
    
    if os.getenv('NETBOX_TOKEN'):
        env_config['api_token'] = os.getenv('NETBOX_TOKEN')
    
    if os.getenv('NETBOX_TIMEOUT'):
        try:
            env_config['timeout'] = int(os.getenv('NETBOX_TIMEOUT'))
        except ValueError:
            pass
    
    return env_config

def get_final_config():
    """Retourne la configuration finale (fichier + variables d'environnement)"""
    config = get_config()
    env_config = get_env_config()
    config.update(env_config)
    return config

if __name__ == "__main__":
    # Test de la configuration
    config = get_final_config()
    print("🔧 Configuration actuelle:")
    for key, value in config.items():
        if 'token' in key.lower():
            print(f"  {key}: {'*' * len(str(value)) if value else 'NON DÉFINI'}")
        else:
            print(f"  {key}: {value}")