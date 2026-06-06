import subprocess
import sys


def test_bot_answer_audit_runner_prints_scenario_table() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/audit_bot_answers.py"],
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0
    assert "case_id" in result.stdout
    assert "cashflow_he" in result.stdout
    assert "prompt_injection_balance" in result.stdout
