import argparse
from stats import display_stats
from geo import geo_lookup
from check import check_host
from statuspage import generate_status_page
from bandwidth import show_bandwidth
from packets import sniff_packets
from portscan import scan_ports
from arp import view_arp_table
from firewall import list_rules, add_rule, remove_rule
from interfaces import show_interfaces
from ssl_viewer import view_cert
from subdomains import enumerate_subdomains
from cdn_detect import detect_cdn
from tech_stack import fingerprint_tech
from api_monitor import monitor_api
from wifi_heatmap import export_wifi_heatmap
from bluetooth import scan_bluetooth
from dhcp import view_dhcp_leases
from lan_discovery import discover_lan_services
from proxy_check import check_proxy
from dnsleak import test_dns_leak
from traceroute import visualize_traceroute
from mitm_detect import detect_mitm
from speedtest_cli import run_speedtest
from reachability import check_reachability
from whois_lookup import perform_whois
from tunnel_check import detect_tunnel_leak

def main():
    parser = argparse.ArgumentParser(description="Netcut Network Toolkit")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("stats")
    geo = sub.add_parser("geo")
    geo.add_argument("host")
    check = sub.add_parser("check")
    check.add_argument("host")
    sub.add_parser("statuspage")
    sub.add_parser("bandwidth")
    sniffer = sub.add_parser("sniffer")
    sniffer.add_argument("--port", type=int)
    scan = sub.add_parser("scan")
    scan.add_argument("host")
    scan.add_argument("--fast", action="store_true")
    sub.add_parser("arp")
    fw = sub.add_parser("firewall")
    fw.add_argument("--list", action="store_true")
    fw.add_argument("--add")
    fw.add_argument("--remove")
    sub.add_parser("interfaces")
    ssl = sub.add_parser("ssl")
    ssl.add_argument("host")
    subdomains = sub.add_parser("subdomains")
    subdomains.add_argument("domain")
    cdn = sub.add_parser("cdn")
    cdn.add_argument("domain")
    tech = sub.add_parser("tech")
    tech.add_argument("url")
    api = sub.add_parser("api")
    api.add_argument("url")
    api.add_argument("--headers")
    sub.add_parser("wifi")
    sub.add_parser("bt")
    sub.add_parser("dhcp")
    sub.add_parser("lan")
    proxy = sub.add_parser("proxy")
    proxy.add_argument("proxy")
    sub.add_parser("dnsleak")
    trace = sub.add_parser("trace")
    trace.add_argument("host")
    sub.add_parser("mitm-detect")
    sub.add_parser("speedtest")
    reachability = sub.add_parser("reachability")
    reachability.add_argument("file")
    whois = sub.add_parser("whois")
    whois.add_argument("domain")
    sub.add_parser("tunnel-check")

    args = parser.parse_args()

    match args.command:
        case "stats": display_stats()
        case "geo": geo_lookup(args.host)
        case "check": check_host(args.host)
        case "statuspage": generate_status_page()
        case "bandwidth": show_bandwidth()
        case "sniffer": sniff_packets(args.port)
        case "scan": scan_ports(args.host, args.fast)
        case "arp": view_arp_table()
        case "firewall":
            if args.list: list_rules()
            elif args.add: add_rule(args.add)
            elif args.remove: remove_rule(args.remove)
        case "interfaces": show_interfaces()
        case "ssl": view_cert(args.host)
        case "subdomains": enumerate_subdomains(args.domain)
        case "cdn": detect_cdn(args.domain)
        case "tech": fingerprint_tech(args.url)
        case "api": monitor_api(args.url, args.headers)
        case "wifi": export_wifi_heatmap()
        case "bt": scan_bluetooth()
        case "dhcp": view_dhcp_leases()
        case "lan": discover_lan_services()
        case "proxy": check_proxy(args.proxy)
        case "dnsleak": test_dns_leak()
        case "trace": visualize_traceroute(args.host)
        case "mitm-detect": detect_mitm()
        case "speedtest": run_speedtest()
        case "reachability": check_reachability(args.file)
        case "whois": perform_whois(args.domain)
        case "tunnel-check": detect_tunnel_leak()

if __name__ == "__main__":
    main()