import seaborn as sns
from matplotlib.figure import Figure

def plot_correlation_matrix(df):
    df = df.loc[:, (df != df.iloc[0]).any()]
    df = df.loc[:, df.mean().abs() > 1e-4]
    spearman_corr = df.corr(method='spearman')
    pearson_corr = df.corr(method='pearson')

    fig = Figure(figsize=(15, 6))
    axes = fig.subplots(nrows=1, ncols=2)
    sns.heatmap(spearman_corr, ax=axes[0], cmap='coolwarm', annot=True, fmt=".2f", vmin=-1, vmax=1)
    sns.heatmap(pearson_corr, ax=axes[1], cmap='coolwarm', annot=True, fmt=".2f", vmin=-1, vmax=1)
    axes[0].set_title('Spearman Correlation')
    axes[1].set_title('Pearson Correlation')

    fig.tight_layout()
    return fig

