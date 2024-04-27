# -*- coding: utf-8 -*-
"""StockClustering.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1VNMKfLgMO_Yazpghhf7-ARvuUliODyja
"""

# this will help in making the Python code more structured automatically (good coding practice)
#%load_ext nb_black

# Libraries to help with reading and manipulating data
import numpy as np
import pandas as pd

# Libraries to help with data visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Removes the limit for the number of displayed columns
pd.set_option("display.max_columns", None)
# Sets the limit for the number of displayed rows
pd.set_option("display.max_rows", 200)

# to scale the data using z-score
from sklearn.preprocessing import StandardScaler

# to compute distances
from scipy.spatial.distance import pdist
from scipy.spatial.distance import cdist

# to perform k-means clustering and compute silhouette scores
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# to visualize the elbow curve and silhouette scores
from yellowbrick.cluster import KElbowVisualizer, SilhouetteVisualizer

# to perform hierarchical clustering, compute cophenetic correlation, and create dendrograms
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage, cophenet

# to perform PCA
from sklearn.decomposition import PCA

"""# **Data Overview dan Data Preprocessing**"""

# Membaca file CSV menjadi DataFrame
data = pd.read_csv("stock_data.csv")

# Menampilkan DataFrame
print(data)

data.shape

df=data.copy()

df.info()

"""Exploration Data Analysis:

No missing values in the dataframe
Four columns contain objects. Two of these columns are categorical.
Eleven numerical values
"""

df.isnull().sum()

df.describe().T

df.duplicated().sum()

#membuat heatmap dari korelasi antara fitur-fitur numerik dalam sebuah DataFrame
num_cols = df.select_dtypes(include=np.number).columns.tolist()

plt.figure(figsize=(15, 7))
sns.heatmap(
    df[num_cols].corr(), annot=True, vmin=-1, vmax=1, fmt=".2f", cmap="Spectral"
)
plt.show()

"""# **Data Exploration dan Data Analysis**"""

# function to plot a boxplot and a histogram along the same scale.
def histogram_boxplot(data, feature, figsize=(12, 7), kde=False, bins=None):
    """
    Boxplot and histogram combined

    data: dataframe
    feature: dataframe column
    figsize: size of figure (default (12,7))
    kde: whether to the show density curve (default False)
    bins: number of bins for histogram (default None)
    """
    f2, (ax_box2, ax_hist2) = plt.subplots(
        nrows=2,  # Number of rows of the subplot grid= 2
        sharex=True,  # x-axis will be shared among all subplots
        gridspec_kw={"height_ratios": (0.25, 0.75)},
        figsize=figsize,
    )  # creating the 2 subplots
    sns.boxplot(
        data=data, x=feature, ax=ax_box2, showmeans=True, color="violet"
    )  # boxplot will be created and a star will indicate the mean value of the column
    sns.histplot(
        data=data, x=feature, kde=kde, ax=ax_hist2, bins=bins, palette="winter"
    ) if bins else sns.histplot(
        data=data, x=feature, kde=kde, ax=ax_hist2
    )  # For histogram
    ax_hist2.axvline(
        data[feature].mean(), color="green", linestyle="--"
    )  # Add mean to the histogram
    ax_hist2.axvline(
        data[feature].median(), color="black", linestyle="-"
    )  # Add median to the histogram

def stacked_barplot(data, predictor, target):
    """
    Print the category counts and plot a stacked bar chart

    data: dataframe
    predictor: independent variable
    target: target variable
    """
    count = data[predictor].nunique()
    sorter = data[target].value_counts().index[-1]
    tab1 = pd.crosstab(data[predictor], data[target], margins=True).sort_values(
        by=sorter, ascending=False
    )
    print(tab1)
    print("-" * 120)
    tab = pd.crosstab(data[predictor], data[target], normalize="index").sort_values(
        by=sorter, ascending=False
    )
    tab.plot(kind="bar", stacked=True, figsize=(count + 5, 5))
    plt.legend(
        loc="lower left", frameon=False,
    )
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.show()

### function to plot distributions wrt target


def distribution_plot_wrt_target(data, predictor, target):

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    target_uniq = data[target].unique()

    axs[0, 0].set_title("Distribution of target for target=" + str(target_uniq[0]))
    sns.histplot(
        data=data[data[target] == target_uniq[0]],
        x=predictor,
        kde=True,
        ax=axs[0, 0],
        color="teal",
        stat="density",
    )

    axs[0, 1].set_title("Distribution of target for target=" + str(target_uniq[1]))
    sns.histplot(
        data=data[data[target] == target_uniq[1]],
        x=predictor,
        kde=True,
        ax=axs[0, 1],
        color="orange",
        stat="density",
    )

    axs[1, 0].set_title("Boxplot w.r.t target")
    sns.boxplot(data=data, x=target, y=predictor, ax=axs[1, 0], palette="gist_rainbow")

    axs[1, 1].set_title("Boxplot (without outliers) w.r.t target")
    sns.boxplot(
        data=data,
        x=target,
        y=predictor,
        ax=axs[1, 1],
        showfliers=False,
        palette="gist_rainbow",
    )

    plt.tight_layout()
    plt.show()

#Menentukan Mean dan Median dari Current Price
histogram_boxplot(df,"Current Price")

print("Mean:",round(df["Current Price"].mean(),2))
print("Median:",round(df["Current Price"].median(),2))

df.groupby(["GICS Sector"])["Price Change"].mean()

# Dataframe telah dikelompokkan dan rata-rata dari kolom "Price Change" dihitung sebelumnya
# Simpan hasil groupby ke dalam variabel baru
grouped_data = df.groupby(["GICS Sector"])["Price Change"].mean().reset_index()

