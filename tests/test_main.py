"""Comprehensive tests for main.py module."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_optimizer.config import TransportMode, settings
from mcp_optimizer.main import (
    cli_main,
    main,
    parse_args,
    run_stdio_server,
    setup_logging,
)


class TestSetupLogging:
    """Tests for setup_logging function."""

    @patch("mcp_optimizer.main.logging.basicConfig")
    def test_setup_logging_json_format(self, mock_basic_config):
        """Test setup logging with JSON format."""
        with patch("mcp_optimizer.main.settings") as mock_settings:
            mock_settings.log_level.value = "INFO"
            mock_settings.log_format.value = "json"

            setup_logging()

            mock_basic_config.assert_called_once()
            args, kwargs = mock_basic_config.call_args
            assert kwargs["level"] == logging.INFO
            assert '"timestamp"' in kwargs["format"]
            assert '"level"' in kwargs["format"]

    @patch("mcp_optimizer.main.logging.basicConfig")
    def test_setup_logging_human_format(self, mock_basic_config):
        """Test setup logging with human-readable format."""
        with patch("mcp_optimizer.main.settings") as mock_settings:
            mock_settings.log_level.value = "DEBUG"
            mock_settings.log_format.value = "human"

            setup_logging()

            mock_basic_config.assert_called_once()
            args, kwargs = mock_basic_config.call_args
            assert kwargs["level"] == logging.DEBUG
            assert "asctime" in kwargs["format"]
            assert "name" in kwargs["format"]

    @patch("mcp_optimizer.main.logging.basicConfig")
    def test_setup_logging_different_levels(self, mock_basic_config):
        """Test setup logging with different log levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR"]

        for level in levels:
            with patch("mcp_optimizer.main.settings") as mock_settings:
                mock_settings.log_level.value = level
                mock_settings.log_format.value = "human"

                setup_logging()

                expected_level = getattr(logging, level)
                args, kwargs = mock_basic_config.call_args
                assert kwargs["level"] == expected_level


class TestRunStdioServer:
    """Tests for run_stdio_server function."""

    @patch("mcp_optimizer.main.create_mcp_server")
    @patch("mcp_optimizer.main.logging.info")
    def test_run_stdio_server(self, mock_logging, mock_create_server):
        """Test running stdio server."""
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server

        run_stdio_server()

        mock_logging.assert_called_with("Starting MCP Optimizer server with stdio transport")
        mock_create_server.assert_called_once()
        mock_server.run.assert_called_once_with(transport="stdio")


