import numpy as np
from functools import lru_cache
from math import erf, sqrt, floor
from tqdm import tqdm  # type: ignore
import typing
from concurrent.futures import ThreadPoolExecutor


def cdf_approx(x : float) -> float:
    return 0.5 * (1 + erf(x / sqrt(2)))


def urand() -> float:
    return np.random.rand()


class GaussianKDTreeNode:
    def __init__(self, indices : np.ndarray, depth : int, feature_vectors : np.ndarray, values : np.ndarray, leaf_size : int = 10, node_index : int = 1):
        self.indices = indices
        self.depth = depth
        self.left = None
        self.right = None
        self.is_leaf = False
        self.position = None
        self.mean_value = None
        self.d = None
        self.min = None
        self.max = None
        self.cut = None

        if len(indices) <= leaf_size:
            self.is_leaf = True
            self.position = np.mean(feature_vectors[indices], axis=0)
            self.mean_value = np.mean(values[indices], axis=0)
        else:
            self.d = depth % feature_vectors.shape[1]
            sorted_idx = indices[np.argsort(feature_vectors[indices, self.d])]
            mid = len(sorted_idx) // 2
            self.cut = feature_vectors[sorted_idx[mid], self.d]
            self.min = feature_vectors[sorted_idx[0], self.d]
            self.max = feature_vectors[sorted_idx[-1], self.d]
            self.left = GaussianKDTreeNode(sorted_idx[:mid], depth+1, feature_vectors, values, leaf_size, node_index + 1)
            self.right = GaussianKDTreeNode(sorted_idx[mid:], depth+1, feature_vectors, values, leaf_size, node_index + 2)

    def query(self, q: np.ndarray, sigma: float, samples: int, p: float = 1.0, min_samples: int = 4) -> list:
        results = []

        if self.is_leaf:
            distance = np.linalg.norm(q - self.position)
            correct_p = np.exp(-distance**2 / (2 * sigma**2))
            results.append(Result(self, samples * correct_p / p))
            return results

        cdf_min = cdf_approx((self.min - q[self.d]) / sigma)
        cdf_max = cdf_approx((self.max - q[self.d]) / sigma)
        cdf_cut = cdf_approx((self.cut - q[self.d]) / sigma)
        p_left = (cdf_cut - cdf_min) / (cdf_max - cdf_min + 1e-12)
        expected_left = p_left * samples
        samples_left = int(floor(expected_left))
        samples_right = int(floor(samples - expected_left))
        if samples_left + samples_right < samples:
            if urand() < expected_left - samples_left:
                samples_left += 1
            else:
                samples_right += 1

        total_allocated = samples_left + samples_right
        if total_allocated < min_samples:
            extra = min_samples - total_allocated
            for _ in range(extra):
                if urand() < p_left:
                    samples_left += 1
                else:
                    samples_right += 1

        if samples_left > 0:
            if self.left is None:
                raise ValueError("Left child is None but samples_left > 0")
            results.extend(self.left.query(q, sigma, samples_left, p * p_left, min_samples))
        if samples_right > 0:
            if self.right is None:
                raise ValueError("Right child is None but samples_right > 0")
            results.extend(self.right.query(q, sigma, samples_right, p * (1 - p_left), min_samples))

        return results


class Result:
    def __init__(self, node : GaussianKDTreeNode, weight : float):
        self.node = node
        self.weight = weight


