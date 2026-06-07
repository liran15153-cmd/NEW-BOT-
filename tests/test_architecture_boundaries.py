from pathlib import Path


def test_hebrew_source_strings_are_utf8_and_contain_hebrew_characters() -> None:
    for path in (
        Path("app/ai/hebrew_response_builder.py"),
        Path("tests/test_chat_message_api.py"),
        Path("tests/test_financial_intent_and_parameter_parsing.py"),
        Path("tests/test_multiturn_conversation_flows.py"),
    ):
        text = path.read_text(encoding="utf-8")
        assert any("\u0590" <= character <= "\u05ff" for character in text), path


def test_source_files_do_not_contain_unicode_replacement_characters() -> None:
    for root in (Path("app"), Path("tests"), Path("docs")):
        for path in root.rglob("*"):
            if path.suffix not in {".py", ".md", ".html", ".css", ".js"}:
                continue
            text = path.read_text(encoding="utf-8")
            assert "\ufffd" not in text, path


def test_user_facing_hebrew_copy_is_only_in_response_builder_and_tests() -> None:
    allowed_hebrew_paths = {
        Path("app/ai/hebrew_response_builder.py"),
        Path("app/ai/assistant_intent_classifier.py"),
        Path("app/ai/financial_intent_parser.py"),
        Path("app/ai/financial_parameter_extractor.py"),
    }
    for path in Path("app").rglob("*.py"):
        if path in allowed_hebrew_paths:
            continue
        text = path.read_text(encoding="utf-8")
        assert not any("\u0590" <= character <= "\u05ff" for character in text), path


def test_decision_engine_contains_no_user_facing_copy() -> None:
    text = Path("app/financial/financial_decision_engine.py").read_text(encoding="utf-8")

    assert not any("\u0590" <= character <= "\u05ff" for character in text)
    assert "Based on" not in text
    assert "I need" not in text
    assert "אפשר" not in text


def test_python_module_names_are_descriptive() -> None:
    expected_paths = {
        Path("app/api/chat_message_api.py"),
        Path("app/api/financial_profile_api.py"),
        Path("app/api/health_check_api.py"),
        Path("app/api/local_tester_api.py"),
        Path("app/ai/assistant_answer_plan.py"),
        Path("app/ai/assistant_intent_classifier.py"),
        Path("app/ai/assistant_policy_schemas.py"),
        Path("app/ai/assistant_response_policy.py"),
        Path("app/ai/chat_message_schemas.py"),
        Path("app/ai/chat_router.py"),
        Path("app/ai/financial_context_readiness.py"),
        Path("app/ai/financial_intent_parser.py"),
        Path("app/ai/financial_parameter_extractor.py"),
        Path("app/ai/financial_tool_executor.py"),
        Path("app/ai/hebrew_response_builder.py"),
        Path("app/dialogue/conversation_flow_manager.py"),
        Path("app/dialogue/conversation_state.py"),
        Path("app/dialogue/conversation_state_store.py"),
        Path("app/financial/demo_financial_tools.py"),
        Path("app/financial/financial_contracts.py"),
        Path("app/financial/financial_decision_engine.py"),
        Path("app/financial/financial_reason_codes.py"),
        Path("app/financial/user_financial_profile.py"),
        Path("tests/api_test_client.py"),
        Path("tests/test_architecture_boundaries.py"),
        Path("tests/test_chat_message_api.py"),
        Path("tests/test_conversation_state.py"),
        Path("tests/test_financial_decision_engine.py"),
        Path("tests/test_financial_profile_api.py"),
        Path("tests/test_financial_intent_and_parameter_parsing.py"),
        Path("tests/test_financial_tool_contracts.py"),
        Path("tests/test_health_check_api.py"),
        Path("tests/test_local_tester_app.py"),
        Path("tests/test_multiturn_conversation_flows.py"),
        Path("tests/test_system_audit_checks.py"),
        Path("tests/test_user_financial_tools.py"),
    }

    for path in expected_paths:
        assert path.exists(), path


def test_response_policy_uses_existing_ai_package_not_parallel_assistant_package() -> None:
    assert not Path("app/assistant").exists()
    assert not Path("app/schemas").exists()


