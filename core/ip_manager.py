import ipaddress
import random
import os

def load_cidrs(file_path):
    """
    Reads cidr ranges from a file.
    Expected format: one CIDR per line (e.g., 104.16.0.0/12).
    """
    cidrs = []
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                # Validate CIDR
                ipaddress.ip_network(line)
                cidrs.append(line)
            except ValueError:
                continue
    return cidrs

def generate_random_ips(cidrs, total_count=200):
    """
    Generates a list of unique random IPs from the provided CIDR list.
    """
    if not cidrs:
        return []
    
    generated_ips = set()
    
    # We want to distribute the target count roughly among the CIDRs, 
    # but since random sampling is fast, we can just pick a random CIDR 
    # and then a random IP.
    
    attempts = 0
    max_attempts = total_count * 5 
    
    while len(generated_ips) < total_count and attempts < max_attempts:
        attempts += 1
        cidr_str = random.choice(cidrs)
        try:
            network = ipaddress.ip_network(cidr_str)
            
            # For larger networks, picking a random integer is efficient
            # For very small networks, we might just list them, but CF ranges are usually large enough.
            
            num_addresses = network.num_addresses
            
            if num_addresses == 1:
                random_ip = network[0]
            else:
                 # network_address is the first IP
                 # We avoid the .0 and broadcast typically, but for CF Anycast, they might be valid.
                 # Let's just pick any in range.
                 random_int = int(network.network_address) + random.randint(0, num_addresses - 1)
                 random_ip = ipaddress.IPv4Address(random_int)
                 
            generated_ips.add(str(random_ip))
            
        except Exception:
            continue
            
    return list(generated_ips)
