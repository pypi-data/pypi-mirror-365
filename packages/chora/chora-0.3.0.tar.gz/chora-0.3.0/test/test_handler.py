import os
from pathlib import Path

import pytest
from conftest import TestClient, make_static_route


def test_handle_static(test_client: TestClient) -> None:
    """Test that static routes are handled properly."""
    path = "test"

    assert test_client.tmp_path is not None  # Type assertion for mypy
    test_dir = test_client.tmp_path / path / "GET"
    make_static_route(
        test_dir, headers={"Content-Type": "application/json"}, body={"key": "value"}
    )

    # Make an HTTP request using the test client
    response = test_client.get(f"/{path}")

    assert response.status_code == 200
    assert response.get_header("Content-Type") == "application/json"
    assert response.json() == {"key": "value"}


def test_dynamic_handler(test_client: TestClient) -> None:
    """Test that dynamic handlers (HANDLE scripts) are executed properly."""
    path = "dynamic"
    method = "GET"

    # Create the directory structure for dynamic handler
    handler_dir = test_client.tmp_path / path / method
    handler_dir.mkdir(parents=True, exist_ok=True)

    # Create a HANDLE script that returns a path to static content
    handle_script = handler_dir / "HANDLE"
    handle_script.write_text("""#!/bin/sh
echo "static_response"
""")
    handle_script.chmod(0o755)  # Make executable

    # Create the static response that the HANDLE script points to
    response_dir = handler_dir / "static_response"
    make_static_route(
        response_dir, headers={"Content-Type": "text/plain"}, body="Dynamic response"
    )

    # Make request
    response = test_client.get(f"/{path}")

    # Verify dynamic handler was executed and returned static content
    assert response.status_code == 200
    assert response.get_header("Content-Type") == "text/plain"
    assert response.json() == "Dynamic response"


def test_directory_not_found(test_client: TestClient) -> None:
    """
    Test handler behavior when requested path doesn't exist and no template is available.

    WHY THIS TEST: This tests the FileNotFoundError path in get_handler() when
    _get_directory() returns None. This is a common scenario when users request
    non-existent endpoints.

    ALTERNATIVE APPROACHES:
    1. Return a custom 404 page instead of letting the exception bubble up
    2. Log the missing path for debugging purposes
    3. Provide a default fallback template mechanism

    This test ensures the server handles missing paths gracefully rather than crashing.
    """
    # Request a path that doesn't exist
    response = test_client.get("/nonexistent/path")

    # Should now return 404 due to improved error handling
    assert response.status_code == 404
    assert "Not Found" in response.text


@pytest.mark.parametrize("missing_file", ["STATUS", "DATA", "HEADERS"])
def test_missing_static_files(test_client: TestClient, missing_file: str) -> None:
    path = "incomplete"
    method = "GET"

    test_dir = test_client.tmp_path / path / method
    test_dir.mkdir(parents=True, exist_ok=True)

    # Create all files except the one we're testing
    files_to_create = {
        "STATUS": "200",
        "DATA": "test",
        "HEADERS": "Content-Type: text/plain",
    }
    files_to_create.pop(missing_file)

    for filename, content in files_to_create.items():
        (test_dir / filename).write_text(content)

    response = test_client.get(f"/{path}")

    # Should return 404 due to missing file (FileNotFoundError)
    assert response.status_code == 404
    assert "Not Found" in response.text


def test_malformed_status_file(test_client: TestClient) -> None:
    """
    Test handler behavior when STATUS file contains non-integer content.
    """
    path = "malformed_status"
    method = "GET"

    test_dir = test_client.tmp_path / path / method
    test_dir.mkdir(parents=True, exist_ok=True)

    # Create files with malformed STATUS
    (test_dir / "STATUS").write_text("not_a_number")
    (test_dir / "DATA").write_text("test data")
    (test_dir / "HEADERS").write_text("Content-Type: text/plain")

    response = test_client.get(f"/{path}")

    # Should return 500 due to ValueError in int() conversion
    assert response.status_code == 500
    assert "Internal Server Error" in response.text


