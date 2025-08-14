#!/usr/bin/env python3
"""
Scripts CLI pour la gestion des circuits dans Netbox
"""

import argparse
import sys
from tabulate import tabulate
from netbox_client import create_client

def list_circuits(client, filters=None):
    """Liste tous les circuits"""
    print("📋 Récupération des circuits...")
    
    params = {}
    if filters:
        if filters.get('provider'):
            params['provider'] = filters['provider']
        if filters.get('type'):
            params['type'] = filters['type']
        if filters.get('status'):
            params['status'] = filters['status']
        if filters.get('site'):
            params['site'] = filters['site']
    
    circuits = client.get_all('/circuits/circuits/', params)
    
    if not circuits:
        print("❌ Aucun circuit trouvé")
        return
    
    headers = ['ID', 'CID', 'Provider', 'Type', 'Status', 'Commit Rate', 'Description']
    rows = []
    
    for circuit in circuits:
        commit_rate = ""
        if circuit.get('commit_rate'):
            commit_rate = f"{circuit['commit_rate']} kbps"
        
        row = [
            circuit['id'],
            circuit['cid'],
            circuit['provider']['name'] if circuit.get('provider') else 'N/A',
            circuit['type']['name'] if circuit.get('type') else 'N/A',
            circuit['status']['label'] if circuit.get('status') else 'N/A',
            commit_rate if commit_rate else 'N/A',
            circuit.get('description', 'N/A')[:50] + ('...' if len(circuit.get('description', '')) > 50 else '')
        ]
        rows.append(row)
    
    print(f"\n🔌 Circuits ({len(circuits)} trouvé(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def list_providers(client):
    """Liste tous les fournisseurs"""
    print("📋 Récupération des fournisseurs...")
    
    providers = client.get_all('/circuits/providers/')
    
    if not providers:
        print("❌ Aucun fournisseur trouvé")
        return
    
    headers = ['ID', 'Nom', 'ASN', 'Account', 'Portal URL', 'NOC Contact', 'Circuits']
    rows = []
    
    for provider in providers:
        # Compter les circuits pour ce fournisseur
        circuits = client.get('/circuits/circuits/', {'provider_id': provider['id']})
        circuit_count = circuits['count'] if circuits else 0
        
        row = [
            provider['id'],
            provider['name'],
            provider.get('asn', 'N/A'),
            provider.get('account', 'N/A'),
            provider.get('portal_url', 'N/A'),
            provider.get('noc_contact', 'N/A'),
            circuit_count
        ]
        rows.append(row)
    
    print(f"\n🏢 Fournisseurs ({len(providers)} trouvé(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def list_circuit_types(client):
    """Liste tous les types de circuits"""
    print("📋 Récupération des types de circuits...")
    
    circuit_types = client.get_all('/circuits/circuit-types/')
    
    if not circuit_types:
        print("❌ Aucun type de circuit trouvé")
        return
    
    headers = ['ID', 'Nom', 'Slug', 'Description', 'Circuits']
    rows = []
    
    for circuit_type in circuit_types:
        # Compter les circuits de ce type
        circuits = client.get('/circuits/circuits/', {'type_id': circuit_type['id']})
        circuit_count = circuits['count'] if circuits else 0
        
        row = [
            circuit_type['id'],
            circuit_type['name'],
            circuit_type['slug'],
            circuit_type.get('description', 'N/A')[:60] + ('...' if len(circuit_type.get('description', '')) > 60 else ''),
            circuit_count
        ]
        rows.append(row)
    
    print(f"\n📋 Types de circuits ({len(circuit_types)} trouvé(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def circuit_details(client, circuit_cid):
    """Affiche les détails d'un circuit spécifique"""
    print(f"🔍 Recherche du circuit: {circuit_cid}")
    
    # Recherche par CID
    circuits = client.get('/circuits/circuits/', {'cid': circuit_cid})
    if not circuits or not circuits.get('results'):
        print(f"❌ Circuit '{circuit_cid}' non trouvé")
        return
    
    circuit = circuits['results'][0]
    
    print(f"\n🔌 Détails du circuit: {circuit['cid']}")
    print("=" * 50)
    
    # Informations de base
    details = [
        ['ID', circuit['id']],
        ['CID', circuit['cid']],
        ['Fournisseur', circuit['provider']['name'] if circuit.get('provider') else 'N/A'],
        ['Type', circuit['type']['name'] if circuit.get('type') else 'N/A'],
        ['Status', circuit['status']['label'] if circuit.get('status') else 'N/A'],
        ['Tenant', circuit['tenant']['name'] if circuit.get('tenant') else 'N/A'],
        ['Date d\'installation', circuit.get('install_date', 'N/A')],
        ['Commit Rate', f"{circuit.get('commit_rate', 'N/A')} kbps" if circuit.get('commit_rate') else 'N/A'],
        ['Description', circuit.get('description', 'N/A')],
        ['Commentaires', circuit.get('comments', 'N/A')]
    ]
    
    print(tabulate(details, headers=['Attribut', 'Valeur'], tablefmt='grid'))
    
    # Récupérer les terminaisons
    print(f"\n🔗 Terminaisons du circuit:")
    terminations = client.get_all('/circuits/circuit-terminations/', {'circuit_id': circuit['id']})
    
    if terminations:
        term_headers = ['Côté', 'Site', 'Provider Network', 'Port Speed', 'Upstream Speed', 'Cross Connect']
        term_rows = []
        
        for term in terminations:
            row = [
                term['term_side'],
                term['site']['name'] if term.get('site') else 'N/A',
                term['provider_network']['name'] if term.get('provider_network') else 'N/A',
                f"{term.get('port_speed', 'N/A')} kbps" if term.get('port_speed') else 'N/A',
                f"{term.get('upstream_speed', 'N/A')} kbps" if term.get('upstream_speed') else 'N/A',
                term.get('xconnect_id', 'N/A')
            ]
            term_rows.append(row)
        
        print(tabulate(term_rows, headers=term_headers, tablefmt='grid'))
    else:
        print("❌ Aucune terminaison trouvée")

def provider_circuits(client, provider_name):
    """Liste tous les circuits d'un fournisseur"""
    print(f"🔍 Recherche des circuits du fournisseur: {provider_name}")
    
    # Trouver le fournisseur
    providers = client.get('/circuits/providers/', {'name': provider_name})
    if not providers or not providers.get('results'):
        print(f"❌ Fournisseur '{provider_name}' non trouvé")
        return
    
    provider = providers['results'][0]
    provider_id = provider['id']
    
    circuits = client.get_all('/circuits/circuits/', {'provider_id': provider_id})
    
    if not circuits:
        print(f"❌ Aucun circuit trouvé pour le fournisseur '{provider_name}'")
        return
    
    print(f"\n🏢 Fournisseur: {provider['name']}")
    print(f"📊 Circuits trouvés: {len(circuits)}")
    print("=" * 50)
    
    headers = ['CID', 'Type', 'Status', 'Sites', 'Commit Rate', 'Install Date']
    rows = []
    
    for circuit in circuits:
        # Récupérer les sites des terminaisons
        terminations = client.get('/circuits/circuit-terminations/', {'circuit_id': circuit['id']})
        sites = []
        if terminations and terminations.get('results'):
            for term in terminations['results']:
                if term.get('site'):
                    sites.append(term['site']['name'])
        
        sites_str = ' ↔ '.join(sites) if sites else 'N/A'
        
        row = [
            circuit['cid'],
            circuit['type']['name'] if circuit.get('type') else 'N/A',
            circuit['status']['label'] if circuit.get('status') else 'N/A',
            sites_str,
            f"{circuit.get('commit_rate', 'N/A')} kbps" if circuit.get('commit_rate') else 'N/A',
            circuit.get('install_date', 'N/A')
        ]
        rows.append(row)
    
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def circuit_statistics(client):
    """Statistiques des circuits"""
    print("📊 Statistiques des circuits")
    print("=" * 40)
    
    # Statistiques générales
    all_circuits = client.get('/circuits/circuits/')
    total_circuits = all_circuits['count'] if all_circuits else 0
    
    # Par status
    print("\n📈 Répartition par status:")
    status_stats = {}
    if all_circuits and all_circuits.get('results'):
        for circuit in all_circuits['results']:
            status = circuit.get('status', {}).get('label', 'Unknown')
            status_stats[status] = status_stats.get(status, 0) + 1
    
    status_rows = [[status, count] for status, count in status_stats.items()]
    if status_rows:
        print(tabulate(status_rows, headers=['Status', 'Nombre'], tablefmt='grid'))
    
    # Par fournisseur
    print(f"\n🏢 Répartition par fournisseur:")
    providers = client.get_all('/circuits/providers/')
    provider_rows = []
    
    for provider in providers:
        circuits = client.get('/circuits/circuits/', {'provider_id': provider['id']})
        count = circuits['count'] if circuits else 0
        if count > 0:
            provider_rows.append([provider['name'], count])
    
    if provider_rows:
        # Trier par nombre de circuits décroissant
        provider_rows.sort(key=lambda x: x[1], reverse=True)
        print(tabulate(provider_rows[:10], headers=['Fournisseur', 'Circuits'], tablefmt='grid'))
        if len(provider_rows) > 10:
            print(f"... et {len(provider_rows) - 10} autres fournisseurs")
    
    # Par type
    print(f"\n📋 Répartition par type:")
    circuit_types = client.get_all('/circuits/circuit-types/')
    type_rows = []
    
    for circuit_type in circuit_types:
        circuits = client.get('/circuits/circuits/', {'type_id': circuit_type['id']})
        count = circuits['count'] if circuits else 0
        if count > 0:
            type_rows.append([circuit_type['name'], count])
    
    if type_rows:
        type_rows.sort(key=lambda x: x[1], reverse=True)
        print(tabulate(type_rows, headers=['Type', 'Circuits'], tablefmt='grid'))
    
    print(f"\n📊 Total général: {total_circuits} circuits")

def main():
    parser = argparse.ArgumentParser(description='Scripts CLI pour les circuits Netbox')
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande list
    list_parser = subparsers.add_parser('list', help='Liste tous les circuits')
    list_parser.add_argument('--provider', help='Filtrer par fournisseur')
    list_parser.add_argument('--type', help='Filtrer par type')
    list_parser.add_argument('--status', help='Filtrer par status')
    list_parser.add_argument('--site', help='Filtrer par site')
    
    # Commande providers
    providers_parser = subparsers.add_parser('providers', help='Liste tous les fournisseurs')
    
    # Commande types
    types_parser = subparsers.add_parser('types', help='Liste tous les types de circuits')
    
    # Commande details
    details_parser = subparsers.add_parser('details', help='Détails d\'un circuit')
    details_parser.add_argument('cid', help='CID du circuit')
    
    # Commande provider-circuits
    provider_circuits_parser = subparsers.add_parser('provider-circuits', help='Circuits d\'un fournisseur')
    provider_circuits_parser.add_argument('provider', help='Nom du fournisseur')
    
    # Commande stats
    stats_parser = subparsers.add_parser('stats', help='Statistiques des circuits')
    
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
                'provider': args.provider,
                'type': args.type,
                'status': args.status,
                'site': args.site
            }
            filters = {k: v for k, v in filters.items() if v is not None}
            list_circuits(client, filters if filters else None)
        
        elif args.command == 'providers':
            list_providers(client)
        
        elif args.command == 'types':
            list_circuit_types(client)
        
        elif args.command == 'details':
            circuit_details(client, args.cid)
        
        elif args.command == 'provider-circuits':
            provider_circuits(client, args.provider)
        
        elif args.command == 'stats':
            circuit_statistics(client)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Opération interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()