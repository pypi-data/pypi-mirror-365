#!/bin/bash
# Script to get available CPU count based on systemd resource limits
# Usage: ./get_available_cpus.sh [--conservative] [--quiet]

CONSERVATIVE=false
QUIET=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --conservative)
            CONSERVATIVE=true
            shift
            ;;
        --quiet|-q)
            QUIET=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--conservative] [--quiet]"
            echo "  --conservative: Use conservative CPU count (reserves some for overhead)"
            echo "  --quiet, -q:    Only output the number"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Get CPU quota from systemd
get_cpu_quota() {
    local quota_file="/run/systemd/system/user-${UID}.slice.d/50-CPUQuota.conf"
    
    if [[ ! -f "$quota_file" ]]; then
        return 1
    fi
    
    local cpu_quota=$(grep "^CPUQuota=" "$quota_file" 2>/dev/null | cut -d'=' -f2)
    
    if [[ -z "$cpu_quota" ]]; then
        return 1
    fi
    
    # Handle percentage format (e.g., "200%" means 2.0)
    if [[ "$cpu_quota" == *% ]]; then
        cpu_quota=${cpu_quota%\%}
        cpu_quota=$(echo "scale=2; $cpu_quota / 100" | bc -l 2>/dev/null)
    fi
    
    echo "$cpu_quota"
    return 0
}

# Get available CPUs
get_available_cpus() {
    local cpu_quota
    cpu_quota=$(get_cpu_quota)
    
    if [[ $? -eq 0 && -n "$cpu_quota" ]]; then
        # Use floor of CPU quota
        local available_cpus=$(echo "$cpu_quota" | cut -d'.' -f1)
        # Ensure at least 1 CPU
        available_cpus=${available_cpus:-1}
        if [[ $available_cpus -lt 1 ]]; then
            available_cpus=1
        fi
        
        if [[ "$QUIET" != true ]]; then
            echo "Systemd CPU quota: $cpu_quota" >&2
            echo "Available CPUs (floor): $available_cpus" >&2
        fi
        
        echo "$available_cpus"
    else
        # Fallback to nproc if no quota found
        local system_cpus=$(nproc 2>/dev/null || echo "1")
        
        if [[ "$QUIET" != true ]]; then
            echo "No systemd CPU quota found, using system CPU count: $system_cpus" >&2
        fi
        
        echo "$system_cpus"
    fi
}

# Get conservative CPU count
get_conservative_cpus() {
    local base_cpus
    base_cpus=$(get_available_cpus)
    local conservative_cpus
    
    if [[ $base_cpus -gt 4 ]]; then
        # Reserve 1 CPU for overhead
        conservative_cpus=$((base_cpus - 1))
    elif [[ $base_cpus -gt 2 ]]; then
        # Use 75% of available CPUs
        conservative_cpus=$(echo "($base_cpus * 3) / 4" | bc)
        conservative_cpus=${conservative_cpus:-1}
        if [[ $conservative_cpus -lt 1 ]]; then
            conservative_cpus=1
        fi
    else
        # Use all available CPUs
        conservative_cpus=$base_cpus
    fi
    
    if [[ "$QUIET" != true ]]; then
        echo "Conservative CPU count (accounting for overhead): $conservative_cpus" >&2
    fi
    
    echo "$conservative_cpus"
}

# Main logic
if [[ "$CONSERVATIVE" == true ]]; then
    cpu_count=$(get_conservative_cpus)
else
    cpu_count=$(get_available_cpus)
fi

if [[ "$QUIET" != true ]]; then
    echo ""
    echo "Recommended number of parallel processes: $cpu_count"
else
    echo "$cpu_count"
fi