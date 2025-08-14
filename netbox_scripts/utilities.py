#!/usr/bin/env python3
"""
Scripts utilitaires pour Netbox CLI
"""

import argparse
import sys
import json
import csv
from datetime import datetime
from tabulate import tabulate
from netbox_client import create_client

def global_search(client, search_term):
    """Recherche globale dans Netbox"""
    print(f"🔍 Recherche globale: '{search_term}'")
    print("=" * 50)
    
    results = {
        'devices': [],
        'sites': [],
        'racks': [],
        'ip_addresses': [],
        'prefixes': [],
        'vlans': [],
        'circuits': []
    }
    
    # Recherche dans les équipements
    try:
        devices = client.get('/dcim/devices/', {'q': search_term})
        if devices and devices.get('results'):
            results['devices'] = devices['results'][:5]  # Limiter à 5 résultats
    except:
        pass
    
    # Recherche dans les sites
    try:
        sites = client.get('/dcim/sites/', {'q': search_term})
        if sites and sites.get('results'):
            results['sites'] = sites['results'][:5]
    except:
        pass
    
    # Recherche dans les racks
    try:
        racks = client.get('/dcim/racks/', {'q': search_term})
        if racks and racks.get('results'):
            results['racks'] = racks['results'][:5]
    except:
        pass
    
    # Recherche dans les adresses IP
    try:
        ips = client.get('/ipam/ip-addresses/', {'q': search_term})
        if ips and ips.get('results'):
            results['ip_addresses'] = ips['results'][:5]
    except:
        pass
    
    # Recherche dans les préfixes
    try:
        prefixes = client.get('/ipam/prefixes/', {'q': search_term})
        if prefixes and prefixes.get('results'):
            results['prefixes'] = prefixes['results'][:5]
    except:
        pass
    
    # Recherche dans les VLANs
    try:
        vlans = client.get('/ipam/vlans/', {'q': search_term})
        if vlans and vlans.get('results'):
            results['vlans'] = vlans['results'][:5]
    except:
        pass
    
    # Recherche dans les circuits
    try:
        circuits = client.get('/circuits/circuits/', {'q': search_term})
        if circuits and circuits.get('results'):
            results['circuits'] = circuits['results'][:5]
    except:
        pass
    
    # Affichage des résultats
    total_found = sum(len(v) for v in results.values())
    
    if total_found == 0:
        print(f"❌ Aucun résultat trouvé pour '{search_term}'")
        return
    
    print(f"✅ {total_found} résultat(s) trouvé(s)")
    
    # Équipements
    if results['devices']:
        print(f"\n🖥️  Équipements ({len(results['devices'])}):")
        headers = ['ID', 'Nom', 'Type', 'Site']
        rows = []
        for device in results['devices']:
            rows.append([
                device['id'],
                device['name'],
                device['device_type']['display'] if device.get('device_type') else 'N/A',
                device['site']['name'] if device.get('site') else 'N/A'
            ])
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    # Sites
    if results['sites']:
        print(f"\n🏢 Sites ({len(results['sites'])}):")
        headers = ['ID', 'Nom', 'Région', 'Status']
        rows = []
        for site in results['sites']:
            rows.append([
                site['id'],
                site['name'],
                site['region']['name'] if site.get('region') else 'N/A',
                site['status']['label'] if site.get('status') else 'N/A'
            ])
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    # Racks
    if results['racks']:
        print(f"\n🗄️  Racks ({len(results['racks'])}):")
        headers = ['ID', 'Nom', 'Site', 'Status']
        rows = []
        for rack in results['racks']:
            rows.append([
                rack['id'],
                rack['name'],
                rack['site']['name'] if rack.get('site') else 'N/A',
                rack['status']['label'] if rack.get('status') else 'N/A'
            ])
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    # Adresses IP
    if results['ip_addresses']:
        print(f"\n🔢 Adresses IP ({len(results['ip_addresses'])}):")
        headers = ['ID', 'Adresse', 'Status', 'Assignée à']
        rows = []
        for ip in results['ip_addresses']:
            assigned_to = "N/A"
            if ip.get('assigned_object') and ip['assigned_object'].get('device'):
                assigned_to = ip['assigned_object']['device']['name']
            
            rows.append([
                ip['id'],
                ip['address'],
                ip['status']['label'] if ip.get('status') else 'N/A',
                assigned_to
            ])
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    # Préfixes
    if results['prefixes']:
        print(f"\n🌐 Préfixes ({len(results['prefixes'])}):")
        headers = ['ID', 'Préfixe', 'Site', 'Status']
        rows = []
        for prefix in results['prefixes']:
            rows.append([
                prefix['id'],
                prefix['prefix'],
                prefix['site']['name'] if prefix.get('site') else 'N/A',
                prefix['status']['label'] if prefix.get('status') else 'N/A'
            ])
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    # VLANs
    if results['vlans']:
        print(f"\n🏷️  VLANs ({len(results['vlans'])}):")
        headers = ['ID', 'VLAN ID', 'Nom', 'Site']
        rows = []
        for vlan in results['vlans']:
            rows.append([
                vlan['id'],
                vlan['vid'],
                vlan['name'],
                vlan['site']['name'] if vlan.get('site') else 'Global'
            ])
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    # Circuits
    if results['circuits']:
        print(f"\n🔌 Circuits ({len(results['circuits'])}):")
        headers = ['ID', 'CID', 'Fournisseur', 'Status']
        rows = []
        for circuit in results['circuits']:
            rows.append([
                circuit['id'],
                circuit['cid'],
                circuit['provider']['name'] if circuit.get('provider') else 'N/A',
                circuit['status']['label'] if circuit.get('status') else 'N/A'
            ])
        print(tabulate(rows, headers=headers, tablefmt='grid'))

