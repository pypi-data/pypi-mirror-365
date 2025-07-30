

# CFstreamparser

This is a simple Python library for parsing CrystFEL stream files, extracting global geometry, unit cell definitions, and per-frame indexing solutions.

## Installation

```bash
pip install CFstreamparser
```

## Usage Examples

```python
from cfstreamparser import parse_stream_file

# 1. Parse a stream file

stream = parse_stream_file("path/to/your.stream")

# 2. Access global unit cell
print("Unit cell:", stream.uc)

# you can also query specfic parameters, e.g. like this:

print("Unit cell:", stream.uc.a) # to get length of a.

# 3. Access global geometry parameters
print("Detector center-to-lens distance (clen):", stream.geom.params["clen"])

# 4. Retrieve a specific frame by its event number (e.g., 215)
chunk = stream.get_chunk_by_event(215)
if chunk:
    print(f"Frame {chunk.event} has {chunk.num_peaks} peaks")

    # 5. Iterate through all indexing solutions for this frame
    for sol_idx, sol in enumerate(chunk.crystals, start=1):
        print(f"Solution {sol_idx}: {sol.num_reflections} reflections, final residual {sol.predict_refine.final_residual:.3f}")

    # 6. Access the first solution's indexed reflections
    first_solution = chunk.crystals[0]
    print("First 5 indexed reflections:", first_solution.reflections[:5])
else:
    print("No chunk found for event 215")
```