# Created on 26/07/2025
# Author: Frank Vega

import itertools
from . import utils

import networkx as nx
from . import greedy

def find_vertex_cover(graph):
    """
    Compute the approximate vertex cover set for an undirected graph.
    
    A vertex cover is a set of vertices such that every edge in the graph is incident 
    to at least one vertex in the set. This function finds an approximate solution
    using a polynomial-time reduction approach.
    
    Args:
        graph (nx.Graph): A NetworkX Graph object representing the input graph.
                         Must be an undirected graph.
   
    Returns:
        set: A set of vertex indices representing the approximate vertex cover set.
             Returns an empty set if the graph is empty or has no edges.
             
    Raises:
        ValueError: If input is not a NetworkX Graph object.
        RuntimeError: If the polynomial-time reduction fails (max degree > 1 after transformation).
    """
    
    def covering_via_reduction_max_degree_1(graph):
        """
        Internal helper function that reduces the vertex cover problem to maximum degree 1 case.
        
        This function implements a polynomial-time reduction technique:
        1. For each vertex u with degree k, replace it with k auxiliary vertices
        2. Each auxiliary vertex connects to one of u's original neighbors with weight 1/k
        3. Solve the resulting max-degree-1 problem optimally using greedy algorithms
        4. Return the better solution between dominating set and vertex cover approaches
        
        Args:
            graph (nx.Graph): Connected component subgraph to process
            
        Returns:
            set: Vertices in the approximate vertex cover for this component
            
        Raises:
            RuntimeError: If reduction fails (resulting graph has max degree > 1)
        """
        # Create a working copy to avoid modifying the original graph
        G = graph.copy()
        weights = {}
        
        # Reduction step: Replace each vertex with auxiliary vertices
        # This transforms the problem into a maximum degree 1 case
        for u in graph.nodes():
            neighbors = list(G.neighbors(u))  # Get neighbors before removing node
            G.remove_node(u)  # Remove original vertex
            k = len(neighbors)  # Degree of original vertex
            
            # Create auxiliary vertices and connect each to one neighbor
            for i, v in enumerate(neighbors):
                aux_vertex = (u, i)  # Auxiliary vertex naming: (original_vertex, index)
                G.add_edge(aux_vertex, v)
                weights[aux_vertex] = 1/k  # Weight inversely proportional to original degree
        
        # Verify the reduction was successful (max degree should be 1)
        max_degree = max(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0
        if max_degree > 1:
            raise RuntimeError(f"Polynomial-time reduction failed: max degree is {max_degree}, expected ≤ 1")
        
        # Apply greedy algorithm for minimum weighted dominating set (optimal for Δ=1)
        dominating_set = greedy.min_weighted_dominating_set_max_degree_1(G)
        # Extract original vertices from auxiliary vertex pairs
        greedy_solution1 = {u for u, _ in dominating_set}
        
        # Set node weights for the weighted vertex cover algorithm
        nx.set_node_attributes(G, weights, 'weight')
        
        # Apply greedy algorithm for minimum weighted vertex cover (optimal for Δ=1)
        vertex_cover = greedy.min_weighted_vertex_cover_max_degree_1(G)
        # Extract original vertices from auxiliary vertex pairs
        greedy_solution2 = {u for u, _ in vertex_cover}
        
        # Return the smaller of the two solutions (better approximation)
        return greedy_solution1 if len(greedy_solution1) <= len(greedy_solution2) else greedy_solution2
    
    # Input validation: Ensure we have a proper NetworkX Graph
    if not isinstance(graph, nx.Graph):
        raise ValueError("Input must be an undirected NetworkX Graph.")
   
    # Handle trivial cases where no vertex cover is needed
    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        return set()  # Empty graph or no edges means empty vertex cover
   
    # Create a working copy to avoid modifying the input graph
    working_graph = graph.copy()
   
    # Preprocessing: Clean the graph by removing unnecessary elements
    # Remove self-loops since they don't affect vertex cover (vertex covers itself)
    working_graph.remove_edges_from(list(nx.selfloop_edges(working_graph)))
   
    # Remove isolated nodes (degree 0) as they don't contribute to any edge coverage
    working_graph.remove_nodes_from(list(nx.isolates(working_graph)))
   
    # Check if preprocessing left us with an empty graph
    if working_graph.number_of_nodes() == 0:
        return set()
   
    # Initialize the result set that will contain our approximate vertex cover
    approximate_vertex_cover = set()
    
    # Process each connected component independently for efficiency
    # This is optimal since components don't share edges, so their vertex covers are independent
    for component in nx.connected_components(working_graph):
        # Extract the induced subgraph for this connected component
        component_subgraph = working_graph.subgraph(component)
        
        # Apply the reduction-based algorithm to find vertex cover for this component
        vertex_solution = covering_via_reduction_max_degree_1(component_subgraph)
        
        # Add the component's vertex cover to the overall solution
        approximate_vertex_cover.update(vertex_solution)                  
    
    return approximate_vertex_cover

def find_vertex_cover_brute_force(graph):
    """
    Computes an exact minimum vertex cover in exponential time.

    Args:
        graph: A NetworkX Graph.

    Returns:
        A set of vertex indices representing the exact vertex cover, or None if the graph is empty.
    """

    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        return None

    n_vertices = len(graph.nodes())

    for k in range(1, n_vertices + 1): # Iterate through all possible sizes of the cover
        for candidate in itertools.combinations(graph.nodes(), k):
            cover_candidate = set(candidate)
            if utils.is_vertex_cover(graph, cover_candidate):
                return cover_candidate
                
    return None



def find_vertex_cover_approximation(graph):
    """
    Computes an approximate vertex cover in polynomial time with an approximation ratio of at most 2 for undirected graphs.

    Args:
        graph: A NetworkX Graph.

    Returns:
        A set of vertex indices representing the approximate vertex cover, or None if the graph is empty.
    """

    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        return None

    #networkx doesn't have a guaranteed minimum vertex cover function, so we use approximation
    vertex_cover = nx.approximation.vertex_cover.min_weighted_vertex_cover(graph)
    return vertex_cover