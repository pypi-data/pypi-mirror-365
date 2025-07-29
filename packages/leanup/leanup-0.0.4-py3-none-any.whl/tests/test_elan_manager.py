#!/usr/bin/env python

"""Tests for `elan_manager` module."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from leanup.elan_manager import ElanManager
from leanup.const import OS_TYPE


@pytest.fixture
def manager():
    """Create a test ElanManager instance."""
    return ElanManager()


@pytest.fixture
def mock_elan_home(tmp_path):
    """Create a temporary elan home directory."""
    elan_home = tmp_path / '.elan'
    elan_home.mkdir()
    return elan_home


def test_manager_initialization(manager):
    """Test ElanManager initialization."""
    assert manager is not None
    assert manager.executor is not None
    assert manager.elan_home is not None
    assert manager.elan_bin_dir is not None


def test_get_download_url(manager):
    """Test download URL generation."""
    url = manager.get_download_url()
    assert url is not None
    assert 'elan' in url.lower()
    
    if OS_TYPE == 'Windows':
        assert url.endswith('.exe')
    else:
        assert url.endswith('.sh')


def test_get_elan_executable_not_found(manager, mock_elan_home):
    """Test get_elan_executable when elan is not installed."""
    manager.elan_home = mock_elan_home
    manager.elan_bin_dir = mock_elan_home / 'bin'
    
    with patch('shutil.which', return_value=None):
        result = manager.get_elan_executable()
        assert result is None


def test_get_elan_executable_found(manager, mock_elan_home):
    """Test get_elan_executable when elan is installed."""
    manager.elan_home = mock_elan_home
    manager.elan_bin_dir = mock_elan_home / 'bin'
    manager.elan_bin_dir.mkdir()
    
    elan_exe = 'elan.exe' if OS_TYPE == 'Windows' else 'elan'
    elan_path = manager.elan_bin_dir / elan_exe
    elan_path.touch()
    
    result = manager.get_elan_executable()
    assert result == elan_path


def test_is_elan_installed(manager):
    """Test elan installation detection."""
    with patch.object(manager, 'get_elan_executable', return_value=None):
        assert not manager.is_elan_installed()
    
    with patch.object(manager, 'get_elan_executable', return_value=Path('/usr/bin/elan')):
        assert manager.is_elan_installed()


def test_get_elan_version(manager):
    """Test elan version detection."""
    with patch.object(manager, 'get_elan_executable', return_value=None):
        assert manager.get_elan_version() is None
    
    mock_path = Path('/usr/bin/elan')
    with patch.object(manager, 'get_elan_executable', return_value=mock_path):
        with patch.object(manager.executor, 'execute', return_value=('elan 1.4.2', '', 0)):
            version = manager.get_elan_version()
            assert '1.4.2' in version


def test_get_status_info_not_installed(manager):
    """Test status info when elan is not installed."""
    with patch.object(manager, 'is_elan_installed', return_value=False):
        info = manager.get_status_info()
        
        assert info['installed'] is False
        assert info['version'] is None
        assert info['executable'] is None
        assert info['toolchains'] == []


def test_get_status_info_installed(manager):
    """Test status info when elan is installed."""
    with patch.object(manager, 'is_elan_installed', return_value=True):
        with patch.object(manager, 'get_elan_version', return_value='1.4.2'):
            with patch.object(manager, 'get_elan_executable', return_value=Path('/usr/bin/elan')):
                with patch.object(manager, 'get_installed_toolchains', return_value=['stable']):
                    info = manager.get_status_info()
                    
                    assert info['installed'] is True
                    assert info['version'] == '1.4.2'
                    assert info['executable'] == '/usr/bin/elan'
                    assert info['toolchains'] == ['stable']


def test_get_installed_toolchains(manager):
    """Test getting installed toolchains."""
    mock_path = Path('/usr/bin/elan')
    
    with patch.object(manager, 'get_elan_executable', return_value=None):
        toolchains = manager.get_installed_toolchains()
        assert toolchains == []
    
    with patch.object(manager, 'get_elan_executable', return_value=mock_path):
        output = "stable\nleanprover/lean4:nightly (default)\n"
        with patch.object(manager.executor, 'execute', return_value=(output, '', 0)):
            toolchains = manager.get_installed_toolchains()
            assert 'stable' in toolchains
            assert 'leanprover/lean4:nightly' in toolchains


@patch('requests.get')
def test_download_installer_success(mock_get, manager, tmp_path):
    """Test successful installer download."""
    # Mock successful HTTP response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.iter_content.return_value = [b'test content']
    mock_get.return_value = mock_response
    
    target_path = tmp_path / 'installer'
    result = manager.download_installer('http://example.com/installer', target_path)
    
    assert result is True
    assert target_path.exists()
    assert target_path.read_bytes() == b'test content'


@patch('requests.get')
def test_download_installer_failure(mock_get, manager, tmp_path):
    """Test installer download failure."""
    # Mock HTTP error
    mock_get.side_effect = Exception("Network error")
    
    target_path = tmp_path / 'installer'
    result = manager.download_installer('http://example.com/installer', target_path)
    
    assert result is False
    assert not target_path.exists()


def test_proxy_elan_command_not_installed(manager):
    """Test elan command proxy when elan is not installed."""
    with patch.object(manager, 'get_elan_executable', return_value=None):
        exit_code = manager.proxy_elan_command(['--help'])
        assert exit_code == 1


@patch('subprocess.run')
def test_proxy_elan_command_success(mock_run, manager):
    """Test successful elan command proxy."""
    mock_path = Path('/usr/bin/elan')
    mock_result = Mock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    
    with patch.object(manager, 'get_elan_executable', return_value=mock_path):
        exit_code = manager.proxy_elan_command(['--help'])
        assert exit_code == 0
        mock_run.assert_called_once_with(['/usr/bin/elan', '--help'], check=False)


@patch('subprocess.run')
def test_proxy_elan_command_failure(mock_run, manager):
    """Test failed elan command proxy."""
    mock_path = Path('/usr/bin/elan')
    mock_run.side_effect = Exception("Command failed")
    
    with patch.object(manager, 'get_elan_executable', return_value=mock_path):
        exit_code = manager.proxy_elan_command(['invalid'])
        assert exit_code == 1
