"""
Configuration management for the email server.
"""

import configparser
import os
import socket
from pathlib import Path
from typing import Optional


class Config:
    """Configuration manager for the email server."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file. If None, looks for cfg.ini in current directory.
        """
        self.config = configparser.ConfigParser()
        
        # Set default values
        self._set_defaults()
        
        # Load from file if exists
        if config_file is None:
            config_file = "cfg.ini"
        
        if os.path.exists(config_file):
            self.config.read(config_file)
        
        # Override with environment variables if set
        self._load_from_env()

        # Resolve auto-detection after all config is loaded
        self._resolve_auto_config()
    
    def _set_defaults(self):
        """Set default configuration values."""
        self.config.add_section('smtpd')
        self.config.set('smtpd', 'host', 'auto')  # Auto-detect best binding method
        self.config.set('smtpd', 'port', '25')

        self.config.add_section('rest')
        self.config.set('rest', 'port', '14000')
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # SMTP configuration
        if 'SMTP_HOST' in os.environ:
            self.config.set('smtpd', 'host', os.environ['SMTP_HOST'])
        if 'SMTP_PORT' in os.environ:
            self.config.set('smtpd', 'port', os.environ['SMTP_PORT'])
        
        # REST API configuration
        if 'REST_PORT' in os.environ:
            self.config.set('rest', 'port', os.environ['REST_PORT'])
    
    @property
    def smtp_host(self) -> str:
        """Get SMTP server host."""
        return self.config.get('smtpd', 'host')
    
    @property
    def smtp_port(self) -> int:
        """Get SMTP server port."""
        return self.config.getint('smtpd', 'port')
    
    @property
    def rest_host(self) -> str:
        """Get REST API host (same as SMTP host)."""
        return self.smtp_host
    
    @property
    def rest_port(self) -> int:
        """Get REST API port."""
        return self.config.getint('rest', 'port')
    
    def save(self, config_file: str = "cfg.ini"):
        """
        Save current configuration to file.
        
        Args:
            config_file: Path to save configuration file.
        """
        with open(config_file, 'w') as f:
            self.config.write(f)

    def _resolve_auto_config(self):
        """Resolve 'auto' configuration values to actual values."""
        # Resolve SMTP host auto-detection
        if self.config.get('smtpd', 'host') == 'auto':
            optimal_host = self._detect_optimal_bind_address()
            self.config.set('smtpd', 'host', optimal_host)

    def _detect_optimal_bind_address(self) -> str:
        """
        Detect the optimal bind address for maximum compatibility.

        Returns:
            The best bind address for the current system
        """
        # Strategy:
        # 1. Try IPv6 dual-stack (::) - works on most modern systems
        # 2. Fall back to IPv4 (0.0.0.0) if IPv6 is not available
        # 3. Final fallback to localhost (127.0.0.1)

        # Test IPv6 dual-stack support
        if self._test_bind_address('::', socket.AF_INET6):
            return '::'

        # Test IPv4 all interfaces
        if self._test_bind_address('0.0.0.0', socket.AF_INET):
            return '0.0.0.0'

        # Final fallback to localhost
        return '127.0.0.1'

    def _test_bind_address(self, address: str, family: int) -> bool:
        """
        Test if we can bind to a specific address.

        Args:
            address: IP address to test
            family: Socket family (AF_INET or AF_INET6)

        Returns:
            True if binding is successful, False otherwise
        """
        try:
            # Create a test socket
            test_socket = socket.socket(family, socket.SOCK_STREAM)
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # For IPv6, enable dual-stack if possible
            if family == socket.AF_INET6:
                try:
                    test_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
                except (AttributeError, OSError):
                    # Some systems don't support this option
                    pass

            # Try to bind to a high port for testing
            test_port = 0  # Let the system choose an available port
            test_socket.bind((address, test_port))
            test_socket.close()
            return True

        except (OSError, socket.error):
            return False

    def get_bind_info(self) -> dict:
        """
        Get detailed information about the current bind configuration.

        Returns:
            Dictionary with bind information
        """
        host = self.smtp_host

        info = {
            'host': host,
            'port': self.smtp_port,
            'description': '',
            'supports_ipv4': False,
            'supports_ipv6': False
        }

        if host == '::':
            info['description'] = 'IPv6 dual-stack (supports both IPv4 and IPv6)'
            info['supports_ipv4'] = True
            info['supports_ipv6'] = True
        elif host == '0.0.0.0':
            info['description'] = 'IPv4 all interfaces'
            info['supports_ipv4'] = True
        elif host == '127.0.0.1':
            info['description'] = 'IPv4 localhost only'
            info['supports_ipv4'] = True
        else:
            info['description'] = f'Custom address: {host}'
            # Try to determine if it's IPv4 or IPv6
            try:
                socket.inet_pton(socket.AF_INET, host)
                info['supports_ipv4'] = True
            except socket.error:
                try:
                    socket.inet_pton(socket.AF_INET6, host)
                    info['supports_ipv6'] = True
                except socket.error:
                    pass

        return info
