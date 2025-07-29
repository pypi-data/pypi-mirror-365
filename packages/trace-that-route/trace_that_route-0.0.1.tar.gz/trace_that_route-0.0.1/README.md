# Trace that route!

Simple python script adding a wrapper around the `traceroute` command.

## Installation

```bash
pip install trace-that-route
```

## Usage

```python
result = traceroute(target = "1.2.3.4", queries = 3, max_steps = 30, protocol = Protocol.TCP)
print(f"It took {len(result.hops)} steps to reach the target:")
for hop in result.hops:
    for router in hop.routers:
        print(f"{hop.hop_number}: {router.ip} ({router.hostname}) - {router.rtts} ms")
```