"""Tests for jupyter-dark-detect."""

import os
import json
import tempfile
from pathlib import Path
from unittest import mock
import pytest

from jupyter_dark_detect import is_dark
from jupyter_dark_detect.detector import (
    _check_jupyterlab_settings,
    _check_vscode_settings,
    _check_system_preferences,
)


class TestJupyterLabSettings:
    """Test JupyterLab settings detection."""

    def test_dark_theme_detection(self, tmp_path):
        """Test detection of dark theme in JupyterLab settings."""
        settings_dir = tmp_path / ".jupyter" / "lab" / "user-settings" / "@jupyterlab" / "apputils-extension"
        settings_dir.mkdir(parents=True)
        
        settings_file = settings_dir / "themes.jupyterlab-settings"
        settings_file.write_text(json.dumps({"theme": "JupyterLab Dark"}))
        
        with mock.patch.object(Path, "home", return_value=tmp_path):
            assert _check_jupyterlab_settings() is True

    def test_light_theme_detection(self, tmp_path):
        """Test detection of light theme in JupyterLab settings."""
        settings_dir = tmp_path / ".jupyter" / "lab" / "user-settings" / "@jupyterlab" / "apputils-extension"
        settings_dir.mkdir(parents=True)
        
        settings_file = settings_dir / "themes.jupyterlab-settings"
        settings_file.write_text(json.dumps({"theme": "JupyterLab Light"}))
        
        with mock.patch.object(Path, "home", return_value=tmp_path):
            assert _check_jupyterlab_settings() is False

    def test_comments_in_settings(self, tmp_path):
        """Test handling of comments in JupyterLab settings."""
        settings_dir = tmp_path / ".jupyter" / "lab" / "user-settings" / "@jupyterlab" / "apputils-extension"
        settings_dir.mkdir(parents=True)
        
        settings_file = settings_dir / "themes.jupyterlab-settings"
        settings_file.write_text("""
        {
            // This is a comment
            "theme": "JupyterLab Dark" /* Another comment */
        }
        """)
        
        with mock.patch.object(Path, "home", return_value=tmp_path):
            assert _check_jupyterlab_settings() is True

    def test_no_settings_file(self, tmp_path):
        """Test when no settings file exists."""
        with mock.patch.object(Path, "home", return_value=tmp_path):
            assert _check_jupyterlab_settings() is None


class TestVSCodeSettings:
    """Test VS Code settings detection."""

    def test_vscode_dark_theme(self, tmp_path):
        """Test detection of dark theme in VS Code settings."""
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        
        settings_file = vscode_dir / "settings.json"
        settings_file.write_text(json.dumps({"workbench.colorTheme": "Dark+ (default dark)"}))
        
        with mock.patch.dict(os.environ, {"VSCODE_PID": "12345"}):
            with mock.patch.object(Path, "cwd", return_value=tmp_path):
                assert _check_vscode_settings() is True

    def test_vscode_light_theme(self, tmp_path):
        """Test detection of light theme in VS Code settings."""
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        
        settings_file = vscode_dir / "settings.json"
        settings_file.write_text(json.dumps({"workbench.colorTheme": "Light+ (default light)"}))
        
        with mock.patch.dict(os.environ, {"VSCODE_PID": "12345"}):
            with mock.patch.object(Path, "cwd", return_value=tmp_path):
                assert _check_vscode_settings() is False

    def test_vscode_nls_config(self):
        """Test detection via VSCODE_NLS_CONFIG environment variable."""
        with mock.patch.dict(os.environ, {
            "VSCODE_PID": "12345",
            "VSCODE_NLS_CONFIG": '{"theme": "dark"}'
        }):
            assert _check_vscode_settings() is True

    def test_not_in_vscode(self):
        """Test when not running in VS Code."""
        with mock.patch.dict(os.environ, {}, clear=True):
            assert _check_vscode_settings() is None


class TestSystemPreferences:
    """Test system preferences detection."""

    @pytest.mark.skipif(not os.sys.platform.startswith("darwin"), reason="macOS only test")
    def test_macos_dark_mode(self):
        """Test macOS dark mode detection."""
        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Dark"
            assert _check_system_preferences() is True

    @pytest.mark.skipif(not os.sys.platform.startswith("darwin"), reason="macOS only test")
    def test_macos_light_mode(self):
        """Test macOS light mode detection."""
        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            assert _check_system_preferences() is False

    @pytest.mark.skipif(not os.sys.platform.startswith("win"), reason="Windows only test")
    def test_windows_dark_mode(self):
        """Test Windows dark mode detection."""
        with mock.patch("winreg.OpenKey") as mock_open:
            with mock.patch("winreg.QueryValueEx") as mock_query:
                mock_query.return_value = (0, None)  # 0 means dark mode
                assert _check_system_preferences() is True

    @pytest.mark.skipif(not os.sys.platform.startswith("win"), reason="Windows only test")
    def test_windows_light_mode(self):
        """Test Windows light mode detection."""
        with mock.patch("winreg.OpenKey") as mock_open:
            with mock.patch("winreg.QueryValueEx") as mock_query:
                mock_query.return_value = (1, None)  # 1 means light mode
                assert _check_system_preferences() is False


class TestMainFunction:
    """Test the main is_dark function."""

    def test_default_to_false(self):
        """Test that is_dark defaults to False when no detection works."""
        with mock.patch("jupyter_dark_detect.detector._check_jupyterlab_settings", return_value=None):
            with mock.patch("jupyter_dark_detect.detector._check_vscode_settings", return_value=None):
                with mock.patch("jupyter_dark_detect.detector._check_javascript_detection", return_value=None):
                    with mock.patch("jupyter_dark_detect.detector._check_system_preferences", return_value=None):
                        assert is_dark() is False

    def test_jupyterlab_priority(self):
        """Test that JupyterLab settings take priority."""
        with mock.patch("jupyter_dark_detect.detector._check_jupyterlab_settings", return_value=True):
            with mock.patch("jupyter_dark_detect.detector._check_vscode_settings", return_value=False):
                assert is_dark() is True

    def test_exception_handling(self):
        """Test that exceptions are handled gracefully."""
        with mock.patch("jupyter_dark_detect.detector._check_jupyterlab_settings", side_effect=Exception("Test error")):
            # Should not raise, should continue to other detection methods
            result = is_dark()
            assert isinstance(result, bool)