class TestParseArgs:
    """Tests for parse_args function."""

    def test_parse_args_defaults(self):
        """Test parsing arguments with defaults."""
        with patch("sys.argv", ["script_name"]):
            args = parse_args()

            assert args.transport == settings.transport_mode.value
            assert args.port == settings.server_port
            assert args.host == settings.server_host
            assert args.debug == settings.debug
            assert args.reload == settings.reload
            assert args.log_level == settings.log_level.value

    def test_parse_args_custom_transport(self):
        """Test parsing arguments with custom transport."""
        with patch("sys.argv", ["script_name", "--transport", "sse"]):
            args = parse_args()

            assert args.transport == "sse"

    def test_parse_args_custom_port(self):
        """Test parsing arguments with custom port."""
        with patch("sys.argv", ["script_name", "--port", "9000"]):
            args = parse_args()

            assert args.port == 9000

    def test_parse_args_custom_host(self):
        """Test parsing arguments with custom host."""
        with patch("sys.argv", ["script_name", "--host", "192.168.1.1"]):
            args = parse_args()

            assert args.host == "192.168.1.1"

    def test_parse_args_debug_flag(self):
        """Test parsing arguments with debug flag."""
        with patch("sys.argv", ["script_name", "--debug"]):
            args = parse_args()

            assert args.debug is True

    def test_parse_args_reload_flag(self):
        """Test parsing arguments with reload flag."""
        with patch("sys.argv", ["script_name", "--reload"]):
            args = parse_args()

            assert args.reload is True

    def test_parse_args_custom_log_level(self):
        """Test parsing arguments with custom log level."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            with patch("sys.argv", ["script_name", "--log-level", level]):
                args = parse_args()

                assert args.log_level == level

    def test_parse_args_all_custom(self):
        """Test parsing arguments with all custom values."""
        with patch(
            "sys.argv",
            [
                "script_name",
                "--transport",
                "sse",
                "--port",
                "8080",
                "--host",
                "localhost",
                "--debug",
                "--reload",
                "--log-level",
                "DEBUG",
            ],
        ):
            args = parse_args()

            assert args.transport == "sse"
            assert args.port == 8080
            assert args.host == "localhost"
            assert args.debug is True
            assert args.reload is True
            assert args.log_level == "DEBUG"


class TestMain:
    """Tests for main function."""

    @patch("mcp_optimizer.main.parse_args")
    @patch("mcp_optimizer.main.setup_logging")
    @patch("mcp_optimizer.main.run_stdio_server")
    @patch("mcp_optimizer.main.settings")
    def test_main_stdio_transport(
        self, mock_settings, mock_run_stdio, mock_setup_logging, mock_parse_args
    ):
        """Test main function with stdio transport."""
        # Setup mock args
        mock_args = MagicMock()
        mock_args.transport = "stdio"
        mock_args.port = 8000
        mock_args.host = "localhost"
        mock_args.debug = False
        mock_args.reload = False
        mock_args.log_level = "INFO"
        mock_parse_args.return_value = mock_args

        # Setup mock settings
        mock_settings.transport_mode = TransportMode.STDIO

        main()

        mock_setup_logging.assert_called_once()
        mock_run_stdio.assert_called_once()

    @patch("mcp_optimizer.main.parse_args")
    @patch("mcp_optimizer.main.setup_logging")
    @patch("asyncio.run")
    @patch("mcp_optimizer.main.run_sse_server")
    @patch("mcp_optimizer.main.settings")
    def test_main_sse_transport(
        self, mock_settings, mock_run_sse, mock_asyncio_run, mock_setup_logging, mock_parse_args
    ):
        """Test main function with SSE transport."""
        # Setup mock args
        mock_args = MagicMock()
        mock_args.transport = "sse"
        mock_args.port = 8000
        mock_args.host = "localhost"
        mock_args.debug = False
        mock_args.reload = False
        mock_args.log_level = "INFO"
        mock_parse_args.return_value = mock_args

        # Setup mock settings
        mock_settings.transport_mode = TransportMode.SSE

        # Mock the run_sse_server to return a coroutine-like object
        mock_coro = MagicMock()
        mock_run_sse.return_value = mock_coro

        main()

        mock_setup_logging.assert_called_once()
        mock_asyncio_run.assert_called_once()

    @patch("mcp_optimizer.main.parse_args")
    @patch("mcp_optimizer.main.setup_logging")
    @patch("mcp_optimizer.main.run_stdio_server")
    @patch("mcp_optimizer.main.logging.info")
    @patch("mcp_optimizer.main.settings")
    def test_main_keyboard_interrupt(
        self, mock_settings, mock_logging, mock_run_stdio, mock_setup_logging, mock_parse_args
    ):
        """Test main function with keyboard interrupt."""
        # Setup mock args
        mock_args = MagicMock()
        mock_args.transport = "stdio"
        mock_args.port = 8000
        mock_args.host = "localhost"
        mock_args.debug = False
        mock_args.reload = False
        mock_args.log_level = "INFO"
        mock_parse_args.return_value = mock_args

        # Setup mock settings
        mock_settings.transport_mode = TransportMode.STDIO

        # Mock keyboard interrupt
        mock_run_stdio.side_effect = KeyboardInterrupt()

        main()

        mock_logging.assert_called_with("Server shutdown requested")

    @patch("mcp_optimizer.main.parse_args")
    @patch("mcp_optimizer.main.setup_logging")
    @patch("mcp_optimizer.main.run_stdio_server")
    @patch("mcp_optimizer.main.logging.error")
    @patch("mcp_optimizer.main.sys.exit")
    @patch("mcp_optimizer.main.settings")
    def test_main_exception_no_debug(
        self,
        mock_settings,
        mock_exit,
        mock_logging,
        mock_run_stdio,
        mock_setup_logging,
        mock_parse_args,
    ):
        """Test main function with exception and no debug mode."""
        # Setup mock args
        mock_args = MagicMock()
        mock_args.transport = "stdio"
        mock_args.port = 8000
        mock_args.host = "localhost"
        mock_args.debug = False
        mock_args.reload = False
        mock_args.log_level = "INFO"
        mock_parse_args.return_value = mock_args

        # Setup mock settings
        mock_settings.transport_mode = TransportMode.STDIO
        mock_settings.debug = False

        # Mock exception
        test_exception = Exception("Test error")
        mock_run_stdio.side_effect = test_exception

        main()

        mock_logging.assert_called_with("Server error: Test error")
        mock_exit.assert_called_with(1)

    @patch("mcp_optimizer.main.parse_args")
    @patch("mcp_optimizer.main.setup_logging")
    @patch("mcp_optimizer.main.run_stdio_server")
    @patch("mcp_optimizer.main.logging.error")
    @patch("mcp_optimizer.main.settings")
    def test_main_exception_debug_mode(
        self, mock_settings, mock_logging, mock_run_stdio, mock_setup_logging, mock_parse_args
    ):
        """Test main function with exception and debug mode."""
        # Setup mock args
        mock_args = MagicMock()
        mock_args.transport = "stdio"
        mock_args.port = 8000
        mock_args.host = "localhost"
        mock_args.debug = True
        mock_args.reload = False
        mock_args.log_level = "INFO"
        mock_parse_args.return_value = mock_args

        # Setup mock settings
        mock_settings.transport_mode = TransportMode.STDIO
        mock_settings.debug = True

        # Mock exception
        test_exception = Exception("Test error")
        mock_run_stdio.side_effect = test_exception

        with pytest.raises(Exception, match="Test error"):
            main()

    @patch("mcp_optimizer.main.settings")
    def test_settings_update_from_args(self, mock_settings):
        """Test that settings are updated from command line arguments."""
        with patch("mcp_optimizer.main.parse_args") as mock_parse_args:
            with patch("mcp_optimizer.main.setup_logging"):
                with patch("mcp_optimizer.main.run_stdio_server"):
                    with patch("asyncio.run") as mock_asyncio_run:
                        with patch("mcp_optimizer.main.run_sse_server", spec=True) as mock_run_sse:
                            # Setup mock args
                            mock_args = MagicMock()
                            mock_args.transport = "sse"
                            mock_args.port = 9000
                            mock_args.host = "0.0.0.0"
                            mock_args.debug = True
                            mock_args.reload = True
                            mock_args.log_level = "DEBUG"
                            mock_parse_args.return_value = mock_args

                            # Setup mock settings
                            mock_settings.transport_mode = TransportMode.SSE

                            # Configure the mock properly
                            test_coro = MagicMock()
                            mock_run_sse.return_value = test_coro

                            main()

                            # Verify settings were updated
                            assert mock_settings.transport_mode == TransportMode("sse")
                            assert mock_settings.server_port == 9000
                            assert mock_settings.server_host == "0.0.0.0"
                            assert mock_settings.debug is True
                            assert mock_settings.reload is True

                            # Verify asyncio.run was called for SSE transport
                            mock_asyncio_run.assert_called_once()


class TestCliMain:
    """Tests for cli_main function."""

    @patch("mcp_optimizer.main.main")
    def test_cli_main_success(self, mock_main):
        """Test cli_main function success."""
        cli_main()

        mock_main.assert_called_once()

    @patch("mcp_optimizer.main.main")
    def test_cli_main_keyboard_interrupt(self, mock_main):
        """Test cli_main function with keyboard interrupt."""
        mock_main.side_effect = KeyboardInterrupt()

        # Should not raise exception
        cli_main()

        mock_main.assert_called_once()


class TestAsyncRunSSEServer:
    """Tests for run_sse_server function."""

    @patch("mcp_optimizer.main.create_mcp_server")
    @patch("mcp_optimizer.main.uvicorn.Server")
    @patch("mcp_optimizer.main.uvicorn.Config")
    @patch("mcp_optimizer.main.logging.info")
    @pytest.mark.filterwarnings("ignore:coroutine.*was never awaited:RuntimeWarning")
    async def test_run_sse_server(self, mock_logging, mock_config, mock_server, mock_create_server):
        """Test running SSE server."""
        from mcp_optimizer.main import run_sse_server

        # Setup mocks
        mock_mcp_server = MagicMock()
        mock_mcp_server.sse_app = MagicMock()
        mock_create_server.return_value = mock_mcp_server

        mock_server_instance = MagicMock()
        # Make serve an async mock with proper awaitable
        mock_server_instance.serve = AsyncMock()
        mock_server.return_value = mock_server_instance

        # Call function
        await run_sse_server()

        # Verify calls
        mock_logging.assert_called_once()
        mock_create_server.assert_called_once()
        mock_config.assert_called_once()
        mock_server.assert_called_once()


class TestMCPObjectExport:
    """Tests for MCP object export."""

    def test_mcp_object_exists(self):
        """Test that mcp object is exported."""
        from mcp_optimizer.main import mcp

        assert mcp is not None
        # The mcp object should be a FastMCP instance
        assert hasattr(mcp, "run")
        assert hasattr(mcp, "tool")
