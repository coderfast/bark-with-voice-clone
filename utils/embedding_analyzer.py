"""
Embedding Analyzer - Speaker Embedding Visualizations

Generates visualizations for voice cloning evaluation:
- UMAP Projection (_umap.png)
- Similarity Heatmap (_similarity.png)
"""

import os
from typing import Optional, List

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

STYLE = {
    'bg': '#0e1117', 'panel': '#161b22', 'grid': '#21262d',
    'text': '#c9d1d9', 'text_dim': '#8b949e',
}


def _apply_style(fig, ax):
    fig.patch.set_facecolor(STYLE['bg'])
    ax.set_facecolor(STYLE['panel'])
    ax.tick_params(colors=STYLE['text_dim'], which='both')
    ax.xaxis.label.set_color(STYLE['text'])
    ax.yaxis.label.set_color(STYLE['text'])
    ax.title.set_color(STYLE['text'])
    ax.grid(True, alpha=0.15, color=STYLE['grid'])
    for spine in ax.spines.values():
        spine.set_color(STYLE['grid'])


# ── 1. UMAP PROJECTION ─────────────────────────────────────────────────────

def generate_embedding_umap(
    embeddings: np.ndarray,
    filepath: str,
    labels: Optional[List[str]] = None,
    figsize: tuple = (10, 8),
    title: Optional[str] = None,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
) -> str:
    """Generate UMAP projection of speaker embeddings.

    Shows clustering of speaker embeddings in 2D space.
    Points from the same speaker should cluster together.

    Useful for evaluating voice cloning quality: does the
    cloned voice's embedding cluster with the target speaker?

    Args:
        embeddings: Array of shape (n_samples, n_features)
        filepath: Output file path
        labels: Optional list of labels per embedding
        figsize: Figure size
        title: Plot title
        n_neighbors: UMAP n_neighbors parameter
        min_dist: UMAP min_dist parameter

    Returns:
        Path to saved plot
    """
    import umap

    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)

    n_samples = embeddings.shape[0]

    # Adjust n_neighbors if needed
    n_neighbors = min(n_neighbors, n_samples - 1)
    if n_neighbors < 2:
        n_neighbors = 2

    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=2,
        metric='cosine',
        random_state=42,
    )
    embedding_2d = reducer.fit_transform(embeddings)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    # Color by label
    if labels is not None:
        unique_labels = list(set(labels))
        cmap = plt.cm.get_cmap('tab10', len(unique_labels))
        for i, label in enumerate(unique_labels):
            mask = [l == label for l in labels]
            ax.scatter(
                embedding_2d[mask, 0], embedding_2d[mask, 1],
                c=[cmap(i)], label=label, s=100, alpha=0.8, edgecolors='white',
                linewidths=0.5,
            )
        ax.legend(fontsize=8, facecolor=STYLE['panel'],
                  edgecolor=STYLE['grid'], labelcolor=STYLE['text'])
    else:
        ax.scatter(
            embedding_2d[:, 0], embedding_2d[:, 1],
            c=STYLE['text'], s=100, alpha=0.8, edgecolors='white',
            linewidths=0.5,
        )

    ax.set_xlabel('UMAP 1')
    ax.set_ylabel('UMAP 2')
    ax.set_title(title or 'Speaker Embedding UMAP Projection')

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 2. SIMILARITY HEATMAP ──────────────────────────────────────────────────

def generate_similarity_heatmap(
    embeddings: np.ndarray,
    filepath: str,
    labels: Optional[List[str]] = None,
    figsize: tuple = (10, 8),
    title: Optional[str] = None,
) -> str:
    """Generate cosine similarity heatmap between speaker embeddings.

    Shows pairwise similarity between all embeddings.
    High diagonal values indicate self-similarity.
    High off-diagonal values between different speakers indicate cloning quality.

    Args:
        embeddings: Array of shape (n_samples, n_features)
        filepath: Output file path
        labels: Optional list of labels per embedding
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    from sklearn.metrics.pairwise import cosine_similarity

    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)

    # Compute cosine similarity matrix
    sim_matrix = cosine_similarity(embeddings)
    n = sim_matrix.shape[0]

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    fig.patch.set_facecolor(STYLE['bg'])
    ax.set_facecolor(STYLE['panel'])

    # Plot heatmap
    cmap = plt.cm.RdYlGn
    im = ax.imshow(sim_matrix, cmap=cmap, vmin=-1, vmax=1, aspect='auto')

    # Add labels
    if labels is not None:
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8,
                           color=STYLE['text'])
        ax.set_yticklabels(labels, fontsize=8, color=STYLE['text'])
    else:
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels([str(i) for i in range(n)], fontsize=8,
                           color=STYLE['text'])
        ax.set_yticklabels([str(i) for i in range(n)], fontsize=8,
                           color=STYLE['text'])

    # Add similarity values
    for i in range(n):
        for j in range(n):
            color = 'white' if sim_matrix[i, j] < 0.5 else 'black'
            ax.text(j, i, f'{sim_matrix[i, j]:.2f}', ha='center', va='center',
                    fontsize=7, color=color)

    cbar = fig.colorbar(im, ax=ax, label='Cosine Similarity')
    cbar.ax.yaxis.label.set_color(STYLE['text'])
    cbar.ax.tick_params(colors=STYLE['text_dim'])

    ax.set_title(title or 'Speaker Embedding Similarity')
    ax.set_xlabel('Embedding')
    ax.set_ylabel('Embedding')

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath
