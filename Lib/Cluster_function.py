from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans, SpectralClustering
from sklearn.neighbors import kneighbors_graph
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_distances
from collections import Counter
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
import math

def deduplicate_content(content_list):
    unique_content_list = pd.Series(content_list).dropna().drop_duplicates().tolist()
    return unique_content_list

def embed_content(content_list, model_name=None, deduplicate=True):
    if deduplicate == True:
        unique_content_list = content_list
    else:
        unique_content_list = deduplicate_content(content_list)
    
    if model_name is None:
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
    else:
        model_name = model_name

    embedding_model = SentenceTransformer(model_name)
    content_embeddings = embedding_model.encode(unique_content_list, show_progress_bar=True)
    content_embeddings = np.array(content_embeddings)
    return unique_content_list, content_embeddings

def deduplicate_embeddings(embeddings):
    """
    Deduplicate embeddings using cosine similarity.
    
    Args:
        embeddings (array-like): List/array of embeddings with shape (n_samples, n_features).
    
    Returns:
        unique_embeddings (np.ndarray): Embeddings after removing near-duplicates.
        keep_indices (list[int]): Original indices kept as representatives.
        duplicate_groups (list[list[int]]): Groups of indices considered duplicates (including the kept one).
    """
    embeddings = np.array(embeddings)
    n = embeddings.shape[0]
    if n == 0:
        return embeddings, [], []

    # Normalize to compute cosine similarity efficiently
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)  # avoid division by zero
    normalized = embeddings / norms

    # Cosine similarity matrix
    sim_matrix = np.matmul(normalized, normalized.T)

    similarity_threshold = 0.9  # consider items with sim >= 0.9 as duplicates
    keep_indices = []
    duplicate_groups = []
    visited = set()

    for i in range(n):
        if i in visited:
            continue
        keep_indices.append(i)
        group = [i]
        for j in range(i + 1, n):
            if j in visited:
                continue
            if sim_matrix[i, j] >= similarity_threshold:
                visited.add(j)
                group.append(j)
        if len(group) > 1:
            duplicate_groups.append(group)

    unique_embeddings = embeddings[keep_indices]
    return unique_embeddings, keep_indices, duplicate_groups

def find_optimal_clusters(content_embeddings):
    """Find the optimal number of clusters using silhouette score"""
    max_clusters = 10
    sil_scores = []
    for k in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(content_embeddings)
        sil_scores.append(silhouette_score(content_embeddings, labels))
    return sil_scores.index(max(sil_scores)) + 2

def find_optimal_clusters_for_knngraph(content_embeddings, knn_graph, method='spectral', 
                                       metric='cosine', mode='connectivity', max_clusters=15):
    """
    Find optimal number of clusters for KNN graph-based clustering
    
    Uses silhouette score based on the KNN graph similarity matrix rather than
    raw embeddings, which is more appropriate for graph-based clustering.
    
    Args:
        content_embeddings: numpy array of embeddings
        knn_graph: pre-computed KNN graph (sparse matrix)
        method: 'spectral' or 'agglomerative'
        metric: distance metric used
        mode: 'connectivity' or 'distance'
        max_clusters: maximum number of clusters to test
    
    Returns:
        optimal_n_clusters: optimal number of clusters
    """
    n_samples = content_embeddings.shape[0]
    max_clusters = min(max_clusters, n_samples - 1)  # Can't have more clusters than samples
    
    # Prepare affinity matrix for silhouette score calculation
    if mode == 'connectivity':
        affinity_matrix = knn_graph.toarray()
    else:  # distance mode
        # Convert distances to similarities
        affinity_matrix = 1 / (1 + knn_graph.toarray())
        affinity_matrix[np.isinf(affinity_matrix)] = 0
    
    # For silhouette score, we need a distance matrix
    # Use cosine distance from original embeddings
    distance_matrix = cosine_distances(content_embeddings)
    
    sil_scores = []
    tested_clusters = []
    
    print(f"Testing cluster numbers from 2 to {max_clusters} for KNN graph clustering...")
    
    for k in range(2, max_clusters + 1):
        try:
            if method == 'spectral':
                clustering = SpectralClustering(
                    n_clusters=k,
                    affinity='precomputed',
                    random_state=42,
                    n_init=10
                )
                labels = clustering.fit_predict(affinity_matrix)
            else:  # agglomerative
                clustering = AgglomerativeClustering(
                    n_clusters=k,
                    connectivity=knn_graph,
                    linkage='average'
                )
                labels = clustering.fit_predict(content_embeddings)
            
            # Calculate silhouette score using distance matrix
            sil_score = silhouette_score(distance_matrix, labels, metric='precomputed')
            sil_scores.append(sil_score)
            tested_clusters.append(k)
            
        except Exception as e:
            print(f"Warning: Failed to test k={k}: {e}")
            continue
    
    if not sil_scores:
        # Fallback: use simple heuristic
        print("Warning: Could not compute silhouette scores, using heuristic")
        return max(2, int(np.sqrt(n_samples)))
    
    # Find optimal number of clusters
    best_idx = np.argmax(sil_scores)
    optimal_n_clusters = tested_clusters[best_idx]
    best_sil_score = sil_scores[best_idx]
    
    print(f"Optimal clusters for KNN graph: {optimal_n_clusters} (silhouette score: {best_sil_score:.4f})")
    print(f"Tested range: {tested_clusters[0]}-{tested_clusters[-1]}, scores: {[f'{s:.3f}' for s in sil_scores]}")
    
    return optimal_n_clusters

