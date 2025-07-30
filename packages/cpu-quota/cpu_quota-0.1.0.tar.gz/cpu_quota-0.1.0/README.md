
# CPU Quotas (soma login nodes)

The soma login nodes are shared resources. The total CPU resources are _soft-limited_ in order to support multiple users. This is done using `systemd` quotas.

Unfortunately, `Python` libraries and command line utilities like `nproc` don't know about the soft limits and provide inaccurate user CPU core values, leading to oversubscribe processes when running custom parallel scripts.

# Workaround

In this repository you will find some useful scripts that get the user CPU qouta values for soma login nodes:

# 1. python ([get_available_cpus.py](get_available_cpus.py))

This script supports multiple usage modes and options:

## Features:

* Reads systemd CPU *quota* from `/run/systemd/system/user-$UID.slice.d/50-CPUQuota.conf`
* Handles both percentage format (e.g., "200%") and decimal format (e.g., "2.0")
* Provides a conservative mode that reserves CPU for system overhead
* Can be imported as a module in other `Python` scripts
* Includes a quiet mode ideal for scripting

## Usage:

```bash
# Make executable
chmod +x get_available_cpus.py

# Basic usage
./get_available_cpus.py

# Conservative mode (reserves some CPU for system)
./get_available_cpus.py --conservative

# Quiet mode (just the number)
./get_available_cpus.py --quiet
```

## In python scripts:

```python
from get_available_cpus import get_parallel_workers

# Use in multiprocessing
import multiprocessing as mp
num_workers = get_parallel_workers()
with mp.Pool(num_workers) as pool:
    # your parallel code here
```

# 2. bash ([get_available_cpus.sh](get_available_cpus.sh))

This is a bash version of the script above for command-line usage:

## Usage:

```bash
# Make executable
chmod +x get_available_cpus.sh

# Basic usage
./get_available_cpus.sh

# Use in other scripts
NUM_CPUS=$(./get_available_cpus.sh --quiet)
```

# 3. pip installing cpu_quota

## How to install:
```bash
python -m pip install cpu_quota
```

## Usage:

```python
from cpu_quota import get_parallel_workers
num_workers = get_parallel_workers()
```


## Features:
* **Systemd Integration:** Reads actual CPU quota limits rather than just hardware CPU count
* **Fallback:** Falls back to nproc if no systemd limits are found
* **Conservative Mode:** Optionally reserves CPU capacity for system overhead
* **Error Handling:** Gracefully handles missing files or parsing errors
* **Flexible Output:** Quiet mode for scripting, verbose mode for debugging