def test_non_executable_handle_script(test_client: TestClient) -> None:
    path = "non_executable"
    method = "GET"

    handler_dir = test_client.tmp_path / path / method
    handler_dir.mkdir(parents=True, exist_ok=True)

    # Create HANDLE script but don't make it executable
    handle_script = handler_dir / "HANDLE"
    handle_script.write_text("""#!/bin/sh
echo "response"
""")
    # Explicitly remove execute permissions
    handle_script.chmod(0o644)

    response = test_client.get(f"/{path}")

    # Should return 403 due to PermissionError
    assert response.status_code == 403
    assert "Forbidden" in response.text


def test_failing_handle_script(test_client: TestClient) -> None:
    path = "failing_script"
    method = "GET"

    handler_dir = test_client.tmp_path / path / method
    handler_dir.mkdir(parents=True, exist_ok=True)

    # Create HANDLE script that exits with error
    handle_script = handler_dir / "HANDLE"
    handle_script.write_text("""#!/bin/sh
echo "Script failed" >&2
exit 1
""")
    handle_script.chmod(0o755)

    response = test_client.get(f"/{path}")

    # Should return 500 due to CalledProcessError
    assert response.status_code == 500
    assert "Internal Server Error" in response.text


def test_handle_script_invalid_output(test_client: TestClient) -> None:
    path = "invalid_output"
    method = "GET"

    handler_dir = test_client.tmp_path / path / method
    handler_dir.mkdir(parents=True, exist_ok=True)

    # Create HANDLE script that outputs non-existent path
    handle_script = handler_dir / "HANDLE"
    handle_script.write_text("""#!/bin/sh
echo "/this/path/does/not/exist"
""")
    handle_script.chmod(0o755)

    response = test_client.get(f"/{path}")

    # Should return 404 because the output path doesn't exist (FileNotFoundError)
    assert response.status_code == 404
    assert "Not Found" in response.text


def test_empty_headers_file(test_client: TestClient) -> None:
    path = "empty_headers"
    method = "GET"

    test_dir = test_client.tmp_path / path / method
    make_static_route(
        test_dir,
        headers={},  # This will create an empty HEADERS file
        body="test content",
    )

    response = test_client.get(f"/{path}")

    assert response.status_code == 200
    assert response.json() == "test content"


def test_malformed_headers_file(test_client: TestClient) -> None:
    """
    Test handler behavior with malformed HEADERS file (no colon separators).
    """
    path = "malformed_headers"
    method = "GET"

    test_dir = test_client.tmp_path / path / method
    test_dir.mkdir(parents=True, exist_ok=True)

    (test_dir / "STATUS").write_text("200")
    (test_dir / "DATA").write_text("test content")
    # Create HEADERS file with lines that don't contain colons
    (test_dir / "HEADERS").write_text("InvalidHeaderLine\nAnotherBadLine")

    response = test_client.get(f"/{path}")

    # Should still work, but with no headers set
    assert response.status_code == 200
    assert response.text == "test content"
    # The malformed headers should be ignored


def test_root_path_handling(test_client: TestClient) -> None:
    method = "GET"

    # Create response for root path (empty string after stripping "/")
    test_dir = test_client.tmp_path / "" / method
    make_static_route(
        test_dir, headers={"Content-Type": "text/html"}, body="<h1>Root Page</h1>"
    )

    response = test_client.get("/")

    assert response.status_code == 200
    assert response.get_header("Content-Type") == "text/html"
    assert response.json() == "<h1>Root Page</h1>"


def test_handle_script_relative_path_output(test_client: TestClient) -> None:
    path = "relative_path"
    method = "GET"

    handler_dir = test_client.tmp_path / path / method
    handler_dir.mkdir(parents=True, exist_ok=True)

    # Create HANDLE script that returns relative path
    handle_script = handler_dir / "HANDLE"
    handle_script.write_text("""#!/bin/sh
echo "relative_response"
""")
    handle_script.chmod(0o755)

    # Create the response directory relative to the script
    response_dir = handler_dir / "relative_response"
    make_static_route(
        response_dir,
        headers={"Content-Type": "application/json"},
        body={"message": "Relative path resolved"},
    )

    response = test_client.get(f"/{path}")

    assert response.status_code == 200
    assert response.get_header("Content-Type") == "application/json"
    assert response.json() == {"message": "Relative path resolved"}


