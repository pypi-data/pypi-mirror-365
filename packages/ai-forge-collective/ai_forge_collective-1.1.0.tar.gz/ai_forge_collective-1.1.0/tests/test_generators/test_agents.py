# This test file has been updated as part of MVP scope cleanup.
# The AgentsGenerator was a Phase 2 feature that is not part of the MVP.
# The MVP focuses on a universal starter template only.

import pytest


def test_agents_generator_removed():
    """Test that AgentsGenerator is not available in MVP scope."""
    # This test confirms the AgentsGenerator has been properly removed
    # as part of MVP scope cleanup - should raise ImportError
    with pytest.raises(
        ImportError, match="AgentsGenerator has been removed in MVP scope cleanup"
    ):
        from ai_forge.generators import agents  # noqa: F401
