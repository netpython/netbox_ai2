# Scripts CLI Netbox - Lecture et Administration

Collection complète de scripts Python CLI pour interagir avec l'API Netbox. Ces scripts permettent de lire et d'analyser toutes les données de votre instance Netbox avec une sortie en tableaux lisibles.

## 🚀 Installation et Configuration

### 1. Installation des dépendances
```bash
cd netbox_scripts
pip install -r requirements.txt
```

### 2. Configuration
Au premier lancement, un fichier de configuration sera créé automatiquement :
```bash
python3 config.py
```

Modifiez ensuite le fichier `netbox_config.json` généré :
```json
{
  "netbox_url": "https://votre-netbox.example.com",
  "api_token": "VOTRE_TOKEN_API_ICI",
  "timeout": 30,
  "verify_ssl": true,
  "items_per_page": 50,
  "max_items": 1000,
  "date_format": "%Y-%m-%d %H:%M:%S"
}
```

### 3. Configuration alternative via variables d'environnement
```bash
export NETBOX_URL="https://votre-netbox.example.com"
export NETBOX_TOKEN="your-api-token-here"
```

### 4. Test de connexion
```bash
python3 netbox_client.py
# ✅ Connexion à Netbox réussie!
# 📍 URL: https://votre-netbox.example.com  
# 📦 Version: 3.6.1
```

## 📁 Structure des Scripts

```
netbox_scripts/
├── config.py              # ⚙️  Configuration (URL, token API)
├── netbox_client.py       # 🔌 Client API commun
├── devices.py             # 🖥️  Scripts pour équipements
├── ipam.py                # 🌐 Scripts pour IP/réseaux/VLANs
├── dcim.py                # 🏢 Scripts pour datacenter/racks
├── circuits.py            # 🔌 Scripts pour circuits/providers
├── utilities.py           # 🛠️  Utilitaires et exports
├── examples/              # 📚 Documentation et exemples
│   └── README.md
├── requirements.txt       # 📦 Dépendances Python
└── README.md             # 📖 Cette documentation
```

## 🛠️ Utilisation

### 🖥️ Équipements (devices.py)
```bash
# Lister tous les équipements
python3 devices.py list

# Filtrer par site, rôle, fabricant
python3 devices.py list --site "Paris-DC1" --role "switch"

# Détails d'un équipement
python3 devices.py details "sw-core-01"

# Interfaces d'un équipement  
python3 devices.py interfaces "sw-core-01"

# Recherche d'équipements
python3 devices.py search "core"
```

### 🌐 IPAM (ipam.py)
```bash
# Lister les préfixes IP
python3 ipam.py prefixes --site "Paris-DC1"

# Lister les adresses IP
python3 ipam.py ips --device "sw-core-01"

# IPs disponibles dans un préfixe
python3 ipam.py available "192.168.1.0/24"

# Statistiques d'utilisation IP
python3 ipam.py stats

# Lister VLANs et VRFs
python3 ipam.py vlans --site "Paris-DC1"
python3 ipam.py vrfs
```

### 🏢 DCIM (dcim.py)
```bash
# Lister sites et racks
python3 dcim.py sites --region "Europe"
python3 dcim.py racks --site "Paris-DC1"

# Élévation d'un rack
python3 dcim.py elevation "RACK-01"

# Câblage et alimentations
python3 dcim.py cables --site "Paris-DC1"
python3 dcim.py power --site "Paris-DC1"

# Résumé complet d'un site
python3 dcim.py summary "Paris-DC1"
```

### 🔌 Circuits (circuits.py)
```bash
# Lister circuits et fournisseurs
python3 circuits.py list --provider "Orange"
python3 circuits.py providers

# Détails d'un circuit
python3 circuits.py details "CIR-12345"

# Circuits d'un fournisseur
python3 circuits.py provider-circuits "Orange"

# Statistiques des circuits
python3 circuits.py stats
```

### 🛠️ Utilitaires (utilities.py)
```bash
# Recherche globale
python3 utilities.py search "paris"

# Export de données (CSV/JSON)
python3 utilities.py export devices --format csv
python3 utilities.py export ip-addresses --format json

# Statut de Netbox
python3 utilities.py status

# Validation des données
python3 utilities.py validate
```

## 🎯 Exemples de Workflows

### 📊 Audit d'un site complet
```bash
# 1. Résumé général
python3 dcim.py summary "Paris-DC1"

# 2. Inventaire des équipements
python3 devices.py list --site "Paris-DC1"

# 3. Utilisation IP
python3 ipam.py stats --prefix "192.168.0.0/16"

# 4. Circuits du site
python3 circuits.py list --site "Paris-DC1"
```

