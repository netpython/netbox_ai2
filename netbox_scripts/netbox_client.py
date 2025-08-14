#!/usr/bin/env python3
"""
Client API Netbox commun pour tous les scripts
"""

import requests
import json
import sys
from urllib.parse import urljoin, urlparse
from config import get_final_config

class NetboxClient:
    def __init__(self, config=None):
        """Initialise le client Netbox"""
        self.config = config or get_final_config()
        self.base_url = self.config['netbox_url'].rstrip('/')
        self.api_url = urljoin(self.base_url, '/api/')
        self.token = self.config['api_token']
        self.timeout = self.config['timeout']
        self.verify_ssl = self.config['verify_ssl']
        
        # Headers pour toutes les requêtes
        self.headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        # Vérification de la configuration
        if not self.token or self.token == "VOTRE_TOKEN_API_ICI":
            print("❌ Token API non configuré!")
            print("Veuillez modifier netbox_config.json ou définir NETBOX_TOKEN")
            sys.exit(1)
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Effectue une requête HTTP vers l'API Netbox"""
        url = urljoin(self.api_url, endpoint.lstrip('/'))
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            # Gestion des erreurs HTTP
            if response.status_code == 401:
                print("❌ Erreur d'authentification - Vérifiez votre token API")
                sys.exit(1)
            elif response.status_code == 403:
                print("❌ Accès refusé - Permissions insuffisantes")
                sys.exit(1)
            elif response.status_code == 404:
                print(f"❌ Endpoint non trouvé: {url}")
                return None
            elif response.status_code >= 400:
                print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
                return None
            
            return response.json()
            
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout lors de la requête vers {url}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"🔌 Erreur de connexion vers {self.base_url}")
            print("Vérifiez l'URL Netbox dans la configuration")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de requête: {e}")
            return None
        except json.JSONDecodeError:
            print("❌ Réponse JSON invalide")
            return None
    
    def get(self, endpoint, params=None):
        """Effectue une requête GET"""
        return self._make_request('GET', endpoint, params=params)
    
    def get_all(self, endpoint, params=None, max_items=None):
        """Récupère tous les éléments avec pagination"""
        all_results = []
        params = params or {}
        max_items = max_items or self.config['max_items']
        
        # Première requête
        response = self.get(endpoint, params)
        if not response:
            return []
        
        all_results.extend(response.get('results', []))
        
        # Pagination
        while response.get('next') and len(all_results) < max_items:
            next_url = response['next']
            # Extraire les paramètres de l'URL next
            from urllib.parse import parse_qs, urlparse
            parsed = urlparse(next_url)
            next_params = parse_qs(parsed.query)
            
            # Convertir les listes en valeurs simples
            for key, value in next_params.items():
                if isinstance(value, list) and len(value) == 1:
                    next_params[key] = value[0]
            
            response = self.get(endpoint, next_params)
            if not response:
                break
                
            all_results.extend(response.get('results', []))
        
        return all_results[:max_items]
    
    def test_connection(self):
        """Test la connexion à l'API Netbox"""
        try:
            response = self.get('/status/')
            if response:
                print("✅ Connexion à Netbox réussie!")
                print(f"📍 URL: {self.base_url}")
                if 'netbox-version' in response:
                    print(f"📦 Version: {response['netbox-version']}")
                return True
            else:
                print("❌ Impossible de se connecter à Netbox")
                return False
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False

# Fonction utilitaire pour créer un client
def create_client():
    """Crée et retourne un client Netbox configuré"""
    return NetboxClient()

if __name__ == "__main__":
    # Test du client
    print("🧪 Test du client Netbox...")
    client = create_client()
    client.test_connection()