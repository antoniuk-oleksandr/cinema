import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skip(
    reason="Enable when integration dependencies and Docker test execution are requested"
)
def test_postgres_redis_rabbitmq_containers_are_available() -> None:
    """Reserved smoke test for Testcontainers-backed infrastructure."""
    assert True