### 🔍 Analyse d'un équipement
```bash
# Détails complets
python3 devices.py details "sw-core-01"

# Interfaces et connexions
python3 devices.py interfaces "sw-core-01"

# Adresses IP assignées
python3 ipam.py ips --device "sw-core-01"
```

### 📤 Export et reporting
```bash
# Export inventaire complet
python3 utilities.py export devices --output "inventaire.csv"

# Export configuration IP
python3 utilities.py export ip-addresses --format json

# Validation des données
python3 utilities.py validate
```

## ✨ Fonctionnalités

### ✅ **Lecture complète**
- **Équipements** : Inventaire, détails, interfaces, connexions
- **IPAM** : Préfixes, IPs, VLANs, VRFs, statistiques d'utilisation  
- **DCIM** : Sites, racks, élévations, câblage, alimentations
- **Circuits** : Fournisseurs, types, terminaisons
- **Recherche** : Globale dans tous les objets

### ✅ **Formats de sortie**
- **Tableaux** lisibles avec ajustement automatique des colonnes
- **Export CSV** pour analyse dans Excel/LibreOffice
- **Export JSON** pour intégration avec d'autres outils
- **Filtrage avancé** sur tous les attributs

### ✅ **Configuration flexible**
- **Fichier JSON** pour la configuration locale
- **Variables d'environnement** pour l'automatisation
- **Gestion SSL** et timeouts configurables
- **Pagination** automatique pour gros volumes

### ✅ **Robustesse**
- **Gestion d'erreurs** complète avec messages explicites
- **Validation** de la connectivité et des permissions
- **Retry** automatique sur les erreurs temporaires
- **Logging** optionnel pour le débogage

## 🔧 Configuration avancée

### Optimisation des performances
```json
{
  "items_per_page": 100,    // Plus d'éléments par requête
  "max_items": 5000,        // Limite globale
  "timeout": 60             // Timeout plus long
}
```

### SSL et sécurité
```json
{
  "verify_ssl": false,      // Pour certificats auto-signés
  "timeout": 30
}
```

### Variables d'environnement
```bash
# Dans un script d'automatisation
export NETBOX_URL="https://netbox.company.com"
export NETBOX_TOKEN="$(cat /secure/netbox-token)"
python3 utilities.py export devices
```

## 📋 Format des Tableaux

Tous les scripts utilisent des tableaux formatés avec bordures pour une lecture optimale :

```
🖥️  Équipements (156 trouvé(s)):
┌────┬─────────────┬─────────────────────┬───────────┬─────────┬────────┬─────────────────┐
│ ID │ Nom         │ Type                │ Site      │ Rack    │ Status │ IP Primaire     │
├────┼─────────────┼─────────────────────┼───────────┼─────────┼────────┼─────────────────┤
│ 1  │ sw-core-01  │ Cisco Catalyst 9300 │ Paris-DC1 │ RACK-01 │ Active │ 192.168.1.1     │
│ 2  │ fw-edge-01  │ Fortinet FortiGate  │ Paris-DC1 │ RACK-02 │ Active │ 192.168.1.2     │
└────┴─────────────┴─────────────────────┴───────────┴─────────┴────────┴─────────────────┘
```

## 🐛 Dépannage

### Problèmes de connexion
```bash
# Test de base
python3 netbox_client.py

# Vérification de la config
python3 config.py
```

### Erreurs courantes
- **401 Unauthorized** : Token API invalide
- **403 Forbidden** : Permissions insuffisantes  
- **404 Not Found** : URL Netbox incorrecte
- **Timeout** : Augmenter la valeur dans la config

### Debug
```bash
# Variables d'environnement pour debug
export NETBOX_DEBUG=1
python3 devices.py list
```

## 📚 Documentation Complète

Consultez le dossier `examples/` pour des exemples détaillés et des workflows complets.

## 🤝 Contribution

Ces scripts sont conçus pour être facilement étendus. Pour ajouter de nouvelles fonctionnalités :

1. Utilisez le client commun `netbox_client.py`
2. Suivez le pattern des autres scripts pour la CLI
3. Utilisez `tabulate` pour l'affichage des tableaux
4. Ajoutez la gestion d'erreurs appropriée

## 📄 Licence

Scripts open source pour l'administration Netbox.

---

**🎯 Objectif** : Simplifier l'administration quotidienne de Netbox avec des outils CLI puissants et faciles à utiliser.