def export_data(client, data_type, output_format='csv', output_file=None):
    """Exporte des données Netbox"""
    print(f"📤 Export des données: {data_type} en format {output_format}")
    
    # Mapping des types de données vers les endpoints
    endpoints = {
        'devices': '/dcim/devices/',
        'sites': '/dcim/sites/',
        'racks': '/dcim/racks/',
        'ip-addresses': '/ipam/ip-addresses/',
        'prefixes': '/ipam/prefixes/',
        'vlans': '/ipam/vlans/',
        'circuits': '/circuits/circuits/',
        'providers': '/circuits/providers/'
    }
    
    if data_type not in endpoints:
        print(f"❌ Type de données non supporté: {data_type}")
        print(f"Types disponibles: {', '.join(endpoints.keys())}")
        return
    
    # Récupérer les données
    data = client.get_all(endpoints[data_type])
    
    if not data:
        print(f"❌ Aucune donnée trouvée pour {data_type}")
        return
    
    # Nom du fichier par défaut
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"netbox_{data_type}_{timestamp}.{output_format}"
    
    # Export selon le format
    if output_format.lower() == 'json':
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    elif output_format.lower() == 'csv':
        if not data:
            print("❌ Aucune donnée à exporter")
            return
        
        # Extraire les clés communes
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        # Filtrer les clés complexes et garder les plus importantes
        simple_keys = []
        for key in sorted(all_keys):
            if not isinstance(data[0].get(key), (dict, list)) or key in ['id', 'name', 'display']:
                simple_keys.append(key)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=simple_keys)
            writer.writeheader()
            
            for item in data:
                # Simplifier les valeurs complexes
                row = {}
                for key in simple_keys:
                    value = item.get(key, '')
                    if isinstance(value, dict):
                        if 'name' in value:
                            value = value['name']
                        elif 'display' in value:
                            value = value['display']
                        else:
                            value = str(value)
                    elif isinstance(value, list):
                        value = ', '.join(str(v) for v in value)
                    row[key] = value
                writer.writerow(row)
    
    else:
        print(f"❌ Format non supporté: {output_format}")
        print("Formats disponibles: json, csv")
        return
    
    print(f"✅ Export terminé: {len(data)} enregistrements dans {output_file}")

