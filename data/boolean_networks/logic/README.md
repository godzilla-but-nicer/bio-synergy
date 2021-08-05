# Format Guide

The files in this directory are a weird format called `cnet` used by some SAT
solver. We don't care about the SAT solver but we do care about transition rule
logic so we might as well use this. This is a guide to the format pulled from
the `cana` documentation.

```
# .v = number of nodes
.v 1
# .l = node label
.l 1 node-a
.l 2 node-b
# .n = (node number) (in-degree) (input node 1) … (input node k)
.n 1 2 4 5
01 1 # transition rule
```
