from pathlib import Path

import pytest

# pytest_plugins = (
#     "tests.fixtures.api_fixtures",
#     "tests.fixtures.model_fixtures",
#     "tests.fixtures.mock_fixtures",
# )


@pytest.fixture
def root_test_dir():
    return Path(__file__).parent
