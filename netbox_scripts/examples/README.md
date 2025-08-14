# Exemples d'utilisation des scripts Netbox CLI

Cette documentation fournit des exemples concrets d'utilisation de tous les scripts Netbox CLI.

## 📋 Configuration initiale

### 1. Configuration du fichier de configuration
```bash
# Le fichier netbox_config.json sera créé automatiquement au premier lancement
python3 config.py

# Modifier le fichier généré avec vos informations
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

### 2. Configuration via variables d'environnement (optionnel)
```bash
export NETBOX_URL="https://votre-netbox.example.com"
export NETBOX_TOKEN="your-api-token-here"
export NETBOX_TIMEOUT="30"
```

### 3. Test de la connexion
```bash
python3 netbox_client.py
```

## 🖥️ Scripts pour les équipements (devices.py)

### Lister tous les équipements
```bash
python3 devices.py list
```

### Filtrer les équipements
```bash
# Par site
python3 devices.py list --site "Paris-DC1"

# Par rôle
python3 devices.py list --role "switch"

# Par fabricant
python3 devices.py list --manufacturer "Cisco"

# Par status
python3 devices.py list --status "active"

# Combiner plusieurs filtres
python3 devices.py list --site "Paris-DC1" --role "switch"
```

### Détails d'un équipement
```bash
# Par nom
python3 devices.py details "sw-core-01"

# Par ID
python3 devices.py details 123
```

### Interfaces d'un équipement
```bash
python3 devices.py interfaces "sw-core-01"
python3 devices.py interfaces 123
```

### Rechercher des équipements
```bash
# Par nom
python3 devices.py search "core"

# Par adresse IP
python3 devices.py search "192.168.1.1"
```

## 🌐 Scripts IPAM (ipam.py)

### Lister les préfixes IP
```bash
# Tous les préfixes
python3 ipam.py prefixes

# Filtrer par site
python3 ipam.py prefixes --site "Paris-DC1"

# Filtrer par VRF
python3 ipam.py prefixes --vrf "MGMT"

# Filtrer par rôle
python3 ipam.py prefixes --role "user-lan"
```

### Lister les adresses IP
```bash
# Toutes les adresses IP
python3 ipam.py ips

# Filtrer par préfixe parent
python3 ipam.py ips --prefix "192.168.1.0/24"

# Filtrer par équipement
python3 ipam.py ips --device "sw-core-01"

# Filtrer par status
python3 ipam.py ips --status "active"
```

### Lister les VLANs
```bash
# Tous les VLANs
python3 ipam.py vlans

# Filtrer par site
python3 ipam.py vlans --site "Paris-DC1"

# Filtrer par groupe
python3 ipam.py vlans --group "production"
```

### Lister les VRFs
```bash
python3 ipam.py vrfs
```

### IPs disponibles dans un préfixe
```bash
python3 ipam.py available "192.168.1.0/24"
python3 ipam.py available "10.0.0.0/16"
```

### Statistiques d'utilisation IP
```bash
# Statistiques globales
python3 ipam.py stats

# Pour un préfixe spécifique
python3 ipam.py stats --prefix "192.168.1.0/24"
```

## 🏢 Scripts DCIM (dcim.py)

### Lister les sites
```bash
# Tous les sites
python3 dcim.py sites

# Filtrer par région
python3 dcim.py sites --region "Europe"

# Filtrer par status
python3 dcim.py sites --status "active"
```

### Lister les racks
```bash
# Tous les racks
python3 dcim.py racks

# Filtrer par site
python3 dcim.py racks --site "Paris-DC1"

# Filtrer par localisation
python3 dcim.py racks --location "Server-Room-A"
```

### Élévation d'un rack
```bash
# Par nom
python3 dcim.py elevation "RACK-01"

# Par ID
python3 dcim.py elevation 456
```

### Lister les localisations
```bash
# Toutes les localisations
python3 dcim.py locations

# Filtrer par site
python3 dcim.py locations --site "Paris-DC1"
```

### Lister les câbles
```bash
# Tous les câbles
python3 dcim.py cables

# Filtrer par site
python3 dcim.py cables --site "Paris-DC1"

# Filtrer par type
python3 dcim.py cables --type "cat6"
```

### Alimentations électriques
```bash
# Toutes les alimentations
python3 dcim.py power

# Filtrer par site
python3 dcim.py power --site "Paris-DC1"
```

### Résumé d'un site
```bash
python3 dcim.py summary "Paris-DC1"
```

## 🔌 Scripts circuits (circuits.py)

### Lister les circuits
```bash
# Tous les circuits
python3 circuits.py list

# Filtrer par fournisseur
python3 circuits.py list --provider "Orange"

