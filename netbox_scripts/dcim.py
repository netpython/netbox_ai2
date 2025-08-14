#!/usr/bin/env python3
"""
Scripts CLI pour la gestion DCIM (Data Center Infrastructure Management) dans Netbox
"""

import argparse
import sys
from tabulate import tabulate
from netbox_client import create_client

def list_sites(client, filters=None):
    """Liste tous les sites"""
    print("📋 Récupération des sites...")
    
    params = {}
    if filters:
        if filters.get('region'):
            params['region'] = filters['region']
        if filters.get('status'):
            params['status'] = filters['status']
    
    sites = client.get_all('/dcim/sites/', params)
    
    if not sites:
        print("❌ Aucun site trouvé")
        return
    
    headers = ['ID', 'Nom', 'Région', 'Status', 'Facility', 'ASN', 'Description']
    rows = []
    
    for site in sites:
        row = [
            site['id'],
            site['name'],
            site['region']['name'] if site.get('region') else 'N/A',
            site['status']['label'] if site.get('status') else 'N/A',
            site.get('facility', 'N/A'),
            site.get('asn', 'N/A'),
            site.get('description', 'N/A')[:50] + ('...' if len(site.get('description', '')) > 50 else '')
        ]
        rows.append(row)
    
    print(f"\n🏢 Sites ({len(sites)} trouvé(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def list_racks(client, filters=None):
    """Liste tous les racks"""
    print("📋 Récupération des racks...")
    
    params = {}
    if filters:
        if filters.get('site'):
            params['site'] = filters['site']
        if filters.get('location'):
            params['location'] = filters['location']
        if filters.get('status'):
            params['status'] = filters['status']
    
    racks = client.get_all('/dcim/racks/', params)
    
    if not racks:
        print("❌ Aucun rack trouvé")
        return
    
    headers = ['ID', 'Nom', 'Site', 'Localisation', 'Status', 'Unités', 'Type', 'Puissance']
    rows = []
    
    for rack in racks:
        row = [
            rack['id'],
            rack['name'],
            rack['site']['name'] if rack.get('site') else 'N/A',
            rack['location']['name'] if rack.get('location') else 'N/A',
            rack['status']['label'] if rack.get('status') else 'N/A',
            f"{rack.get('u_height', 'N/A')}U",
            rack['type']['label'] if rack.get('type') else 'N/A',
            f"{rack.get('max_weight', 'N/A')}kg" if rack.get('max_weight') else 'N/A'
        ]
        rows.append(row)
    
    print(f"\n🗄️  Racks ({len(racks)} trouvé(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def rack_elevation(client, rack_name_or_id):
    """Affiche l'élévation d'un rack"""
    print(f"🔍 Récupération de l'élévation du rack: {rack_name_or_id}")
    
    # Trouver le rack
    if rack_name_or_id.isdigit():
        rack = client.get(f'/dcim/racks/{rack_name_or_id}/')
    else:
        racks = client.get('/dcim/racks/', {'name': rack_name_or_id})
        if racks and racks.get('results'):
            rack = racks['results'][0]
        else:
            rack = None
    
    if not rack:
        print(f"❌ Rack '{rack_name_or_id}' non trouvé")
        return
    
    # Récupérer l'élévation
    elevation = client.get(f'/dcim/racks/{rack["id"]}/elevation/')
    
    if not elevation:
        print("❌ Impossible de récupérer l'élévation")
        return
    
    print(f"\n🗄️  Élévation du rack: {rack['name']} ({rack['u_height']}U)")
    print(f"📍 Site: {rack['site']['name']}")
    if rack.get('location'):
        print(f"📍 Localisation: {rack['location']['name']}")
    print("=" * 60)
    
    # Organiser les données par unité
    rack_units = {}
    for face in ['front', 'rear']:
        if face in elevation:
            for unit_data in elevation[face]:
                unit_num = unit_data['id']
                if unit_num not in rack_units:
                    rack_units[unit_num] = {'front': None, 'rear': None}
                rack_units[unit_num][face] = unit_data.get('device')
    
    # Afficher l'élévation
    headers = ['Unité', 'Face avant', 'Face arrière']
    rows = []
    
    for unit in range(rack['u_height'], 0, -1):  # Du haut vers le bas
        front_device = "🔳 Libre"
        rear_device = "🔳 Libre"
        
        if unit in rack_units:
            if rack_units[unit]['front']:
                device = rack_units[unit]['front']
                front_device = f"🖥️  {device['name']} ({device['device_type']['model']})"
            
            if rack_units[unit]['rear']:
                device = rack_units[unit]['rear']
                rear_device = f"🖥️  {device['name']} ({device['device_type']['model']})"
        
        rows.append([f"U{unit:2d}", front_device, rear_device])
    
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def list_locations(client, site_filter=None):
    """Liste les localisations"""
    print("📋 Récupération des localisations...")
    
    params = {}
    if site_filter:
        params['site'] = site_filter
    
    locations = client.get_all('/dcim/locations/', params)
    
    if not locations:
        print("❌ Aucune localisation trouvée")
        return
    
    headers = ['ID', 'Nom', 'Site', 'Parent', 'Status', 'Description']
    rows = []
    
    for location in locations:
        row = [
            location['id'],
            location['name'],
            location['site']['name'] if location.get('site') else 'N/A',
            location['parent']['name'] if location.get('parent') else 'N/A',
            location['status']['label'] if location.get('status') else 'N/A',
            location.get('description', 'N/A')[:50] + ('...' if len(location.get('description', '')) > 50 else '')
        ]
        rows.append(row)
    
    print(f"\n📍 Localisations ({len(locations)} trouvée(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def list_cables(client, filters=None):
    """Liste les câbles"""
    print("📋 Récupération des câbles...")
    
    params = {}
    if filters:
        if filters.get('site'):
            params['site'] = filters['site']
        if filters.get('status'):
            params['status'] = filters['status']
        if filters.get('type'):
            params['type'] = filters['type']
    
    cables = client.get_all('/dcim/cables/', params)
    
    if not cables:
        print("❌ Aucun câble trouvé")
        return
    
    headers = ['ID', 'Label', 'Type', 'Longueur', 'Extrémité A', 'Extrémité B', 'Status']
    rows = []
    
    for cable in cables:
        # Extrémité A
        termination_a = "N/A"
        if cable.get('a_terminations'):
            term = cable['a_terminations'][0]
            if term.get('object'):
                obj = term['object']
                if obj.get('device') and obj.get('name'):
                    termination_a = f"{obj['device']['name']}:{obj['name']}"
                elif obj.get('name'):
                    termination_a = obj['name']
        
        # Extrémité B
        termination_b = "N/A"
        if cable.get('b_terminations'):
            term = cable['b_terminations'][0]
            if term.get('object'):
                obj = term['object']
                if obj.get('device') and obj.get('name'):
                    termination_b = f"{obj['device']['name']}:{obj['name']}"
                elif obj.get('name'):
                    termination_b = obj['name']
        
        length = f"{cable.get('length', 'N/A')}{cable.get('length_unit', {}).get('label', '')}" if cable.get('length') else 'N/A'
        
        row = [
            cable['id'],
            cable.get('label', 'N/A'),
            cable['type']['label'] if cable.get('type') else 'N/A',
            length,
            termination_a,
            termination_b,
            cable['status']['label'] if cable.get('status') else 'N/A'
        ]
        rows.append(row)
    
    print(f"\n🔌 Câbles ({len(cables)} trouvé(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def list_power_feeds(client, site_filter=None):
    """Liste les alimentations électriques"""
    print("📋 Récupération des alimentations électriques...")
    
    params = {}
    if site_filter:
        params['site'] = site_filter
    
    power_feeds = client.get_all('/dcim/power-feeds/', params)
    
    if not power_feeds:
        print("❌ Aucune alimentation trouvée")
        return
    
    headers = ['ID', 'Nom', 'Rack', 'Status', 'Type', 'Voltage', 'Ampérage', 'Puissance Max']
    rows = []
    
    for feed in power_feeds:
        row = [
            feed['id'],
            feed['name'],
            feed['rack']['name'] if feed.get('rack') else 'N/A',
            feed['status']['label'] if feed.get('status') else 'N/A',
            feed['type']['label'] if feed.get('type') else 'N/A',
            f"{feed.get('voltage', 'N/A')}V" if feed.get('voltage') else 'N/A',
            f"{feed.get('amperage', 'N/A')}A" if feed.get('amperage') else 'N/A',
            f"{feed.get('max_utilization', 'N/A')}%" if feed.get('max_utilization') else 'N/A'
        ]
        rows.append(row)
    
    print(f"\n⚡ Alimentations électriques ({len(power_feeds)} trouvée(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def site_summary(client, site_name):
    """Résumé complet d'un site"""
    print(f"📊 Résumé du site: {site_name}")
    
    # Trouver le site
    sites = client.get('/dcim/sites/', {'name': site_name})
    if not sites or not sites.get('results'):
        print(f"❌ Site '{site_name}' non trouvé")
        return
    
    site = sites['results'][0]
    site_id = site['id']
    
    print(f"\n🏢 Site: {site['name']}")
    print("=" * 50)
    
    # Informations de base
    info_table = [
        ['ID', site['id']],
        ['Nom', site['name']],
        ['Région', site['region']['name'] if site.get('region') else 'N/A'],
        ['Status', site['status']['label'] if site.get('status') else 'N/A'],
        ['Facility ID', site.get('facility', 'N/A')],
        ['ASN', site.get('asn', 'N/A')],
        ['Timezone', site.get('time_zone', 'N/A')],
        ['Description', site.get('description', 'N/A')]
    ]
    print(tabulate(info_table, headers=['Attribut', 'Valeur'], tablefmt='grid'))
    
    # Statistiques
    print(f"\n📊 Statistiques:")
    
    # Compter les équipements
    devices = client.get('/dcim/devices/', {'site_id': site_id})
    device_count = devices['count'] if devices else 0
    
    # Compter les racks
    racks = client.get('/dcim/racks/', {'site_id': site_id})
    rack_count = racks['count'] if racks else 0
    
    # Compter les localisations
    locations = client.get('/dcim/locations/', {'site_id': site_id})
    location_count = locations['count'] if locations else 0
    
    # Compter les câbles
    cables = client.get('/dcim/cables/', {'site': site_name})
    cable_count = cables['count'] if cables else 0
    
    # Compter les préfixes IP
    prefixes = client.get('/ipam/prefixes/', {'site_id': site_id})
    prefix_count = prefixes['count'] if prefixes else 0
    
    stats_table = [
        ['🖥️  Équipements', device_count],
        ['🗄️  Racks', rack_count],
        ['📍 Localisations', location_count],
        ['🔌 Câbles', cable_count],
        ['🌐 Préfixes IP', prefix_count]
    ]
    print(tabulate(stats_table, headers=['Type', 'Nombre'], tablefmt='grid'))

def main():
    parser = argparse.ArgumentParser(description='Scripts CLI pour DCIM Netbox')
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande sites
    sites_parser = subparsers.add_parser('sites', help='Liste les sites')
    sites_parser.add_argument('--region', help='Filtrer par région')
    sites_parser.add_argument('--status', help='Filtrer par status')
    
    # Commande racks
    racks_parser = subparsers.add_parser('racks', help='Liste les racks')
    racks_parser.add_argument('--site', help='Filtrer par site')
    racks_parser.add_argument('--location', help='Filtrer par localisation')
    racks_parser.add_argument('--status', help='Filtrer par status')
    
    # Commande elevation
    elevation_parser = subparsers.add_parser('elevation', help='Élévation d\'un rack')
    elevation_parser.add_argument('rack', help='Nom ou ID du rack')
    
    # Commande locations
    locations_parser = subparsers.add_parser('locations', help='Liste les localisations')
    locations_parser.add_argument('--site', help='Filtrer par site')
    
    # Commande cables
    cables_parser = subparsers.add_parser('cables', help='Liste les câbles')
    cables_parser.add_argument('--site', help='Filtrer par site')
    cables_parser.add_argument('--status', help='Filtrer par status')
    cables_parser.add_argument('--type', help='Filtrer par type')
    
    # Commande power
    power_parser = subparsers.add_parser('power', help='Liste les alimentations électriques')
    power_parser.add_argument('--site', help='Filtrer par site')
    
    # Commande summary
    summary_parser = subparsers.add_parser('summary', help='Résumé d\'un site')
    summary_parser.add_argument('site', help='Nom du site')
    
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
        if args.command == 'sites':
            filters = {'region': args.region, 'status': args.status}
            filters = {k: v for k, v in filters.items() if v is not None}
            list_sites(client, filters if filters else None)
        
        elif args.command == 'racks':
            filters = {'site': args.site, 'location': args.location, 'status': args.status}
            filters = {k: v for k, v in filters.items() if v is not None}
            list_racks(client, filters if filters else None)
        
        elif args.command == 'elevation':
            rack_elevation(client, args.rack)
        
        elif args.command == 'locations':
            list_locations(client, args.site)
        
        elif args.command == 'cables':
            filters = {'site': args.site, 'status': args.status, 'type': args.type}
            filters = {k: v for k, v in filters.items() if v is not None}
            list_cables(client, filters if filters else None)
        
        elif args.command == 'power':
            list_power_feeds(client, args.site)
        
        elif args.command == 'summary':
            site_summary(client, args.site)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Opération interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()