def test_deeply_nested_path(test_client: TestClient) -> None:
    path = "api/v1/users/123/profile/settings"
    method = "GET"

    test_dir = test_client.tmp_path / path / method
    make_static_route(
        test_dir,
        headers={"Content-Type": "application/json"},
        body={"deeply": "nested", "path": "works"},
    )

    response = test_client.get(f"/{path}")

    assert response.status_code == 200
    assert response.get_header("Content-Type") == "application/json"
    assert response.json() == {"deeply": "nested", "path": "works"}


def test_root_dir_is_invalid(test_client: TestClient) -> None:
    os.removedirs(test_client.tmp_path)
    response = test_client.get("/")
    assert response.status_code == 404


class TestTemplating:
    @pytest.mark.parametrize("user_id", ["123", "456", "abc", "user-with-dashes"])
    def test_template_matching(self, test_client: TestClient, user_id: str) -> None:
        """Test that __TEMPLATE__ directories are used when exact path doesn't exist."""
        base_path = "users"
        method = "GET"

        # Create a __TEMPLATE__ directory instead of exact path
        # The handler looks for: users/{user_id}/GET, but we create: users/__TEMPLATE__/GET
        template_dir = test_client.tmp_path / base_path / "__TEMPLATE__" / method
        make_static_route(
            template_dir,
            headers={"Content-Type": "application/json"},
            body={"user_id": "template_matched", "message": "Found via template"},
        )

        response = test_client.get(f"/{base_path}/{user_id}")

        assert response.status_code == 200
        assert response.get_header("Content-Type") == "application/json"
        assert response.json() == {
            "user_id": "template_matched",
            "message": "Found via template",
        }

    def test_we_prioritize_untemplated(self, test_client: TestClient) -> None:
        template_dir = (
            test_client.tmp_path / "__TEMPLATE__" / "__TEMPLATE__" / "__TEMPLATE__"
        )
        make_static_route(
            template_dir,
            headers={"Content-Type": "application/json"},
            body={"user_id": "template_matched", "message": "Found via template"},
        )

        non_template_dir = test_client.tmp_path / "__TEMPLATE__" / "user_id" / "GET"
        make_static_route(
            non_template_dir,
            headers={"Content-Type": "application/json"},
            body={"user_id": "no_template", "message": "Not a template match"},
        )

        get_resp = test_client.get("/users/user_id")
        assert get_resp.status_code == 200
        assert get_resp.get_header("Content-Type") == "application/json"
        assert get_resp.json() == {
            "user_id": "no_template",
            "message": "Not a template match",
        }

        # We don't create a PUT handler
        put_resp = test_client.put("/users/user_id")
        assert put_resp.status_code == 404, put_resp.text

    def test_template_shortcircuits(self, test_client: TestClient) -> None:
        """
        Test that template matching short-circuits and doesn't fall back to deeper templates.
        """
        template_dir = (
            test_client.tmp_path / "__TEMPLATE__" / "__TEMPLATE__" / "__TEMPLATE__"
        )
        make_static_route(
            template_dir,
            headers={"Content-Type": "application/json"},
            body={"user_id": "template_matched", "message": "Found via template"},
        )

        make_static_route(
            Path("users/GET"),
            headers={"Content-Type": "application/json"},
            body={"user_id": "template_matched", "message": "Found via template"},
        )

        get_resp = test_client.get("/users/user_id")
        assert get_resp.status_code == 200
        assert get_resp.get_header("Content-Type") == "application/json"
        assert get_resp.json() == {
            "user_id": "template_matched",
            "message": "Found via template",
        }

    def test_templated_methods(self, test_client: TestClient) -> None:
        template_dir = (
            test_client.tmp_path / "__TEMPLATE__" / "__TEMPLATE__" / "__TEMPLATE__"
        )
        make_static_route(
            template_dir,
            headers={"Content-Type": "application/json"},
            body={"user_id": "template_matched", "message": "Found via template"},
        )

        get_resp = test_client.get("/users/user_id")
        put_resp = test_client.put("/users/user_id")

        assert get_resp.status_code == put_resp.status_code
        assert get_resp.headers == put_resp.headers
        assert get_resp.json() == put_resp.json()

        assert get_resp.status_code == 200
        assert get_resp.get_header("Content-Type") == "application/json"
        assert get_resp.json() == {
            "user_id": "template_matched",
            "message": "Found via template",
        }
