"""
CPU Quota - Determine actual CPU availability based on systemd resource limits.

This package provides utilities to get the actual number of CPUs available
in systems with CPU quotas, which is more accurate than nproc in shared systems.
Particularly useful for soma login nodes and other shared computing environments.
"""

__version__ = "0.1.0"

from .core import (
    get_cpu_quota_from_systemd, 
    get_available_cpus, 
    get_available_cpus_conservative,
    get_parallel_workers,
    get_conservative_parallel_workers
)

def main():
    """Main entry point for the command line interface."""
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

__all__ = [
    "get_cpu_quota_from_systemd", 
    "get_available_cpus", 
    "get_available_cpus_conservative",
    "get_parallel_workers",
    "get_conservative_parallel_workers",
    "main"
]