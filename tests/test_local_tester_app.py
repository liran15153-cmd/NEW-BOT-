from pathlib import Path

from tests.api_test_client import get


def test_tester_page_is_served() -> None:
    response = get("/tester")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "BOT V1 Tester" in response.text
    assert 'id="message-input"' in response.text
    assert 'id="file-input"' in response.text


def test_tester_static_assets_are_served() -> None:
    script_response = get("/tester/assets/tester.js")
    style_response = get("/tester/assets/tester.css")

    assert script_response.status_code == 200
    assert "sendMessage" in script_response.text
    assert style_response.status_code == 200
    assert ".app-shell" in style_response.text


def test_tester_file_panel_is_local_sandbox_only() -> None:
    script_source = Path("app/tester/assets/tester.js").read_text(encoding="utf-8")

    assert "FileReader" in script_source
    assert "/upload" not in script_source
    assert "/files" not in script_source


def test_windows_tester_launcher_targets_local_tester() -> None:
    script_source = Path("scripts/start_tester.ps1").read_text(encoding="utf-8")

    assert "app.main:app" in script_source
    assert "$PreferredPort = 8000" in script_source
    assert "/tester" in script_source
    assert "Start-Process" in script_source


