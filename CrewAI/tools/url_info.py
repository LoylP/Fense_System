import socket
import whois
import tldextract

def extract_domain(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"

def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception:
        return None

def get_domain_info(url):
    domain = extract_domain(url)
    ip_address = get_ip(domain)

    try:
        w = whois.whois(domain)
        return {
            "domain": domain,
            "ip_address": ip_address,
            "creation_date": str(w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date),
            "registrar": w.registrar,
            "org": w.org,
            "country": w.country
        }
    except Exception:
        return {
            "domain": domain,
            "ip_address": ip_address,
            "creation_date": None,
            "registrar": None,
            "org": None,
            "country": None
        }