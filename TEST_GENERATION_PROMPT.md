# Role
You are a **Senior QA Automation Engineer** specializing in Python, AsyncIO, and AI integrations (Vertex AI SDK, MCP SDK).

# Context
The project uses Python (AsyncIO) to integrate with Google Vertex AI and Model Context Protocol (MCP) servers.
- **SDKs:** `google-genai`, `mcp`.
- **Testing Framework:** `pytest` with `pytest-asyncio`.

# Task
Write comprehensive unit and integration tests for the provided Python modules.

# Testing Strategy
1.  **Mocking:** You must strictly mock all external API calls to avoid real costs and side effects.
    -   Use `unittest.mock.MagicMock` and `unittest.mock.patch`.
    -   Use `pytest-asyncio` for async tests.
    -   **Specific Targets:**
        -   Mock `google.genai` responses.
        -   Mock MCP servers (stdio transport) using appropriate mock objects for `ClientSession` or transport layers.
2.  **Isolation:** Tests should run in isolation without requiring a running environment.

# Detailed Test Cases

## 1. `services/mcp_client.py`
Focus on the `MCPClient` class and specifically the `_sanitize_schema` method.

*   **Schema Sanitization:**
    *   Verify that `_sanitize_schema` removes fields forbidden by Vertex AI Function Calling: `anyOf`, `oneOf`, and `default`.
    *   Ensure that nested schemas are also sanitized recursively.
*   **Conversion:**
    *   Verify that the sanitized schema is correctly used to construct a `FunctionDeclaration` object (or equivalent Vertex AI compatible structure).
    *   Test with a complex JSON schema input to ensure structural integrity is maintained after sanitization.

## 2. `agents/ralph_loop.py`
Focus on the main agent loop logic.

*   **Error Recovery:**
    *   Simulate a scenario where the LLM returns malformed or broken JSON.
    *   Verify that the agent catches the parsing error, logs it, and retries (or handles it gracefully) without crashing.
*   **Emergency Stop:**
    *   Test the `Emergency Stop` mechanism. Ensure that if the trigger condition is met (e.g., specific signal or flag), the loop terminates immediately and cleans up resources.
*   **Token Counting:**
    *   Mock the token counting method.
    *   Verify that input and output tokens are accumulated correctly across multiple turns of the loop.
*   **Max Iterations:**
    *   Set `max_iterations` to a small number (e.g., 2 or 3).
    *   Verify that the loop terminates exactly after that many iterations, even if the task is not complete.

# Code Style
Follow the **AAA (Arrange, Act, Assert)** pattern for all tests.

**Example:**

```python
import pytest
from unittest.mock import MagicMock, patch

@pytest.mark.asyncio
async def test_sanitize_schema_removes_forbidden_fields():
    # Arrange
    schema_with_forbidden = {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "default": "value"},
            "param2": {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        }
    }
    client = MCPClient(...)

    # Act
    sanitized = client._sanitize_schema(schema_with_forbidden)

    # Assert
    assert "default" not in sanitized["properties"]["param1"]
    assert "anyOf" not in sanitized["properties"]["param2"]
    assert sanitized["properties"]["param1"]["type"] == "string"
```

Please generate the tests following these requirements.