def cluster_with_dbscan(optimal_n_clusters, content_embeddings, eps_values=None):
    """Try different eps values to get better clustering"""
    best_labels = None
    best_eps = None
    best_n_clusters = 0
    
    if eps_values is None:
        eps_values = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    for eps in eps_values:
        dbscan = DBSCAN(eps=eps, min_samples=2, metric='cosine')
        labels = dbscan.fit_predict(content_embeddings)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        if n_clusters > best_n_clusters and n_clusters <= optimal_n_clusters * 2:
            best_labels = labels
            best_eps = eps
            best_n_clusters = n_clusters
    
    if best_labels is None:
        # Fallback to tighter eps
        dbscan = DBSCAN(eps=0.25, min_samples=2, metric='cosine')
        best_labels = dbscan.fit_predict(content_embeddings)
        best_eps = 0.25
        best_n_clusters = len(set(best_labels)) - (1 if -1 in best_labels else 0)
    
    n_noise = list(best_labels).count(-1)
    print(f"DBSCAN (eps={best_eps}): {best_n_clusters} clusters, {n_noise} noise points")
    print(f"Cluster distribution: {Counter(best_labels)}")
    
    return best_labels, best_n_clusters, n_noise

def cluster_with_knngraph(content_embeddings, n_neighbors=None, n_clusters=None, 
                          method='spectral', metric='cosine', mode='connectivity'):
    """
    Cluster using KNN graph-based methods
    
    Args:
        content_embeddings: numpy array of embeddings (n_samples, n_features)
        n_neighbors: number of neighbors for KNN graph (default: auto-calculate)
        n_clusters: number of clusters (default: auto-calculate using optimal clusters)
        method: clustering method - 'spectral' or 'agglomerative'
        metric: distance metric for KNN graph ('cosine', 'euclidean', etc.)
        mode: 'connectivity' (binary) or 'distance' (weighted by distance)
    
    Returns:
        labels: cluster labels
        n_clusters: number of clusters found
        n_noise: number of noise points (0 for KNN graph methods)
    """
    n_samples = content_embeddings.shape[0]
    
    # Auto-determine n_neighbors if not provided
    if n_neighbors is None:
        # Use sqrt of n_samples or minimum of 10, whichever is larger
        n_neighbors = max(int(np.sqrt(n_samples)), 10)
        n_neighbors = min(n_neighbors, n_samples - 1)  # Can't exceed n_samples - 1
    
    # Build KNN graph
    print(f"Building KNN graph with n_neighbors={n_neighbors}, metric={metric}, mode={mode}")
    knn_graph = kneighbors_graph(
        content_embeddings, 
        n_neighbors=n_neighbors, 
        metric=metric,
        mode=mode,
        include_self=False
    )
    
    # Auto-determine n_clusters if not provided using KNN graph-specific method
    if n_clusters is None:
        n_clusters = find_optimal_clusters_for_knngraph(
            content_embeddings, 
            knn_graph, 
            method=method,
            metric=metric,
            mode=mode
        )
    
    # Apply clustering method
    if method == 'spectral':
        # Spectral clustering on KNN graph
        print(f"Applying Spectral Clustering with {n_clusters} clusters")
        clustering = SpectralClustering(
            n_clusters=n_clusters,
            affinity='precomputed',
            random_state=42,
            n_init=10
        )
        # Convert sparse matrix to dense for spectral clustering
        # Use adjacency matrix (connectivity or distance)
        if mode == 'connectivity':
            affinity_matrix = knn_graph.toarray()
        else:  # distance mode
            # Convert distances to similarities (inverse)
            affinity_matrix = 1 / (1 + knn_graph.toarray())
            # Handle division by zero
            affinity_matrix[np.isinf(affinity_matrix)] = 0
        
        labels = clustering.fit_predict(affinity_matrix)
        
    elif method == 'agglomerative':
        # Agglomerative clustering on KNN graph
        print(f"Applying Agglomerative Clustering with {n_clusters} clusters")
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            connectivity=knn_graph,
            linkage='average'
        )
        labels = clustering.fit_predict(content_embeddings)
    
    else:
        raise ValueError(f"Unknown method: {method}. Choose 'spectral' or 'agglomerative'")
    
    n_clusters_found = len(set(labels))
    n_noise = 0  # KNN graph methods don't produce noise points
    
    print(f"KNN Graph Clustering ({method}): {n_clusters_found} clusters, {n_noise} noise points")
    print(f"Cluster distribution: {Counter(labels)}")
    
    return labels, n_clusters_found, n_noise

