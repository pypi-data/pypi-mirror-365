"""
Integration tests for GuasKD package with real image processing scenarios.
"""

import pytest
import numpy as np
from GuasKD import Filtering


class TestFilteringIntegration:
    """Integration tests for Filtering with synthetic images."""

    def test_simple_synthetic_image(self):
        """Test bilateral filtering on a simple synthetic image."""
        # Test with fixed bilateral filter - proper weight normalization

        # Test on a simple image first
        simple_image = np.zeros((50, 50, 3), dtype=np.uint8)
        simple_image[20:30, 20:30] = [255, 0, 0]  # Red square
        simple_image[25:35, 25:35] = [0, 255, 0]  # Green square overlapping

        # Add some noise
        noise = np.random.randint(-5, 5, simple_image.shape) * 6
        noisy_simple = np.clip(
            simple_image.astype(int) + noise, 0, 255
        ).astype(np.uint8)

        # Normalize image to [0, 1] if needed
        if noisy_simple.max() > 1.0:
            noisy_simple = noisy_simple.astype(np.float32) / 255.0

        print("Testing on simple synthetic image...")
        s = Filtering(
            sigma_spatial=0.5,
            sigma_color=0.1,
            sigma_b=0.2,
            leaf_size=4,
            samples=16
        )
        filtered_simple = s(noisy_simple, noisy_simple, mode='Bilateral')

        # Assertions
        assert filtered_simple.shape == noisy_simple.shape
        assert filtered_simple.dtype == noisy_simple.dtype
        assert not np.array_equal(filtered_simple, noisy_simple)  # Should be filtered

        # Check that filtering preserves the overall structure
        # The filtered image should have similar mean values
        original_mean = np.mean(noisy_simple)
        filtered_mean = np.mean(filtered_simple)
        # Should be close
        assert abs(original_mean - filtered_mean) < 0.1

    def test_noise_reduction(self):
        """Test that bilateral filtering reduces noise."""
        # Create a clean image
        clean_image = np.zeros((30, 30, 3), dtype=np.float32)
        clean_image[10:20, 10:20] = [1.0, 0.5, 0.0]  # Orange rectangle

        # Add significant noise
        noise_level = 0.3
        noisy_image = clean_image + np.random.normal(
            0, noise_level, clean_image.shape
        )
        noisy_image = np.clip(noisy_image, 0, 1)

        # Apply bilateral filtering
        bf = Filtering(
            sigma_spatial=1.0,
            sigma_color=0.2,
            sigma_b=0.1,
            leaf_size=5,
            samples=20
        )
        filtered_image = bf(noisy_image, noisy_image, mode='Bilateral')

        # Calculate noise levels
        original_noise = np.std(noisy_image - clean_image)
        filtered_noise = np.std(filtered_image - clean_image)

        # Filtered image should have less noise
        assert filtered_noise < original_noise

        # But should still preserve edges
        # Check that the rectangle is still visible
        rect_region = filtered_image[10:20, 10:20]
        background_region = filtered_image[5:10, 5:10]

        # The rectangle should still be distinguishable from background
        rect_mean = np.mean(rect_region)
        bg_mean = np.mean(background_region)
        # Should be distinguishable
        assert abs(rect_mean - bg_mean) > 0.1

    def test_edge_preservation(self):
        """Test that bilateral filtering preserves edges."""
        # Create an image with sharp edges
        edge_image = np.zeros((40, 40, 3), dtype=np.float32)
        edge_image[15:25, 15:25] = [1.0, 1.0, 1.0]  # White square

        # Add some noise
        noisy_edge = edge_image + np.random.normal(0, 0.1, edge_image.shape)
        noisy_edge = np.clip(noisy_edge, 0, 1)

        # Apply bilateral filtering
        bf = Filtering(
            sigma_spatial=0.8,
            sigma_color=0.15,
            sigma_b=0.05,
            leaf_size=6,
            samples=24
        )
        filtered_edge = bf(noisy_edge, noisy_edge, mode='Bilateral')

        # Check edge preservation
        # The difference between inside and outside the square should still be significant
        inside_square = filtered_edge[15:25, 15:25]
        outside_square = filtered_edge[5:15, 5:15]

        inside_mean = np.mean(inside_square)
        outside_mean = np.mean(outside_square)

        # The edge should still be visible
        assert abs(inside_mean - outside_mean) > 0.3

    def test_spatial_filtering_mode(self):
        """Test spatial filtering mode."""
        # Create a test image
        test_image = np.random.rand(20, 20, 3).astype(np.float32)

        # Apply spatial filtering
        bf = Filtering(
            sigma_spatial=1.0,
            sigma_color=0.1,
            leaf_size=4,
            samples=12
        )
        filtered_spatial = bf(test_image, test_image, mode='Spatial')

        # Check results
        assert filtered_spatial.shape == test_image.shape
        assert filtered_spatial.dtype == test_image.dtype
        assert not np.array_equal(filtered_spatial, test_image)


if __name__ == "__main__":
    pytest.main([__file__])
