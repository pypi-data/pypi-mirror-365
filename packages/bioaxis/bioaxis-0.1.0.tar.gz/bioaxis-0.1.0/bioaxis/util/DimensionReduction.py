

class DimensionReduction:

    def get_2d_coords(
            self,
            feature,
            met='tsne'
    ):
        from sklearn.decomposition import PCA
        if met == 'tsne':
            from sklearn.manifold import TSNE
            pca = PCA(n_components=50)
            pcs = pca.fit_transform(feature)
            tsne = TSNE(n_components=2, init='pca', learning_rate='auto')
            fea_transformed = tsne.fit_transform(pcs)
            x_coord = fea_transformed[:, 0]
            y_coord = fea_transformed[:, 1]
        elif met == 'umap':
            pass
        else:
            pass
        return x_coord, y_coord