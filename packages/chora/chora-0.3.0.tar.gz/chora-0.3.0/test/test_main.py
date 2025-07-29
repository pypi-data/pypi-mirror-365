from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from chora.__main__ import main


class TestMain:
    """Test cases for the main function."""

    @patch("chora.__main__.start_server")
    @patch("chora.__main__.parse_arguments")
    @patch("builtins.print")
    def test_main_successful_execution(
        self, mock_print, mock_parse_args, mock_start_server, tmp_path
    ):
        """Test successful execution of main function."""
        # Setup mock arguments
        mock_args = Mock()
        mock_args.root = str(tmp_path)
        mock_args.host = "localhost"
        mock_args.port = 8000
        mock_parse_args.return_value = mock_args

        # Create the root directory
        tmp_path.mkdir(exist_ok=True)

        # Execute main
        main()

        # Verify parse_arguments was called
        mock_parse_args.assert_called_once()

        # Verify start_server was called with correct arguments
        mock_start_server.assert_called_once_with(tmp_path, "localhost", 8000)

        # Verify print statements were called
        expected_prints = [
            "Starting chora server...",
            f"  Root directory: {tmp_path.absolute()}",
            "  Server address: http://localhost:8000",
            "  Press Ctrl+C to stop the server",
        ]

        assert mock_print.call_count == 4
        for i, expected_call in enumerate(expected_prints):
            assert mock_print.call_args_list[i][0][0] == expected_call

    @patch("chora.__main__.parse_arguments")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_main_root_directory_does_not_exist(
        self, mock_exit, mock_print, mock_parse_args, tmp_path
    ):
        """Test main function when root directory does not exist."""
        # Setup mock arguments with non-existent directory
        mock_args = Mock()
        mock_args.root = str(tmp_path / "nonexistent")
        mock_args.host = "localhost"
        mock_args.port = 8000
        mock_parse_args.return_value = mock_args

        # Execute main
        main()

        # Verify error message and exit
        mock_print.assert_called_once_with(
            f"Error: Root directory '{mock_args.root}' does not exist."
        )
        mock_exit.assert_called_once_with(1)

    @patch("chora.__main__.parse_arguments")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_main_root_path_is_not_directory(
        self, mock_exit, mock_print, mock_parse_args, tmp_path
    ):
        """Test main function when root path is not a directory."""
        # Create a file instead of directory
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("not a directory")

        # Setup mock arguments
        mock_args = Mock()
        mock_args.root = str(test_file)
        mock_args.host = "localhost"
        mock_args.port = 8000
        mock_parse_args.return_value = mock_args

        # Execute main
        main()

        # Verify error message and exit
        mock_print.assert_called_once_with(
            f"Error: Root path '{mock_args.root}' is not a directory."
        )
        mock_exit.assert_called_once_with(1)

    @patch("chora.__main__.start_server")
    @patch("chora.__main__.parse_arguments")
    @patch("builtins.print")
    def test_main_with_custom_host_and_port(
        self, mock_print, mock_parse_args, mock_start_server, tmp_path
    ):
        """Test main function with custom host and port."""
        # Setup mock arguments
        mock_args = Mock()
        mock_args.root = str(tmp_path)
        mock_args.host = "0.0.0.0"
        mock_args.port = 9000
        mock_parse_args.return_value = mock_args

        # Create the root directory
        tmp_path.mkdir(exist_ok=True)

        # Execute main
        main()

        # Verify start_server was called with custom host and port
        mock_start_server.assert_called_once_with(tmp_path, "0.0.0.0", 9000)

        # Verify correct server address in print statement
        server_address_call = mock_print.call_args_list[1][0][0]
        assert server_address_call == "  Server address: http://0.0.0.0:9000"

    @patch("chora.__main__.start_server")
    @patch("chora.__main__.parse_arguments")
    @patch("builtins.print")
    def test_main_with_relative_path(
        self, mock_print, mock_parse_args, mock_start_server, tmp_path
    ):
        """Test main function with relative path that gets converted to absolute."""
        # Create a subdirectory
        subdir = tmp_path / "api"
        subdir.mkdir()

        # Setup mock arguments with relative path
        mock_args = Mock()
        mock_args.root = "./api"
        mock_args.host = "localhost"
        mock_args.port = 8000
        mock_parse_args.return_value = mock_args

        # Change to the temp directory so relative path works
        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(tmp_path)

            # Execute main
            main()

            # Verify start_server was called with Path object
            mock_start_server.assert_called_once()
            call_args = mock_start_server.call_args[0]
            assert isinstance(call_args[0], Path)
            assert call_args[1] == "localhost"
            assert call_args[2] == 8000

        finally:
            # Restore original working directory
            import os

            os.chdir(original_cwd)

    @patch("chora.__main__.start_server")
    @patch("chora.__main__.parse_arguments")
    @patch("builtins.print")
    def test_main_print_statements_format(
        self, mock_print, mock_parse_args, mock_start_server, tmp_path
    ):
        """Test that print statements are formatted correctly."""
        # Setup mock arguments
        mock_args = Mock()
        mock_args.root = str(tmp_path)
        mock_args.host = "test.example.com"
        mock_args.port = 3000
        mock_parse_args.return_value = mock_args

        # Create the root directory
        tmp_path.mkdir(exist_ok=True)

        # Execute main
        main()

        # Verify all print statements
        print_calls = [call[0][0] for call in mock_print.call_args_list]

        assert print_calls[0] == "Starting chora server..."
        assert print_calls[1] == f"  Root directory: {tmp_path.absolute()}"
        assert print_calls[2] == "  Server address: http://test.example.com:3000"
        assert print_calls[3] == "  Press Ctrl+C to stop the server"

    @patch("chora.__main__.start_server", side_effect=KeyboardInterrupt)
    @patch("chora.__main__.parse_arguments")
    @patch("builtins.print")
    def test_main_handles_keyboard_interrupt(
        self, mock_print, mock_parse_args, mock_start_server, tmp_path
    ):
        """Test that main function handles KeyboardInterrupt from start_server."""
        # Setup mock arguments
        mock_args = Mock()
        mock_args.root = str(tmp_path)
        mock_args.host = "localhost"
        mock_args.port = 8000
        mock_parse_args.return_value = mock_args

        # Create the root directory
        tmp_path.mkdir(exist_ok=True)

        # Execute main - should not raise exception
        with pytest.raises(KeyboardInterrupt):
            main()

        # Verify setup was completed before KeyboardInterrupt
        mock_parse_args.assert_called_once()
        mock_start_server.assert_called_once()

    @patch("chora.__main__.parse_arguments")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_main_absolute_path_validation(
        self, mock_exit, mock_print, mock_parse_args, tmp_path
    ):
        """Test main function with absolute path validation."""
        # Setup mock arguments with absolute path to non-existent directory
        nonexistent_path = tmp_path / "does" / "not" / "exist"
        mock_args = Mock()
        mock_args.root = str(nonexistent_path)
        mock_args.host = "localhost"
        mock_args.port = 8000
        mock_parse_args.return_value = mock_args

        # Execute main
        main()

        # Verify error handling
        mock_print.assert_called_once_with(
            f"Error: Root directory '{str(nonexistent_path)}' does not exist."
        )
        mock_exit.assert_called_once_with(1)

    @patch("chora.__main__.start_server")
    @patch("chora.__main__.parse_arguments")
    @patch("builtins.print")
    def test_main_path_object_conversion(
        self, mock_print, mock_parse_args, mock_start_server, tmp_path
    ):
        """Test that string path is properly converted to Path object."""
        # Setup mock arguments
        mock_args = Mock()
        mock_args.root = str(tmp_path)
        mock_args.host = "localhost"
        mock_args.port = 8000
        mock_parse_args.return_value = mock_args

        # Create the root directory
        tmp_path.mkdir(exist_ok=True)

        # Execute main
        main()

        # Verify that start_server received a Path object, not a string
        mock_start_server.assert_called_once()
        root_arg = mock_start_server.call_args[0][0]
        assert isinstance(root_arg, Path)
        assert root_arg == tmp_path