# Filtrer par type
python3 circuits.py list --type "Internet"

# Filtrer par status
python3 circuits.py list --status "active"
```

### Lister les fournisseurs
```bash
python3 circuits.py providers
```

### Lister les types de circuits
```bash
python3 circuits.py types
```

### Détails d'un circuit
```bash
python3 circuits.py details "CIR-12345"
```

### Circuits d'un fournisseur
```bash
python3 circuits.py provider-circuits "Orange"
```

### Statistiques des circuits
```bash
python3 circuits.py stats
```

## 🛠️ Utilitaires (utilities.py)

### Recherche globale
```bash
# Recherche par terme
python3 utilities.py search "paris"
python3 utilities.py search "192.168"
python3 utilities.py search "switch"
```

### Export de données
```bash
# Export en CSV (par défaut)
python3 utilities.py export devices
python3 utilities.py export sites
python3 utilities.py export ip-addresses

# Export en JSON
python3 utilities.py export devices --format json

# Spécifier un fichier de sortie
python3 utilities.py export devices --output "mes_equipements.csv"
```

### Statut de Netbox
```bash
python3 utilities.py status
```

### Validation des données
```bash
python3 utilities.py validate
```

## 📊 Exemples de workflows courants

### 1. Audit d'un site
```bash
# Résumé général du site
python3 dcim.py summary "Paris-DC1"

# Équipements du site
python3 devices.py list --site "Paris-DC1"

# Racks du site
python3 dcim.py racks --site "Paris-DC1"

# Préfixes IP du site
python3 ipam.py prefixes --site "Paris-DC1"
```

### 2. Analyse d'un équipement
```bash
# Détails de l'équipement
python3 devices.py details "sw-core-01"

# Interfaces de l'équipement
python3 devices.py interfaces "sw-core-01"

# Adresses IP de l'équipement
python3 ipam.py ips --device "sw-core-01"
```

### 3. Planification IP
```bash
# Statistiques d'utilisation
python3 ipam.py stats

# IPs disponibles dans un préfixe
python3 ipam.py available "192.168.1.0/24"

# Préfixes d'un site
python3 ipam.py prefixes --site "Paris-DC1"
```

### 4. Gestion des circuits
```bash
# Tous les circuits d'un fournisseur
python3 circuits.py provider-circuits "Orange"

# Détails d'un circuit spécifique
python3 circuits.py details "CIR-12345"

# Statistiques globales
python3 circuits.py stats
```

### 5. Export et reporting
```bash
# Export de tous les équipements
python3 utilities.py export devices --format csv --output "inventaire_equipements.csv"

# Export des adresses IP
python3 utilities.py export ip-addresses --format json --output "adresses_ip.json"

# Validation des données
python3 utilities.py validate
```

## 🔧 Conseils d'utilisation

### 1. Performance
- Utilisez des filtres pour limiter les résultats sur de grosses instances
- Les exports JSON sont plus rapides que CSV pour de gros volumes
- La configuration `max_items` limite le nombre d'éléments récupérés

### 2. Automatisation
```bash
#!/bin/bash
# Script de backup quotidien
DATE=$(date +%Y%m%d)
mkdir -p backups/$DATE

python3 utilities.py export devices --output "backups/$DATE/devices.csv"
python3 utilities.py export sites --output "backups/$DATE/sites.csv"
python3 utilities.py export ip-addresses --output "backups/$DATE/ips.csv"
```

### 3. Dépannage
```bash
# Test de connexion
python3 netbox_client.py

# Vérification de la configuration
python3 config.py

# Validation des données
python3 utilities.py validate
```

## 📝 Formats de sortie

Tous les scripts utilisent le format tableau par défaut avec `tabulate` pour une lecture humaine optimale. Les colonnes sont automatiquement ajustées et les données trop longues sont tronquées avec "...".

### Exemples de sortie

**Liste d'équipements:**
```
🖥️  Équipements (15 trouvé(s)):
┌────┬─────────────┬─────────────────────┬───────────┬─────────┬────────┬─────────────────┐
│ ID │ Nom         │ Type                │ Site      │ Rack    │ Status │ IP Primaire     │
├────┼─────────────┼─────────────────────┼───────────┼─────────┼────────┼─────────────────┤
│ 1  │ sw-core-01  │ Cisco Catalyst 9300 │ Paris-DC1 │ RACK-01 │ Active │ 192.168.1.1     │
│ 2  │ fw-edge-01  │ Fortinet FortiGate  │ Paris-DC1 │ RACK-02 │ Active │ 192.168.1.2     │
└────┴─────────────┴─────────────────────┴───────────┴─────────┴────────┴─────────────────┘
```

Cette structure offre une excellente lisibilité pour l'administration quotidienne de Netbox.