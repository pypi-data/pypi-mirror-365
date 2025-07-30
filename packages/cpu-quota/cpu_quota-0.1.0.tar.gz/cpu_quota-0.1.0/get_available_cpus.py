#!/usr/bin/env python3
"""
Script to determine the actual number of CPUs available based on systemd resource limits.
This is more accurate than nproc in shared systems with CPU quotas.

Usage:
    python3 get_available_cpus.py
    ./get_available_cpus.py
"""

import os
import sys
import math
from pathlib import Path


def get_cpu_quota_from_systemd():
    """
    Read CPU quota from systemd user slice configuration.
    Returns the CPU quota as a float, or None if not found/parseable.
    """
    uid = os.getuid()
    quota_file = Path(f"/run/systemd/system/user-{uid}.slice.d/50-CPUQuota.conf")
    
    if not quota_file.exists():
        return None
    
    try:
        with open(quota_file, 'r') as f:
            content = f.read()
        
        # Look for CPUQuota= line
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('CPUQuota='):
                quota_str = line.split('=', 1)[1].strip()
                
                # Handle percentage format (e.g., "200%" means 2 CPUs)
                if quota_str.endswith('%'):
                    quota_percent = float(quota_str[:-1])
                    return quota_percent / 100.0
                else:
                    # Handle decimal format (e.g., "2.0" means 2 CPUs)
                    return float(quota_str)
    
    except (IOError, ValueError, IndexError) as e:
        print(f"Warning: Could not parse CPU quota file: {e}", file=sys.stderr)
        return None
    
    return None


def get_available_cpus():
    """
    Get the number of CPUs available for parallel execution.
    
    Returns:
        int: Number of CPUs that can be used for parallel processing
    """
    # First try to get systemd CPU quota
    cpu_quota = get_cpu_quota_from_systemd()
    
    if cpu_quota is not None:
        # Round down to get integer number of CPUs
        # This is conservative - if you have 2.5 CPU quota, you get 2 CPUs
        available_cpus = int(math.floor(cpu_quota))
        
        # Ensure at least 1 CPU is available
        available_cpus = max(1, available_cpus)
        
        print(f"Systemd CPU quota: {cpu_quota:.2f}")
        print(f"Available CPUs (floor): {available_cpus}")
        return available_cpus
    
    else:
        # Fallback to system CPU count if no quota is found
        system_cpus = os.cpu_count() or 1
        print(f"No systemd CPU quota found, using system CPU count: {system_cpus}")
        return system_cpus


def get_available_cpus_conservative():
    """
    More conservative version that accounts for system overhead.
    
    Returns:
        int: Conservative number of CPUs for parallel processing
    """
    base_cpus = get_available_cpus()
    
    # Reserve some CPU capacity for system overhead on shared systems
    if base_cpus > 4:
        # On systems with more CPUs, reserve 1 CPU for overhead
        conservative_cpus = base_cpus - 1
    elif base_cpus > 2:
        # On medium systems, use 75% of available CPUs
        conservative_cpus = max(1, int(base_cpus * 0.75))
    else:
        # On small systems, use all available CPUs
        conservative_cpus = base_cpus
    
    print(f"Conservative CPU count (accounting for overhead): {conservative_cpus}")
    return conservative_cpus


def main():
    """Main function when script is run directly."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Get available CPU count based on systemd resource limits"
    )
    parser.add_argument(
        "--conservative", 
        action="store_true",
        help="Use conservative CPU count (reserves some for system overhead)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true", 
        help="Only output the number, no additional information"
    )
    
    args = parser.parse_args()
    
    if args.conservative:
        cpu_count = get_available_cpus_conservative()
    else:
        cpu_count = get_available_cpus()
    
    if args.quiet:
        print(cpu_count)
    else:
        print(f"\nRecommended number of parallel processes: {cpu_count}")


# Example usage functions for importing in other Python scripts
def get_parallel_workers():
    """
    Convenience function to get CPU count for parallel processing.
    This is the function you'd typically use in your Python scripts.
    """
    return get_available_cpus()


def get_conservative_parallel_workers():
    """
    Convenience function to get conservative CPU count for parallel processing.
    Use this in shared environments where you want to be more considerate.
    """
    return get_available_cpus_conservative()


if __name__ == "__main__":
    main()