if __name__ == "__main__":
    from json_yaml_IO import *
    high_priority = read_json('jd_intent_results.json')['high_priority']
    unique_high_priority = deduplicate_content(high_priority)
    unique_high_priority, high_priority_embeddings = embed_content(unique_high_priority, None)
    optimal_n_clusters = find_optimal_clusters(high_priority_embeddings)
    
    # DBSCAN clustering
    print("=" * 50)
    print("DBSCAN Clustering")
    print("=" * 50)
    best_labels, best_n_clusters, n_noise = cluster_with_dbscan(optimal_n_clusters, high_priority_embeddings)
    print(best_labels[:10])
    print(unique_high_priority[:10])
    print(f'length of unique_high_priority: {len(unique_high_priority)}')
    print(f'length of high_priority_embeddings: {len(high_priority_embeddings)}')
    print(f'length of best_labels: {len(best_labels)}')
    print(f'best_n_clusters: {best_n_clusters}')
    print(f'n_noise: {n_noise}')
    print(Counter(best_labels))
    print(f'length of Counter(best_labels): {len(Counter(best_labels))}')
    
    # KNN Graph clustering - Spectral method
    print("\n" + "=" * 50)
    print("KNN Graph Clustering (Spectral)")
    print("=" * 50)
    knn_labels_spectral, knn_n_clusters_spectral, knn_noise_spectral = cluster_with_knngraph(
        high_priority_embeddings,
        n_neighbors=None,  # auto-calculate
        n_clusters=optimal_n_clusters,
        method='spectral',
        metric='cosine',
        mode='connectivity'
    )
    print(f'KNN Spectral - n_clusters: {knn_n_clusters_spectral}, noise: {knn_noise_spectral}')
    
    # KNN Graph clustering - Agglomerative method
    print("\n" + "=" * 50)
    print("KNN Graph Clustering (Agglomerative)")
    print("=" * 50)
    knn_labels_agg, knn_n_clusters_agg, knn_noise_agg = cluster_with_knngraph(
        high_priority_embeddings,
        n_neighbors=None,  # auto-calculate
        n_clusters=optimal_n_clusters,
        method='agglomerative',
        metric='cosine',
        mode='connectivity'
    )
    print(f'KNN Agglomerative - n_clusters: {knn_n_clusters_agg}, noise: {knn_noise_agg}')