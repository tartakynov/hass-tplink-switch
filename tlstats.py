"""
TP-Link TL-SG1016PE Network Switch Monitor
Handles authentication and fetching port statistics via HTTP
"""

import asyncio
import logging
import re
from typing import Optional, List
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)


class TLStats:
    """
    Client for connecting to TP-Link TL-SG1016PE network switch admin console
    and fetching port monitoring statistics.
    """

    def __init__(self, host: str, username: str, password: str, port: int = 80):
        """
        Initialize the TLStats client.

        Args:
            host: IP address or hostname of the switch
            username: Admin username
            password: Admin password
            port: HTTP port (default: 80)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.base_url = f"http://{host}:{port}" if port != 80 else f"http://{host}"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self._authenticated = False
        self.link_statuses: Optional[List[int]] = None

    def _authenticate(self) -> bool:
        """
        Authenticate with the switch using username and password.

        Returns:
            True if authentication successful, False otherwise
        """
        auth_url = urljoin(self.base_url, '/logon.cgi')

        auth_data = {
            'username': self.username,
            'password': self.password,
            'cpassword': '',
            'logon': 'Login'
        }

        try:
            # Clear any existing cookies
            self.session.cookies.clear()

            # Send authentication request
            response = self.session.post(
                auth_url,
                data=auth_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10,
                verify=False  # Skip SSL verification as per curl --insecure
            )

            if response.status_code != 200:
                logger.error(f"Authentication failed with status code: {response.status_code}")
                return False

            # Parse the response to check if authentication was successful
            # Look for logonInfo array in the response
            logon_pattern = r'var\s+logonInfo\s*=\s*new\s+Array\s*\(\s*(\d+)'
            match = re.search(logon_pattern, response.text)

            if match:
                logon_status = int(match.group(1))
                if logon_status == 0:
                    # Authentication successful
                    logger.debug("Authentication successful")
                    self._authenticated = True

                    # Check if we got the H_P_SSID cookie
                    if 'H_P_SSID' in self.session.cookies:
                        logger.debug(f"Session cookie obtained: H_P_SSID={self.session.cookies['H_P_SSID']}")
                    else:
                        logger.warning("H_P_SSID cookie not found in response")

                    return True
                else:
                    logger.error(f"Authentication failed with logonInfo status: {logon_status}")
                    return False
            else:
                logger.error("Could not find logonInfo in authentication response")
                return False

        except requests.RequestException as e:
            logger.error(f"Authentication request failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            return False

    def _fetch_port_statistics(self) -> Optional[List[int]]:
        """
        Fetch port statistics from the switch.

        Returns:
            List of port link statuses (18 elements: 16 ethernet + 2 SFP) if successful, None otherwise
        """
        if not self._authenticated:
            logger.error("Cannot fetch statistics: not authenticated")
            return None

        stats_url = urljoin(self.base_url, '/PortStatisticsRpm.htm')

        try:
            # Send request with session cookie
            response = self.session.get(
                stats_url,
                headers={'Referer': stats_url},
                timeout=10,
                verify=False
            )

            if response.status_code != 200:
                logger.error(f"Failed to fetch statistics with status code: {response.status_code}")
                return None

            # Parse the response to extract the link status array
            # Look for all_info object with link_status array
            status_pattern = r'var\s+all_info\s*=\s*\{[^}]*link_status:\s*\[([^\]]+)\]'
            match = re.search(status_pattern, response.text)

            if match:
                status_str = match.group(1)
                # Parse the comma-separated values
                try:
                    status_values = [int(x.strip()) for x in status_str.split(',')]
                    logger.debug(f"Successfully fetched port link statuses: {status_values}")
                    return status_values
                except ValueError as e:
                    logger.error(f"Failed to parse link status values: {e}")
                    return None
            else:
                logger.error("Could not find all_info link_status array in response")
                # Check if we need to re-authenticate
                if 'logonInfo' in response.text:
                    logger.info("Session expired, need to re-authenticate")
                    self._authenticated = False
                return None

        except requests.RequestException as e:
            logger.error(f"Statistics request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching statistics: {e}")
            return None

    def get_port_statuses(self) -> Optional[List[int]]:
        """
        Get current port link statuses from the switch.
        Re-authenticates on every call to avoid session persistence issues.

        Returns:
            List of port link statuses (18 elements: 16 ethernet + 2 SFP) if successful, None otherwise
        """
        # Always re-authenticate on every call
        self._authenticated = False
        if not self._authenticate():
            logger.error("Failed to authenticate with switch")
            return None

        # Fetch port statistics
        statuses = self._fetch_port_statistics()

        return statuses

    async def update(self) -> bool:
        """
        Asynchronously fetch and update port link statuses from the switch.
        Uses the host and credentials provided in the constructor.

        Returns:
            True if link statuses fetched successfully, False otherwise
        """
        try:
            statuses = await asyncio.to_thread(self.get_port_statuses)

            if statuses is not None:
                self.link_statuses = statuses
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error during update: {e}")
            return False

    def close(self):
        """
        Close the session and cleanup resources.
        """
        self.session.close()
        self._authenticated = False
