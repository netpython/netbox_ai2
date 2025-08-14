#!/usr/bin/env python3
"""
Scripts CLI pour la gestion IPAM (IP Address Management) dans Netbox
"""

import argparse
import sys
from tabulate import tabulate
from netbox_client import create_client
import ipaddress

def list_prefixes(client, filters=None):
    """Liste tous les préfixes IP"""
    print("📋 Récupération des préfixes IP...")
    
    params = {}
    if filters:
        if filters.get('vrf'):
            params['vrf'] = filters['vrf']
        if filters.get('site'):
            params['site'] = filters['site']
        if filters.get('role'):
            params['role'] = filters['role']
        if filters.get('status'):
            params['status'] = filters['status']
    
    prefixes = client.get_all('/ipam/prefixes/', params)
    
    if not prefixes:
        print("❌ Aucun préfixe trouvé")
        return
    
    headers = ['ID', 'Préfixe', 'VRF', 'Site', 'Rôle', 'Status', 'Utilisé %', 'Description']
    rows = []
    
    for prefix in prefixes:
        # Calculer le pourcentage d'utilisation
        try:
            network = ipaddress.ip_network(prefix['prefix'])
            total_ips = network.num_addresses
            # Pour IPv4, retirer réseau et broadcast
            if network.version == 4 and network.prefixlen < 31:
                total_ips -= 2
            
            used_percentage = "N/A"
            if prefix.get('_depth') == 0:  # Préfixe parent
                # Récupérer les statistiques d'utilisation
                stats = client.get(f"/ipam/prefixes/{prefix['id']}/available-ips/")
                if stats:
                    available = len(stats) if isinstance(stats, list) else 0
                    used = total_ips - available
                    used_percentage = f"{(used/total_ips)*100:.1f}%" if total_ips > 0 else "0%"
        except:
            used_percentage = "N/A"
        
        row = [
            prefix['id'],
            prefix['prefix'],
            prefix['vrf']['name'] if prefix.get('vrf') else 'Global',
            prefix['site']['name'] if prefix.get('site') else 'N/A',
            prefix['role']['name'] if prefix.get('role') else 'N/A',
            prefix['status']['label'] if prefix.get('status') else 'N/A',
            used_percentage,
            prefix.get('description', 'N/A')[:50] + ('...' if len(prefix.get('description', '')) > 50 else '')
        ]
        rows.append(row)
    
    print(f"\n🌐 Préfixes IP ({len(prefixes)} trouvé(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def list_ip_addresses(client, filters=None):
    """Liste les adresses IP"""
    print("📋 Récupération des adresses IP...")
    
    params = {}
    if filters:
        if filters.get('prefix'):
            params['parent'] = filters['prefix']
        if filters.get('vrf'):
            params['vrf'] = filters['vrf']
        if filters.get('status'):
            params['status'] = filters['status']
        if filters.get('device'):
            params['device'] = filters['device']
    
    ip_addresses = client.get_all('/ipam/ip-addresses/', params)
    
    if not ip_addresses:
        print("❌ Aucune adresse IP trouvée")
        return
    
    headers = ['ID', 'Adresse', 'VRF', 'Status', 'DNS', 'Assignée à', 'Description']
    rows = []
    
    for ip in ip_addresses:
        assigned_to = "N/A"
        if ip.get('assigned_object'):
            obj = ip['assigned_object']
            if obj.get('device'):
                assigned_to = f"Device: {obj['device']['name']}"
                if obj.get('name'):
                    assigned_to += f" ({obj['name']})"
            elif obj.get('virtual_machine'):
                assigned_to = f"VM: {obj['virtual_machine']['name']}"
                if obj.get('name'):
                    assigned_to += f" ({obj['name']})"
            else:
                assigned_to = str(obj)
        
        row = [
            ip['id'],
            ip['address'],
            ip['vrf']['name'] if ip.get('vrf') else 'Global',
            ip['status']['label'] if ip.get('status') else 'N/A',
            ip.get('dns_name', 'N/A'),
            assigned_to,
            ip.get('description', 'N/A')[:40] + ('...' if len(ip.get('description', '')) > 40 else '')
        ]
        rows.append(row)
    
    print(f"\n🔢 Adresses IP ({len(ip_addresses)} trouvée(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def list_vlans(client, filters=None):
    """Liste les VLANs"""
    print("📋 Récupération des VLANs...")
    
    params = {}
    if filters:
        if filters.get('site'):
            params['site'] = filters['site']
        if filters.get('group'):
            params['group'] = filters['group']
        if filters.get('status'):
            params['status'] = filters['status']
    
    vlans = client.get_all('/ipam/vlans/', params)
    
    if not vlans:
        print("❌ Aucun VLAN trouvé")
        return
    
    headers = ['ID', 'VLAN ID', 'Nom', 'Site', 'Groupe', 'Status', 'Rôle', 'Description']
    rows = []
    
    for vlan in vlans:
        row = [
            vlan['id'],
            vlan['vid'],
            vlan['name'],
            vlan['site']['name'] if vlan.get('site') else 'Global',
            vlan['group']['name'] if vlan.get('group') else 'N/A',
            vlan['status']['label'] if vlan.get('status') else 'N/A',
            vlan['role']['name'] if vlan.get('role') else 'N/A',
            vlan.get('description', 'N/A')[:50] + ('...' if len(vlan.get('description', '')) > 50 else '')
        ]
        rows.append(row)
    
    print(f"\n🏷️  VLANs ({len(vlans)} trouvé(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def list_vrfs(client):
    """Liste les VRFs"""
    print("📋 Récupération des VRFs...")
    
    vrfs = client.get_all('/ipam/vrfs/')
    
    if not vrfs:
        print("❌ Aucun VRF trouvé")
        return
    
    headers = ['ID', 'Nom', 'RD', 'RT Import', 'RT Export', 'Description']
    rows = []
    
    for vrf in vrfs:
        import_rts = ', '.join([rt['name'] for rt in vrf.get('import_targets', [])])
        export_rts = ', '.join([rt['name'] for rt in vrf.get('export_targets', [])])
        
        row = [
            vrf['id'],
            vrf['name'],
            vrf.get('rd', 'N/A'),
            import_rts if import_rts else 'N/A',
            export_rts if export_rts else 'N/A',
            vrf.get('description', 'N/A')[:60] + ('...' if len(vrf.get('description', '')) > 60 else '')
        ]
        rows.append(row)
    
    print(f"\n🗂️  VRFs ({len(vrfs)} trouvé(s)):")
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def available_ips(client, prefix):
    """Affiche les IPs disponibles dans un préfixe"""
    print(f"🔍 Recherche d'IPs disponibles dans: {prefix}")
    
    # Trouver le préfixe
    prefixes = client.get('/ipam/prefixes/', {'prefix': prefix})
    if not prefixes or not prefixes.get('results'):
        print(f"❌ Préfixe '{prefix}' non trouvé")
        return
    
    prefix_obj = prefixes['results'][0]
    prefix_id = prefix_obj['id']
    
    # Récupérer les IPs disponibles
    available = client.get(f'/ipam/prefixes/{prefix_id}/available-ips/')
    
    if not available:
        print(f"❌ Aucune IP disponible dans {prefix}")
        return
    
    print(f"\n✅ IPs disponibles dans {prefix} ({len(available)} trouvée(s)):")
    
    # Afficher les 20 premières IPs disponibles
    display_count = min(20, len(available))
    for i, ip in enumerate(available[:display_count]):
        print(f"  {i+1:2d}. {ip['address']}")
    
    if len(available) > 20:
        print(f"  ... et {len(available) - 20} autres")

def ip_usage_stats(client, prefix=None):
    """Statistiques d'utilisation IP"""
    if prefix:
        print(f"📊 Statistiques d'utilisation pour: {prefix}")
        prefixes = client.get('/ipam/prefixes/', {'prefix': prefix})
        if not prefixes or not prefixes.get('results'):
            print(f"❌ Préfixe '{prefix}' non trouvé")
            return
        prefix_list = prefixes['results']
    else:
        print("📊 Statistiques globales d'utilisation IP")
        prefix_list = client.get_all('/ipam/prefixes/')
    
    if not prefix_list:
        print("❌ Aucun préfixe trouvé")
        return
    
    headers = ['Préfixe', 'Total IPs', 'IPs Utilisées', 'IPs Libres', 'Utilisation %']
    rows = []
    
    for prefix_obj in prefix_list:
        try:
            network = ipaddress.ip_network(prefix_obj['prefix'])
            total_ips = network.num_addresses
            
            # Pour IPv4, retirer réseau et broadcast si ce n'est pas un /31 ou /32
            if network.version == 4 and network.prefixlen < 31:
                total_ips -= 2
            
            # Compter les IPs utilisées dans ce préfixe
            used_ips = client.get('/ipam/ip-addresses/', {'parent': prefix_obj['prefix']})
            used_count = used_ips['count'] if used_ips else 0
            
            free_count = total_ips - used_count
            usage_percent = (used_count / total_ips * 100) if total_ips > 0 else 0
            
            row = [
                prefix_obj['prefix'],
                total_ips,
                used_count,
                free_count,
                f"{usage_percent:.1f}%"
            ]
            rows.append(row)
            
        except Exception as e:
            print(f"⚠️  Erreur pour {prefix_obj['prefix']}: {e}")
            continue
    
    if rows:
        print(tabulate(rows, headers=headers, tablefmt='grid'))

def main():
    parser = argparse.ArgumentParser(description='Scripts CLI pour IPAM Netbox')
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande prefixes
    prefixes_parser = subparsers.add_parser('prefixes', help='Liste les préfixes IP')
    prefixes_parser.add_argument('--vrf', help='Filtrer par VRF')
    prefixes_parser.add_argument('--site', help='Filtrer par site')
    prefixes_parser.add_argument('--role', help='Filtrer par rôle')
    prefixes_parser.add_argument('--status', help='Filtrer par status')
    
    # Commande ips
    ips_parser = subparsers.add_parser('ips', help='Liste les adresses IP')
    ips_parser.add_argument('--prefix', help='Filtrer par préfixe parent')
    ips_parser.add_argument('--vrf', help='Filtrer par VRF')
    ips_parser.add_argument('--status', help='Filtrer par status')
    ips_parser.add_argument('--device', help='Filtrer par équipement')
    
    # Commande vlans
    vlans_parser = subparsers.add_parser('vlans', help='Liste les VLANs')
    vlans_parser.add_argument('--site', help='Filtrer par site')
    vlans_parser.add_argument('--group', help='Filtrer par groupe')
    vlans_parser.add_argument('--status', help='Filtrer par status')
    
    # Commande vrfs
    vrfs_parser = subparsers.add_parser('vrfs', help='Liste les VRFs')
    
    # Commande available
    available_parser = subparsers.add_parser('available', help='IPs disponibles dans un préfixe')
    available_parser.add_argument('prefix', help='Préfixe à analyser (ex: 192.168.1.0/24)')
    
    # Commande stats
    stats_parser = subparsers.add_parser('stats', help='Statistiques d\'utilisation')
    stats_parser.add_argument('--prefix', help='Préfixe spécifique à analyser')
    
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
        if args.command == 'prefixes':
            filters = {
                'vrf': args.vrf,
                'site': args.site,
                'role': args.role,
                'status': args.status
            }
            filters = {k: v for k, v in filters.items() if v is not None}
            list_prefixes(client, filters if filters else None)
        
        elif args.command == 'ips':
            filters = {
                'prefix': args.prefix,
                'vrf': args.vrf,
                'status': args.status,
                'device': args.device
            }
            filters = {k: v for k, v in filters.items() if v is not None}
            list_ip_addresses(client, filters if filters else None)
        
        elif args.command == 'vlans':
            filters = {
                'site': args.site,
                'group': args.group,
                'status': args.status
            }
            filters = {k: v for k, v in filters.items() if v is not None}
            list_vlans(client, filters if filters else None)
        
        elif args.command == 'vrfs':
            list_vrfs(client)
        
        elif args.command == 'available':
            available_ips(client, args.prefix)
        
        elif args.command == 'stats':
            ip_usage_stats(client, args.prefix)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Opération interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()