# Example usage in Filtering:
class Filtering:
    def __init__(self,
                 sigma_spatial : float = 1.0,
                 sigma_color : float = 0.1,
                 sigma_b : float = 0.0,
                 samples : int = 32,
                 leaf_size : int = 10,
                 fallback_mode : str = 'nearest',
                 min_samples: int = 4):
        self.sigma_spatial = sigma_spatial
        self.sigma_color = sigma_color
        self.sigma_b = sigma_b
        self.sigma_s = sqrt(1 - sigma_b**2)/2
        self.samples = samples
        self.leaf_size = leaf_size
        self.use_fallback = fallback_mode
        self.min_samples = min_samples

    def preprocess(self, image : np.ndarray, mode : str) -> np.ndarray:
        """ Preprocess the image to create feature vectors.

        Parameters
        ----------
        image : np.ndarray
            Input image array.
        mode : str
            Preprocessing mode, either 'Bilateral' or 'Spatial'.

        Returns
        -------
        np.ndarray
            Feature vectors for the image.

        Raises
        ------
        ValueError
            If the image shape is not 3D or mode is not recognized.
        """
        if len(image.shape) != 3:
            raise ValueError("Image must be a 3D array (C, H, W)")
        H, W, C = image.shape
        if mode == 'Bilateral':
            x, y = np.meshgrid(np.arange(W), np.arange(H))
            position_vectors = np.zeros((H, W, C+2))
            position_vectors[..., 0] = x / (W*self.sigma_spatial)
            position_vectors[..., 1] = y / (H*self.sigma_spatial)
            position_vectors[..., 2:] = image / (self.sigma_color)
            return position_vectors.reshape(-1 , C+2)
        elif mode == 'Spatial':
            x, y = np.meshgrid(np.arange(W), np.arange(H))
            position_vectors = np.zeros((H, W, 2))
            position_vectors[..., 0] = x / (W*self.sigma_spatial)
            position_vectors[..., 1] = y / (H*self.sigma_spatial)
            return position_vectors.reshape(-1, 2)
        else:
            raise ValueError(f"Unknown mode '{mode}'. Supported modes are 'Bilateral' and 'Spatial'.")

    def build_gaussian_kdtree(self, feature_vectors : np.ndarray, values : np.ndarray, leaf_size : int = 8) -> GaussianKDTreeNode:
        indices = np.arange(feature_vectors.shape[0])
        return GaussianKDTreeNode(indices, 0, feature_vectors, values, leaf_size)

    def splat(self, query: np.ndarray, tree: GaussianKDTreeNode, sigma : float, samples : int = 32) -> typing.Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Splat a single query point onto the tree nodes.
        Returns:
            node_positions: positions of the leaf nodes
            node_values: accumulated values per node (weighted)
            node_weights: accumulated weights per node
        """
        results = tree.query(query, sigma, samples)
        node_positions = np.array([leaf.node.position for leaf in results])
        node_weights = np.array([result.weight for result in results])
        node_mean_values = np.array([result.node.mean_value for result in results])
        total_weight = np.sum(node_weights)
        if total_weight > 0:
            node_weights /= total_weight
        node_values = node_weights[:, None] * node_mean_values
        return node_positions, node_values, node_weights

    @lru_cache(maxsize=None)
    def gaussian_weight(self, distance: float, sigma: float) -> float:
        """
        Compute Gaussian weight for a given distance and sigma.

        Args:
            distance (float): Distance between points.
            sigma (float): Standard deviation for Gaussian kernel.

        Returns:
            float: Gaussian weight.
        """
        return float(np.exp(-distance**2 / (2 * sigma**2)))

    def blur(self, node_positions: np.ndarray, node_values: np.ndarray, node_weights: np.ndarray, sigma: float) -> typing.Tuple[np.ndarray, np.ndarray]:
        """
        Apply Gaussian blur to the values in the leaf nodes.

        Args:
            node_positions (np.ndarray): Positions of the leaf nodes (num_nodes, feature_dim).
            node_values (np.ndarray): Weighted values accumulated at the leaf nodes (num_nodes, value_dim).
            node_weights (np.ndarray): Weights accumulated at the leaf nodes (num_nodes,).
            sigma (float): Standard deviation for the Gaussian kernel.

        Returns:
            tuple: (blurred_values, blurred_weights) - normalized blurred values and accumulated weights
        """
        distances = np.linalg.norm(node_positions[:, None, :] - node_positions[None, :, :], axis=2)
        blur_weights = np.exp(-distances**2 / (2 * sigma**2))

        # Apply blur to both values and weights
        blurred_values = blur_weights @ node_values
        blurred_weights = blur_weights @ node_weights

        # Normalize by accumulated weights to get proper averages
        # Avoid division by zero
        blurred_weights = np.maximum(blurred_weights, 1e-8)
        normalized_values = blurred_values / blurred_weights[:, None]

        return normalized_values, blurred_weights

    def slice(self, query: np.ndarray, blurred_values: np.ndarray, blurred_weights: np.ndarray, node_positions: np.ndarray, sigma: float) -> np.ndarray:
        """
        Slice the image at a specific query point and interpolate the blurred values.

        Args:
            query (np.ndarray): Query point in feature space (1D array).
            blurred_values (np.ndarray): Blurred values at the leaf nodes (num_nodes, value_dim).
            blurred_weights (np.ndarray): Blurred weights at the leaf nodes (num_nodes,).
            node_positions (np.ndarray): Positions of the leaf nodes (num_nodes, feature_dim).
            sigma (float): Standard deviation for Gaussian kernel.

        Returns:
            np.ndarray: Interpolated pixel value at the query point.
        """
        distances = np.linalg.norm(query[None, :] - node_positions, axis=1)
        weights = np.exp(-distances**2 / (2 * sigma**2))

        # Interpolate both the blurred values and the blurred weights
        sliced_value = np.sum((weights * blurred_weights)[:, None] * blurred_values, axis=0)
        sliced_weight = np.sum(weights * blurred_weights)

        # Normalize the sliced value by the sliced weight
        if sliced_weight > 1e-4:
            return np.asarray(sliced_value / sliced_weight)
        else:
            if self.use_fallback == 'nearest':
                nearest_idx = np.argmin(distances)
                return blurred_values[nearest_idx]
            # elif self.use_fallback == 'original':
            #     return original_value
            else:
                return np.asarray(sliced_value / sliced_weight)

    def process_feature_vector(self, i: int, fv: np.ndarray) -> typing.Tuple[int, np.ndarray]:
        """
        Process a single feature vector for filtering.

        Args:
            i (int): Index of the feature vector.
            fv (np.ndarray): Feature vector.
            v (np.ndarray): Value vector to be filtered.

        Returns:
            typing.Tuple[int, np.ndarray]: Index and filtered value.
        """
        node_positions, node_values, node_weights = self.splat(fv, self.root, self.sigma_s, self.samples)
        blurred_values, blurred_weights = self.blur(node_positions, node_values, node_weights, self.sigma_b)
        return i, self.slice(fv, blurred_values, blurred_weights, node_positions, self.sigma_s)

    def __call__(self, image: np.ndarray, values: np.ndarray, mode : typing.Literal["Spatial", "Bilateral"]) -> np.ndarray:
        """
        Call the instance to apply filtering basssed on apploed mode.

        Args:
            image (np.ndarray): Input image to build the feature space from.
            values (np.ndarray): Values to be filtered.
            mode (typing.Literal["Spatial", "Bilateral"]): Filtering mode.

        Returns:
            np.ndarray: Filtered image.
        """
        self.feature_vectors = self.preprocess(image, mode)
        self.values = values.reshape(-1, values.shape[-1])
        self.root = self.build_gaussian_kdtree(self.feature_vectors, self.values, self.leaf_size)
        filtered_values = np.zeros_like(self.values, dtype=self.values.dtype)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_feature_vector, i, fv) for i, fv in enumerate(self.feature_vectors)]
            for future in tqdm(futures, desc="Filtering", total=len(futures)):
                i, result = future.result()
                filtered_values[i] = result

        filtered_image = filtered_values.reshape(values.shape)
        return filtered_image.astype(values.dtype)