def netbox_status(client):
    """Affiche le statut général de Netbox"""
    print("📊 Statut général de Netbox")
    print("=" * 40)
    
    # Informations sur l'instance
    try:
        status = client.get('/status/')
        if status:
            print("✅ Connexion à Netbox: OK")
            if status.get('netbox-version'):
                print(f"📦 Version Netbox: {status['netbox-version']}")
            if status.get('python-version'):
                print(f"🐍 Version Python: {status['python-version']}")
        else:
            print("❌ Impossible de récupérer le statut")
            return
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return
    
    print(f"\n📈 Statistiques des objets:")
    
    # Compter les différents types d'objets
    stats = []
    
    objects_to_count = [
        ('Sites', '/dcim/sites/'),
        ('Équipements', '/dcim/devices/'),
        ('Racks', '/dcim/racks/'),
        ('Interfaces', '/dcim/interfaces/'),
        ('Câbles', '/dcim/cables/'),
        ('Préfixes IP', '/ipam/prefixes/'),
        ('Adresses IP', '/ipam/ip-addresses/'),
        ('VLANs', '/ipam/vlans/'),
        ('VRFs', '/ipam/vrfs/'),
        ('Circuits', '/circuits/circuits/'),
        ('Fournisseurs', '/circuits/providers/')
    ]
    
    for name, endpoint in objects_to_count:
        try:
            response = client.get(endpoint)
            count = response['count'] if response else 0
            stats.append([name, count])
        except:
            stats.append([name, 'Erreur'])
    
    print(tabulate(stats, headers=['Type d\'objet', 'Nombre'], tablefmt='grid'))

def validate_data(client):
    """Validation basique des données"""
    print("🔍 Validation des données Netbox")
    print("=" * 40)
    
    issues = []
    
    # Vérifier les équipements sans IP primaire
    try:
        devices = client.get_all('/dcim/devices/')
        devices_without_ip = [d for d in devices if not d.get('primary_ip4') and not d.get('primary_ip6')]
        if devices_without_ip:
            issues.append(f"🔴 {len(devices_without_ip)} équipements sans IP primaire")
    except:
        issues.append("❌ Erreur lors de la vérification des équipements")
    
    # Vérifier les interfaces non connectées
    try:
        interfaces = client.get('/dcim/interfaces/', {'connected': 'false'})
        unconnected_count = interfaces['count'] if interfaces else 0
        if unconnected_count > 0:
            issues.append(f"🟡 {unconnected_count} interfaces non connectées")
    except:
        issues.append("❌ Erreur lors de la vérification des interfaces")
    
    # Vérifier les racks sans équipements
    try:
        racks = client.get_all('/dcim/racks/')
        empty_racks = []
        for rack in racks:
            devices_in_rack = client.get('/dcim/devices/', {'rack_id': rack['id']})
            if not devices_in_rack or devices_in_rack['count'] == 0:
                empty_racks.append(rack)
        
        if empty_racks:
            issues.append(f"🟡 {len(empty_racks)} racks vides")
    except:
        issues.append("❌ Erreur lors de la vérification des racks")
    
    # Vérifier les circuits sans terminaisons
    try:
        circuits = client.get_all('/circuits/circuits/')
        circuits_without_terms = []
        for circuit in circuits:
            terms = client.get('/circuits/circuit-terminations/', {'circuit_id': circuit['id']})
            if not terms or terms['count'] == 0:
                circuits_without_terms.append(circuit)
        
        if circuits_without_terms:
            issues.append(f"🔴 {len(circuits_without_terms)} circuits sans terminaisons")
    except:
        issues.append("❌ Erreur lors de la vérification des circuits")
    
    # Affichage des résultats
    if issues:
        print("⚠️  Problèmes détectés:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ Aucun problème majeur détecté")

def main():
    parser = argparse.ArgumentParser(description='Utilitaires CLI pour Netbox')
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande search
    search_parser = subparsers.add_parser('search', help='Recherche globale')
    search_parser.add_argument('term', help='Terme de recherche')
    
    # Commande export
    export_parser = subparsers.add_parser('export', help='Exporter des données')
    export_parser.add_argument('type', choices=['devices', 'sites', 'racks', 'ip-addresses', 'prefixes', 'vlans', 'circuits', 'providers'], help='Type de données à exporter')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='csv', help='Format d\'export')
    export_parser.add_argument('--output', help='Fichier de sortie')
    
    # Commande status
    status_parser = subparsers.add_parser('status', help='Statut de Netbox')
    
    # Commande validate
    validate_parser = subparsers.add_parser('validate', help='Validation des données')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Création du client Netbox
    try:
        client = create_client()
    except Exception as e:
        print(f"❌ Erreur lors de la création du client: {e}")
        sys.exit(1)
    
    # Exécution des commandes
    try:
        if args.command == 'search':
            global_search(client, args.term)
        
        elif args.command == 'export':
            export_data(client, args.type, args.format, args.output)
        
        elif args.command == 'status':
            netbox_status(client)
        
        elif args.command == 'validate':
            validate_data(client)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Opération interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()