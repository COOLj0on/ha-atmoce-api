"""Constants for the Atmoce Cloud API integration.

This module defines all configuration keys, domain identifiers, and default
values used throughout the Atmoce integration.
"""

# Integration domain identifier
DOMAIN = "atmoce"

# Atmoce Cloud web interface URL
WEB_BASE_URL = "https://www.atmocecloud.com"

# Default polling interval in seconds (15 minutes)
DEFAULT_SCAN_INTERVAL = 15 * 60

# Data source identifier
SOURCE_CLOUD = "Cloud API"

# Configuration keys used in config_entry.data
CONF_SITE_ID = "site_id"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
