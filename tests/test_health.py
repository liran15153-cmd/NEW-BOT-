from tests.support import get


def test_health_returns_ok_status() -> None:
    response = get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "financial-wellness-assistant",
    }