# Buat plot menggunakan seaborn
plt.figure(figsize=(10, 6))
sns.barplot(x="Price Change", y="GICS Sector", data=grouped_data, palette="viridis")
plt.title("Rata-rata Perubahan Harga Berdasarkan Sektor")
plt.xlabel("Rata-rata Perubahan Harga")
plt.ylabel("Sektor")
plt.show()

distribution_plot_wrt_target(df, "GICS Sector", "Cash Ratio")

test = df.groupby(["GICS Sector"], as_index = False)["Cash Ratio"].mean().sort_values(by = "Cash Ratio", ascending = False)

histogram_boxplot(test, "Cash Ratio")

print(test)
print("Mean:", test["Cash Ratio"].mean())
print("Median:", test["Cash Ratio"].median())

distribution_plot_wrt_target(df, "GICS Sector", "P/E Ratio")

test = df.groupby(["GICS Sector"], as_index = False)["P/E Ratio"].mean().sort_values(by = "P/E Ratio", ascending = False)

histogram_boxplot(test, "P/E Ratio")

print(test)
print("Mean:", test["P/E Ratio"].mean())
print("Median:", test["P/E Ratio"].median())

"""# **Pembuatan Model K-Means Menggunakan Elbow Method**"""

# Scaling data sebelum clustering
scaler = StandardScaler()
subset = df[num_cols].copy()
subset_scaled = scaler.fit_transform(subset)

# Creating a dataframe from the scaled data
subset_scaled_df = pd.DataFrame(subset_scaled, columns=subset.columns)

# Copy the scaled dataframe to be used in K-means and Hierarchical Clustering
scaled_k = subset_scaled_df.copy()
scaled_h = subset_scaled_df.copy()

df_k = df.copy()

clusters = range(1, 9)
meanDistortions = []

for k in clusters:
    model = KMeans(n_clusters=k)
    model.fit(scaled_k)
    prediction = model.predict(scaled_k)
    distortion = (
        sum(
            np.min(cdist(scaled_k, model.cluster_centers_, "euclidean"), axis=1)
        )
        / scaled_k.shape[0]
    )

    meanDistortions.append(distortion)

    print("Number of Clusters:", k, "\tAverage Distortion:", distortion)

plt.plot(clusters, meanDistortions, "bx-")
plt.xlabel("k")
plt.ylabel("Average Distortion")
plt.title("Selecting k with the Elbow Method", fontsize=20)

sil_score = []
cluster_list = list(range(2, 10))
for n_clusters in cluster_list:
    clusterer = KMeans(n_clusters=n_clusters)
    preds = clusterer.fit_predict((scaled_k))
    # centers = clusterer.cluster_centers_
    score = silhouette_score(scaled_k, preds)
    sil_score.append(score)
    print("For n_clusters = {}, silhouette score is {}".format(n_clusters, score))

plt.plot(cluster_list, sil_score)

kmeans = KMeans(n_clusters=4, random_state=0)
kmeans.fit(scaled_k)

# adding kmeans cluster labels to the original dataframe
df_k["K_means_segments"] = kmeans.labels_

import pandas as pd

# Pastikan tipe data kolom ROE adalah numerik
df_k['ROE'] = pd.to_numeric(df_k['ROE'], errors='coerce')  # Mengubah ke numerik, nilai non-numerik akan menjadi NaN

# Kelompokkan berdasarkan K_means_segments dan hitung rata-rata serta jumlah baris dalam setiap kelompok
cluster_profile = df_k.groupby("K_means_segments").agg({
    'ROE': 'mean',       # Hitung rata-rata ROE
    'K_means_segments': 'size'  # Hitung jumlah baris (jumlah observasi) dalam setiap kelompok
})

# Ubah nama kolom hasil size menjadi count_in_each_segment
cluster_profile.rename(columns={'K_means_segments': 'count_in_each_segment'}, inplace=True)

# Tampilkan cluster profiles dengan highlight nilai maksimum dalam setiap kolom
styled_cluster_profile = cluster_profile.style.highlight_max(color="green", axis=0)
styled_cluster_profile

plt.figure(figsize=(15, 10))
plt.suptitle("Boxplot of numerical variables for each cluster")

for i, variable in enumerate(num_cols):
    # plt.subplot(2, 3, i + 1)
    sns.boxplot(data=df_k, x="K_means_segments", y=variable)
    plt.show()

plt.tight_layout(pad=2.0)

"""# **Hasil Nama Perusahaan di Setiap Cluster**"""

# Melihat setiap saham di tiap cluster yang telah di segmentasi
for cl in df_k["K_means_segments"].unique():
    print("In cluster {}, the following countries are present:".format(cl))
    print(df_k[df_k["K_means_segments"] == cl]["Security"].unique())
    print()

"""# **Evaluasi Model Silhotte Score, Inersia, DBI**"""

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.metrics import davies_bouldin_score
# Misalkan scaled_k adalah data yang telah di-preprocessing dan siap untuk digunakan
# scaled_k = ... (pastikan data sudah di-scale jika diperlukan)

# Inisialisasi dan latih model K-Means dengan jumlah kluster (n_clusters) = 4
kmeans = KMeans(n_clusters=4, random_state=0)
kmeans.fit(scaled_k)  # Lakukan clustering

# Lakukan prediksi klaster untuk setiap sampel dalam data
cluster_labels = kmeans.labels_

# Hitung nilai silhouette score
silhouette_avg = silhouette_score(scaled_k, cluster_labels)
print("Silhouette Score:", silhouette_avg)

inertia = kmeans.inertia_
print("Inertia:", inertia)

dbi = davies_bouldin_score(scaled_k, cluster_labels)
print("Davies-Bouldin Index (DBI):", dbi)

