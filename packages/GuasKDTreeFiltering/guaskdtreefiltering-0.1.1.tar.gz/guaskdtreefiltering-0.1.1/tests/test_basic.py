"""
Basic tests for GuasKD package.
"""

import pytest


def test_import():
    """Test that we can import the package."""
    try:
        from GuasKD import Filtering
        assert True
    except ImportError:
        pytest.fail("Could not import Filtering")


if __name__ == "__main__":
    pytest.main([__file__])
