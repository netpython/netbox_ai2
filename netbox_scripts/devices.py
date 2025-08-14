#!/usr/bin/env python3
"""
Scripts CLI pour la gestion des équipements (devices) dans Netbox
"""

import argparse
import sys
from tabulate import tabulate
from netbox_client import create_client

def list_devices(client, filters=None):
    """Liste tous les équipements"""
    print("📋 Récupération des équipements...")
    
    params = {}
    if filters:
        if filters.get('site'):
            params['site'] = filters['site']
        if filters.get('role'):
            params['role'] = filters['role']
        if filters.get('manufacturer'):
            params['manufacturer'] = filters['manufacturer']
        if filters.get('status'):
            params['status'] = filters['status']
    
    devices = client.get_all('/dcim/devices/', params)
    
    if not devices:
        print("❌ Aucun équipement trouvé")
        return
    
    # Préparation des données pour le tableau
    headers = ['ID', 'Nom', 'Type', 'Site', 'Rack', 'Status', 'IP Primaire']
    rows = []
    
    for device in devices:
        primary_ip = ""
        if device.get('primary_ip'):
            primary_ip = device['primary_ip']['address'].split('/')[0]
        
        row = [
            device['id'],
            device['name'],
            device['device_type']['display'] if device.get('device_type') else 'N/A',
            device['site']['name'] if device.get('site') else 'N/A',
            device['rack']['name'] if device.get('rack') else 'N/A',
            device['status']['label'] if device.get('status') else 'N/A',
            primary_ip
        ]
        rows.append(row)
    
    print(f"\n🖥️  Équipements ({len(devices)} trouvé(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def device_details(client, device_name_or_id):
    """Affiche les détails d'un équipement spécifique"""
    print(f"🔍 Recherche de l'équipement: {device_name_or_id}")
    
    # Essayer par ID d'abord
    if device_name_or_id.isdigit():
        device = client.get(f'/dcim/devices/{device_name_or_id}/')
    else:
        # Recherche par nom
        devices = client.get('/dcim/devices/', {'name': device_name_or_id})
        if devices and devices.get('results'):
            device = devices['results'][0]
        else:
            device = None
    
    if not device:
        print(f"❌ Équipement '{device_name_or_id}' non trouvé")
        return
    
    # Affichage des détails
    print(f"\n🖥️  Détails de l'équipement: {device['name']}")
    print("=" * 50)
    
    details = [
        ['ID', device['id']],
        ['Nom', device['name']],
        ['Type', device['device_type']['display'] if device.get('device_type') else 'N/A'],
        ['Fabricant', device['device_type']['manufacturer']['name'] if device.get('device_type') else 'N/A'],
        ['Site', device['site']['name'] if device.get('site') else 'N/A'],
        ['Rack', device['rack']['name'] if device.get('rack') else 'N/A'],
        ['Position', device.get('position', 'N/A')],
        ['Status', device['status']['label'] if device.get('status') else 'N/A'],
        ['Rôle', device['device_role']['name'] if device.get('device_role') else 'N/A'],
        ['Plateforme', device['platform']['name'] if device.get('platform') else 'N/A'],
        ['Numéro de série', device.get('serial', 'N/A')],
        ['Asset tag', device.get('asset_tag', 'N/A')],
        ['IP Primaire IPv4', device['primary_ip4']['address'] if device.get('primary_ip4') else 'N/A'],
        ['IP Primaire IPv6', device['primary_ip6']['address'] if device.get('primary_ip6') else 'N/A'],
        ['Commentaires', device.get('comments', 'N/A')],
    ]
    
    print(tabulate(details, headers=['Attribut', 'Valeur'], tablefmt='grid'))

def list_device_interfaces(client, device_name_or_id):
    """Liste les interfaces d'un équipement"""
    print(f"🔌 Récupération des interfaces pour: {device_name_or_id}")
    
    # Récupérer l'ID de l'équipement
    device_id = None
    if device_name_or_id.isdigit():
        device_id = device_name_or_id
    else:
        devices = client.get('/dcim/devices/', {'name': device_name_or_id})
        if devices and devices.get('results'):
            device_id = devices['results'][0]['id']
    
    if not device_id:
        print(f"❌ Équipement '{device_name_or_id}' non trouvé")
        return
    
    interfaces = client.get_all('/dcim/interfaces/', {'device_id': device_id})
    
    if not interfaces:
        print("❌ Aucune interface trouvée")
        return
    
    headers = ['Nom', 'Type', 'Status', 'IP Addresses', 'Connecté à', 'Description']
    rows = []
    
    for interface in interfaces:
        # Récupérer les adresses IP
        ip_addresses = []
        if interface.get('count_ipaddresses', 0) > 0:
            ips = client.get_all('/ipam/ip-addresses/', {'interface_id': interface['id']})
            ip_addresses = [ip['address'] for ip in ips]
        
        connected_to = ""
        if interface.get('connected_endpoint'):
            connected_to = f"{interface['connected_endpoint']['device']['name']}:{interface['connected_endpoint']['name']}"
        
        row = [
            interface['name'],
            interface['type']['label'] if interface.get('type') else 'N/A',
            '🟢 Activé' if interface.get('enabled') else '🔴 Désactivé',
            '\n'.join(ip_addresses) if ip_addresses else 'N/A',
            connected_to,
            interface.get('description', 'N/A')
        ]
        rows.append(row)
    
    print(f"\n🔌 Interfaces de l'équipement ({len(interfaces)} trouvée(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def search_devices(client, search_term):
    """Recherche d'équipements par nom, IP ou description"""
    print(f"🔍 Recherche d'équipements: '{search_term}'")
    
    all_devices = []
    
    # Recherche par nom
    devices_by_name = client.get('/dcim/devices/', {'name__icontains': search_term})
    if devices_by_name and devices_by_name.get('results'):
        all_devices.extend(devices_by_name['results'])
    
    # Recherche par adresse IP
    try:
        ip_addresses = client.get('/ipam/ip-addresses/', {'address__icontains': search_term})
        if ip_addresses and ip_addresses.get('results'):
            for ip in ip_addresses['results']:
                if ip.get('assigned_object') and ip['assigned_object'].get('device'):
                    device_id = ip['assigned_object']['device']['id']
                    device = client.get(f'/dcim/devices/{device_id}/')
                    if device and device not in all_devices:
                        all_devices.append(device)
    except:
        pass
    
    # Suppression des doublons
    unique_devices = []
    seen_ids = set()
    for device in all_devices:
        if device['id'] not in seen_ids:
            unique_devices.append(device)
            seen_ids.add(device['id'])
    
    if not unique_devices:
        print(f"❌ Aucun équipement trouvé pour '{search_term}'")
        return
    
    headers = ['ID', 'Nom', 'Type', 'Site', 'Status', 'IP Primaire']
    rows = []
    
    for device in unique_devices:
        primary_ip = ""
        if device.get('primary_ip'):
            primary_ip = device['primary_ip']['address'].split('/')[0]
        
        row = [
            device['id'],
            device['name'],
            device['device_type']['display'] if device.get('device_type') else 'N/A',
            device['site']['name'] if device.get('site') else 'N/A',
            device['status']['label'] if device.get('status') else 'N/A',
            primary_ip
        ]
        rows.append(row)
    
    print(f"\n🔍 Résultats de recherche ({len(unique_devices)} trouvé(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def main():
    parser = argparse.ArgumentParser(description='Scripts CLI pour les équipements Netbox')
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande list
    list_parser = subparsers.add_parser('list', help='Liste tous les équipements')
    list_parser.add_argument('--site', help='Filtrer par site')
    list_parser.add_argument('--role', help='Filtrer par rôle')
    list_parser.add_argument('--manufacturer', help='Filtrer par fabricant')
    list_parser.add_argument('--status', help='Filtrer par status')
    
    # Commande details
    details_parser = subparsers.add_parser('details', help='Détails d\'un équipement')
    details_parser.add_argument('device', help='Nom ou ID de l\'équipement')
    
    # Commande interfaces
    interfaces_parser = subparsers.add_parser('interfaces', help='Interfaces d\'un équipement')
    interfaces_parser.add_argument('device', help='Nom ou ID de l\'équipement')
    
    # Commande search
    search_parser = subparsers.add_parser('search', help='Rechercher des équipements')
    search_parser.add_argument('term', help='Terme de recherche')
    
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
        if args.command == 'list':
            filters = {
                'site': args.site,
                'role': args.role,
                'manufacturer': args.manufacturer,
                'status': args.status
            }
            # Retirer les filtres None
            filters = {k: v for k, v in filters.items() if v is not None}
            list_devices(client, filters if filters else None)
        
        elif args.command == 'details':
            device_details(client, args.device)
        
        elif args.command == 'interfaces':
            list_device_interfaces(client, args.device)
        
        elif args.command == 'search':
            search_devices(client, args.term)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Opération interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()