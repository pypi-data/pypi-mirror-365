import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score
import os

def same_features_different_label_skew(
    df, label_col, dataset_name='SFDL_DB', output_dir='.', max_k=10, k_optimal=None
):
    """
    Perform Same Features, Different Label Skew using KMeans with optional manual cluster count.

    Parameters:
        df (pd.DataFrame): The full dataset.
        label_col (str): Name of the label column to drop before clustering.
        dataset_name (str): A name identifier for the output files.
        output_dir (str): Where to save the client CSV files.
        max_k (int): Max clusters to search over if k_optimal is None.
        k_optimal (int or None): If given, use this number of clusters directly.
    """
    X = df.drop(columns=[label_col])
    y = df[label_col]

    # Determine k
    if k_optimal is None:
        db_scores = []
        k_range = range(2, max_k + 1)
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=0)
            labels = kmeans.fit_predict(X)
            score = davies_bouldin_score(X, labels)
            db_scores.append(score)

        plt.figure(figsize=(8, 5))
        plt.plot(k_range, db_scores, marker='o', linestyle='--')
        plt.title('Davies-Bouldin Score for Optimal k')
        plt.xlabel('Number of Clusters (k)')
        plt.ylabel('Davies-Bouldin Score')
        plt.xticks(k_range)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        k_optimal = k_range[db_scores.index(min(db_scores))]
        print(f"\n[Auto] The optimal number of clusters (k) is: {k_optimal}")
    else:
        print(f"\n[Manual] Using provided number of clusters (k): {k_optimal}")

    # Apply KMeans
    kmeans = KMeans(n_clusters=k_optimal, random_state=0)
    df['cluster'] = kmeans.fit_predict(X)

    client_data = [[] for _ in range(k_optimal)]
    for cluster_id in range(k_optimal):
        cluster_data = df[df['cluster'] == cluster_id]
        n_samples_per_client = len(cluster_data) // k_optimal
        for i in range(k_optimal):
            start = i * n_samples_per_client
            end = (i + 1) * n_samples_per_client
            client_data[i].append(cluster_data.iloc[start:end])

    os.makedirs(output_dir, exist_ok=True)
    for i, client_chunks in enumerate(client_data):
        client_df = pd.concat(client_chunks).drop(columns=['cluster'])
        filename = os.path.join(output_dir, f'client{i+1}_{dataset_name}.csv')
        client_df.to_csv(filename, index=False)
        print(f"Saved {filename} with shape: {client_df.shape}")
