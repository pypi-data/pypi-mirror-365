# Hvala: Approximate Vertex Cover Solver

![In honor of those who supported me in my final days in Serbia.](docs/serbia.jpg)

This work builds upon [Disproving the Unique Games Conjecture](https://www.preprints.org/manuscript/202506.0875).

---

# The Minimum Vertex Cover Problem

The **Minimum Vertex Cover (MVC)** problem is a classic optimization problem in computer science and graph theory. It involves finding the smallest set of vertices in a graph that **covers** all edges, meaning at least one endpoint of every edge is included in the set.

## Formal Definition

Given an undirected graph $G = (V, E)$, a **vertex cover** is a subset $V' \subseteq V$ such that for every edge $(u, v) \in E$, at least one of $u$ or $v$ belongs to $V'$. The MVC problem seeks the vertex cover with the smallest cardinality.

## Importance and Applications

- **Theoretical Significance:** MVC is a well-known NP-hard problem, central to complexity theory.
- **Practical Applications:**
  - **Network Security:** Identifying critical nodes to disrupt connections.
  - **Bioinformatics:** Analyzing gene regulatory networks.
  - **Wireless Sensor Networks:** Optimizing sensor coverage.

## Related Problems

- **Maximum Independent Set:** The complement of a vertex cover.
- **Set Cover Problem:** A generalization of MVC.

---

## Problem Statement

Input: A Boolean Adjacency Matrix $M$.

Answer: Find a Minimum Vertex Cover.

### Example Instance: 5 x 5 matrix

|        | c1  | c2  | c3  | c4  | c5  |
| ------ | --- | --- | --- | --- | --- |
| **r1** | 0   | 0   | 1   | 0   | 1   |
| **r2** | 0   | 0   | 0   | 1   | 0   |
| **r3** | 1   | 0   | 0   | 0   | 1   |
| **r4** | 0   | 1   | 0   | 0   | 0   |
| **r5** | 1   | 0   | 1   | 0   | 0   |

The input for undirected graph is typically provided in [DIMACS](http://dimacs.rutgers.edu/Challenges) format. In this way, the previous adjacency matrix is represented in a text file using the following string representation:

```
p edge 5 4
e 1 3
e 1 5
e 2 4
e 3 5
```

This represents a 5x5 matrix in DIMACS format such that each edge $(v,w)$ appears exactly once in the input file and is not repeated as $(w,v)$. In this format, every edge appears in the form of

```
e W V
```

where the fields W and V specify the endpoints of the edge while the lower-case character `e` signifies that this is an edge descriptor line.

_Example Solution:_

Vertex Cover Found `1, 2, 3`: Nodes `1`, `2`, and `3` constitute an optimal solution.

---

# Vertex Cover via Degree Reduction Algorithm

## Algorithm Overview

The **Vertex Cover via Degree Reduction Algorithm** is a polynomial-time approximation algorithm that finds near-optimal vertex covers by transforming the input graph into a simpler structure where optimal solutions can be computed efficiently.

### Core Approach

1. **Preprocessing**: Remove self-loops and isolated vertices from the input graph
2. **Component Decomposition**: Process each connected component independently
3. **Degree Reduction**: Transform each component using a novel reduction technique:
   - Replace each vertex `u` of degree `k` with `k` auxiliary vertices
   - Connect each auxiliary vertex to one of `u`'s original neighbors
   - Assign weight `1/k` to each auxiliary vertex
   - Resulting graph has maximum degree ≤ 1 (paths and cycles only)
4. **Optimal Solving**: Apply two different greedy algorithms on the reduced graph:
   - Minimum weighted dominating set algorithm
   - Minimum weighted vertex cover algorithm
5. **Solution Selection**: Choose the better of the two solutions
6. **Extraction**: Map auxiliary vertices back to original vertices

### Key Innovation

The algorithm's strength lies in its **dual-approach strategy**: by solving both dominating set and vertex cover problems optimally on the degree-1 reduced graph and selecting the better solution, it consistently outperforms single-approach algorithms.

## Performance Guarantees

### Approximation Ratio
- **Theoretical Bound**: `< 2` (strict inequality)
- **Practical Performance**: Often significantly better than 2, approaching optimal for many graph classes
- **Comparison**: Outperforms classical algorithms like the standard edge-based 2-approximation

### Time Complexity
- **Overall Runtime**: `O(|V| + |E|)` - linear time
- **Space Complexity**: `O(|V| + |E|)` for storing the reduced graph

#### Complexity Breakdown
| Phase | Time Complexity | Description |
|-------|----------------|-------------|
| Preprocessing | `O(|V| + |E|)` | Remove self-loops and isolated vertices |
| Component Finding | `O(|V| + |E|)` | DFS/BFS for connected components |
| Graph Reduction | `O(|E|)` | Create auxiliary vertices and edges |
| Optimal Solving | `O(|V| + |E|)` | Greedy algorithms on degree-1 graphs |
| Solution Extraction | `O(|V|)` | Map back to original vertices |

## Advantages

✅ **Superior Approximation**: Achieves approximation ratio < 2 (better than classical algorithms)

✅ **Optimal Time Complexity**: Linear time `O(|V| + |E|)` - matches the best possible for graph problems

✅ **Practical Efficiency**: Often produces near-optimal solutions in real-world instances

✅ **Theoretical Rigor**: Formal proofs guarantee correctness and performance bounds

✅ **Robust Design**: Handles all graph types including disconnected graphs and edge cases

## Use Cases

The algorithm is particularly effective for:
- **Large sparse graphs** where linear time complexity is crucial
- **Graphs with moderate vertex degrees** where the reduction preserves structure well
- **Applications requiring proven approximation guarantees** with practical efficiency
- **Real-time systems** where predictable linear performance is essential

## Implementation Notes

The algorithm requires:
- NetworkX for graph operations
- Custom greedy solvers for minimum weighted dominating set and vertex cover on degree-1 graphs
- Efficient data structures for mapping between original and auxiliary vertices

The dual-solution approach (trying both dominating set and vertex cover) is essential for achieving the < 2 approximation ratio and should not be omitted in implementations.

---

# Compile and Environment

## Prerequisites

- Python ≥ 3.12

## Installation

```bash
pip install hvala
```

## Execution

1. Clone the repository:

   ```bash
   git clone https://github.com/frankvegadelgado/hvala.git
   cd hvala
   ```

2. Run the script:

   ```bash
   idemo -i ./benchmarks/testMatrix1
   ```

   utilizing the `idemo` command provided by Hvala's Library to execute the Boolean adjacency matrix `hvala\benchmarks\testMatrix1`. The file `testMatrix1` represents the example described herein. We also support `.xz`, `.lzma`, `.bz2`, and `.bzip2` compressed text files.

   **Example Output:**

   ```
   testMatrix1: Vertex Cover Found 1, 2, 3
   ```

   This indicates nodes `1, 2, 3` form a vertex cover.

---

## Vertex Cover Size

Use the `-c` flag to count the nodes in the vertex cover:

```bash
idemo -i ./benchmarks/testMatrix2 -c
```

**Output:**

```
testMatrix2: Vertex Cover Size 5
```

---

# Command Options

Display help and options:

```bash
idemo -h
```

**Output:**

```bash
usage: idemo [-h] -i INPUTFILE [-a] [-b] [-c] [-v] [-l] [--version]

Compute the Approximate Vertex Cover for undirected graph encoded in DIMACS format.

options:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        input file path
  -a, --approximation   enable comparison with a polynomial-time approximation approach within a factor of at most 2
  -b, --bruteForce      enable comparison with the exponential-time brute-force approach
  -c, --count           calculate the size of the vertex cover
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

---

# Batch Execution

Batch execution allows you to solve multiple graphs within a directory consecutively.

To view available command-line options for the `batch_idemo` command, use the following in your terminal or command prompt:

```bash
batch_idemo -h
```

This will display the following help information:

```bash
usage: batch_idemo [-h] -i INPUTDIRECTORY [-a] [-b] [-c] [-v] [-l] [--version]

Compute the Approximate Vertex Cover for all undirected graphs encoded in DIMACS format and stored in a directory.

options:
  -h, --help            show this help message and exit
  -i INPUTDIRECTORY, --inputDirectory INPUTDIRECTORY
                        Input directory path
  -a, --approximation   enable comparison with a polynomial-time approximation approach within a factor of at most 2
  -b, --bruteForce      enable comparison with the exponential-time brute-force approach
  -c, --count           calculate the size of the vertex cover
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

---

# Testing Application

A command-line utility named `test_idemo` is provided for evaluating the Algorithm using randomly generated, large sparse matrices. It supports the following options:

```bash
usage: test_idemo [-h] -d DIMENSION [-n NUM_TESTS] [-s SPARSITY] [-a] [-b] [-c] [-w] [-v] [-l] [--version]

The Hvala Testing Application using randomly generated, large sparse matrices.

options:
  -h, --help            show this help message and exit
  -d DIMENSION, --dimension DIMENSION
                        an integer specifying the dimensions of the square matrices
  -n NUM_TESTS, --num_tests NUM_TESTS
                        an integer specifying the number of tests to run
  -s SPARSITY, --sparsity SPARSITY
                        sparsity of the matrices (0.0 for dense, close to 1.0 for very sparse)
  -a, --approximation   enable comparison with a polynomial-time approximation approach within a factor of at most 2
  -b, --bruteForce      enable comparison with the exponential-time brute-force approach
  -c, --count           calculate the size of the vertex cover
  -w, --write           write the generated random matrix to a file in the current directory
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

---

# Code

- Python implementation by **Frank Vega**.

---

# License

- MIT License.
