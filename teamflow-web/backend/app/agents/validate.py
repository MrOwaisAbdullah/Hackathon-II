"""Validation script for TeamFlow AI Chatbot agent implementation.

This script validates the implementation without requiring the dependencies
to be installed. It checks:
1. File structure
2. Syntax validity
3. Configuration correctness
"""
import ast
import os
from pathlib import Path


def validate_python_syntax(filepath: Path) -> bool:
    """Validate Python file syntax."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            ast.parse(f.read())
        return True
    except SyntaxError as e:
        print(f"  ❌ Syntax error: {e}")
        return False


def validate_agent_implementation():
    """Validate the agent implementation."""
    print("=" * 60)
    print("TeamFlow AI Chatbot - Implementation Validation")
    print("=" * 60)
    print()

    base_path = Path("/mnt/d/GIAIC/Quarter 4/Hackathon II/teamflow-web/backend/app/agents")

    # Check file structure
    print("1. Checking file structure...")
    required_files = [
        "__init__.py",
        "client.py",
        "chatbot.py",
        "example.py",
        "README.md",
    ]

    for filename in required_files:
        filepath = base_path / filename
        if filepath.exists():
            print(f"  ✓ {filename} exists")
        else:
            print(f"  ❌ {filename} missing")

    print()

    # Check syntax
    print("2. Validating Python syntax...")
    py_files = list(base_path.glob("*.py"))

    all_valid = True
    for py_file in py_files:
        if py_file.name == "__pycache__":
            continue

        print(f"  Checking {py_file.name}...", end=" ")
        if validate_python_syntax(py_file):
            print("✓")
        else:
            all_valid = False

    print()

    # Check configuration
    print("3. Checking configuration...")
    config_path = Path("/mnt/d/GIAIC/Quarter 4/Hackathon II/teamflow-web/backend/app/core/config.py")

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config_content = f.read()

        if "gemini_api_key" in config_content:
            print("  ✓ gemini_api_key field found in config")
        else:
            print("  ❌ gemini_api_key field missing in config")

        if "settings.gemini_api_key" in (base_path / "client.py").read_text():
            print("  ✓ client.py references settings.gemini_api_key")
        else:
            print("  ❌ client.py doesn't reference settings.gemini_api_key")
    else:
        print("  ❌ config.py not found")

    print()

    # Check key implementation details
    print("4. Checking implementation details...")

    client_py = (base_path / "client.py").read_text()
    chatbot_py = (base_path / "chatbot.py").read_text()

    # Check client.py
    checks = [
        ("AsyncOpenAI import", "from openai import AsyncOpenAI" in client_py),
        ("Base URL configuration", 'base_url="https://generativelanguage.googleapis.com/v1beta/"' in client_py),
        ("API key configuration", "settings.gemini_api_key" in client_py),
        ("set_default_openai_client", "set_default_openai_client" in client_py),
        ("Singleton pattern", "_gemini_client" in client_py),
    ]

    for check_name, result in checks:
        if result:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ❌ {check_name} missing")

    print()

    # Check chatbot.py
    chatbot_checks = [
        ("Agent import", "from agents import Agent" in chatbot_py),
        ("Runner import", ("from agents import" in chatbot_py and "Runner" in chatbot_py)),
        ("Agent creation", "def create_chatbot_agent" in chatbot_py),
        ("Streaming runner", "async def run_chatbot_stream" in chatbot_py),
        ("Model parameter", ("gemini-2.0-flash-exp" in chatbot_py or "model=" in chatbot_py)),
        ("MCP integration", "from app.mcp.server import mcp" in chatbot_py),
    ]

    for check_name, result in chatbot_checks:
        if result:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ❌ {check_name} missing")

    print()

    # Summary
    print("=" * 60)
    if all_valid:
        print("✓ All syntax checks passed!")
    else:
        print("❌ Some syntax checks failed")

    print()
    print("Next steps:")
    print("1. Install dependencies: uv sync")
    print("2. Set GEMINI_API_KEY in .env file")
    print("3. Run example: python -m app.agents.example")
    print("=" * 60)


if __name__ == "__main__":
    validate_agent_implementation()
