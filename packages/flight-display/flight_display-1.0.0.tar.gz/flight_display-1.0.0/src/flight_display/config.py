#!/usr/bin/env python3
"""
Configuration module for Aircraft Tracker
Contains all configurable parameters with sensible defaults
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import os
import json


@dataclass
class LocationConfig:
    """Location-related configuration"""

    # Default fallback location (NYC)
    default_latitude: float = 40.7128
    default_longitude: float = -74.0060
    default_location_name: str = "New York City, NY, USA"

    # Default search radius in kilometers
    default_radius_km: float = 50.0


@dataclass
class APIConfig:
    """API endpoints and timeouts"""

    # Aircraft data APIs
    opensky_base_url: str = "https://opensky-network.org/api/states/all"
    adsbx_db_base_url: str = "https://adsbexchange.com/api/dbsearch.php"

    # Geolocation APIs
    ipapi_url: str = "http://ipapi.co/json/"
    httpbin_ip_url: str = "https://httpbin.org/ip"
    ipinfo_base_url: str = "https://ipinfo.io"

    # Airline codes data source
    openflights_airlines_url: str = (
        "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat"
    )

    # Timeouts (seconds)
    aircraft_data_timeout: int = 15
    geolocation_timeout: int = 10
    airline_codes_timeout: int = 10
    aircraft_details_timeout: int = 5


@dataclass
class RetryConfig:
    """Retry and rate limiting configuration"""

    max_retries: int = 3
    base_delay: int = 5  # Base delay in seconds
    exponential_backoff: bool = True


@dataclass
class DisplayConfig:
    """Display formatting configuration"""

    # Aircraft display limits
    max_aircraft_displayed: int = 12
    max_callsign_length: int = 10
    max_operator_length: int = 18
    operator_truncate_suffix: str = "..."

    # Altitude thresholds for color coding (feet)
    high_altitude_threshold: int = 30000
    medium_altitude_threshold: int = 10000

    # Speed thresholds for vertical rate indicators (ft/min)
    high_climb_threshold: int = 500
    high_descent_threshold: int = -500
    low_climb_threshold: int = 100
    low_descent_threshold: int = -100

    # Distance thresholds for color coding (km)
    close_distance_threshold: float = 10.0
    medium_distance_threshold: float = 25.0

    # Display formatting
    departure_board_title: str = "AIRCRAFT DEPARTURE BOARD"
    departure_board_width: int = 100

    # Table format
    table_format: str = "fancy_grid"
    table_alignment: str = "center"

    # Update interval (seconds)
    default_update_interval: int = 10


@dataclass
class ConversionFactors:
    """Unit conversion factors"""

    # Distance
    km_per_degree_lat: float = 111.0  # Approximate km per degree latitude
    earth_radius_km: float = 6371.0  # Earth's radius for Haversine formula

    # Aviation units
    meters_to_feet: float = 3.28084
    ms_to_knots: float = 1.94384
    ms_to_fpm: float = 196.85  # meters/second to feet/minute


@dataclass
class AircraftTypeConfig:
    """Aircraft type mapping configuration"""

    # Common aircraft type mappings (full name -> short code)
    type_mappings: Optional[Dict[str, str]] = None

    # Pattern for extracting model numbers
    model_number_pattern: str = r"[A-Z]\d{3}"

    # Fallback aircraft code
    unknown_aircraft_code: str = "UNK"
    fallback_code_length: int = 4

    def __post_init__(self):
        if self.type_mappings is None:
            self.type_mappings = {
                "Boeing 737": "B737",
                "Boeing 747": "B747",
                "Boeing 757": "B757",
                "Boeing 767": "B767",
                "Boeing 777": "B777",
                "Boeing 787": "B787",
                "Airbus A320": "A320",
                "Airbus A321": "A321",
                "Airbus A330": "A330",
                "Airbus A340": "A340",
                "Airbus A350": "A350",
                "Airbus A380": "A380",
                "Embraer": "EMB",
                "Bombardier": "CRJ",
                "McDonnell Douglas": "MD",
            }


@dataclass
class RegistrationConfig:
    """Aircraft registration pattern configuration"""

    # Registration patterns for operator detection
    registration_patterns: Optional[Dict[str, Tuple[str, str]]] = (
        None  # prefix -> (operator, country)
    )

    # Private aircraft callsign patterns
    private_callsign_patterns: Optional[List[str]] = None
    private_registration_patterns: Optional[List[str]] = None

    def __post_init__(self):
        if self.registration_patterns is None:
            self.registration_patterns = {
                "N": ("US Registered", "United States"),
                "G-": ("UK Registered", "United Kingdom"),
                "D-": ("German Registered", "Germany"),
                "F-": ("French Registered", "France"),
                "VT-": ("Indian Registered", "India"),
                "C-": ("Canadian Registered", "Canada"),
                "JA": ("Japanese Registered", "Japan"),
                "HL": ("South Korean Registered", "South Korea"),
                "VH-": ("Australian Registered", "Australia"),
                "ZK-": ("New Zealand Registered", "New Zealand"),
            }

        if self.private_callsign_patterns is None:
            self.private_callsign_patterns = ["JA", "HL", "VH", "ZK"]

        if self.private_registration_patterns is None:
            self.private_registration_patterns = ["G-", "D-", "F-", "I-", "OE-"]


@dataclass
class TrackerConfig:
    """Main configuration class containing all sub-configurations"""

    location: LocationConfig = field(default_factory=LocationConfig)
    api: APIConfig = field(default_factory=APIConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    conversion: ConversionFactors = field(default_factory=ConversionFactors)
    aircraft_types: AircraftTypeConfig = field(default_factory=AircraftTypeConfig)
    registration: RegistrationConfig = field(default_factory=RegistrationConfig)

    # Feature flags
    fetch_online_codes: bool = True
    enable_caching: bool = True
    enable_color_output: bool = True


def load_config_from_file(config_path: Optional[str] = None) -> TrackerConfig:
    """
    Load configuration from a JSON file

    Args:
        config_path: Path to the configuration file. If None, looks for config.json
                    in the current directory or uses defaults.

    Returns:
        TrackerConfig instance with loaded or default values
    """
    if config_path is None:
        # Look for config.json in current directory
        config_path = "config.json"

    config = TrackerConfig()

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)

            # Update configuration with loaded values
            # This is a simple implementation - could be made more sophisticated
            for section, values in config_data.items():
                if hasattr(config, section) and isinstance(values, dict):
                    section_config = getattr(config, section)
                    for key, value in values.items():
                        if hasattr(section_config, key):
                            setattr(section_config, key, value)

            print(f"✅ Configuration loaded from {config_path}")

        except Exception as e:
            print(f"⚠️ Error loading configuration from {config_path}: {e}")
            print("🔄 Using default configuration")

    return config


def save_config_to_file(config: TrackerConfig, config_path: str = "config.json"):
    """
    Save configuration to a JSON file

    Args:
        config: TrackerConfig instance to save
        config_path: Path where to save the configuration file
    """
    try:
        # Convert dataclass to dictionary for JSON serialization
        config_dict = {}

        for field_name in config.__dataclass_fields__:
            field_value = getattr(config, field_name)
            if hasattr(field_value, "__dataclass_fields__"):
                # It's a dataclass, convert to dict
                config_dict[field_name] = {
                    sub_field: getattr(field_value, sub_field)
                    for sub_field in field_value.__dataclass_fields__
                }
            else:
                # It's a simple value
                config_dict[field_name] = field_value

        with open(config_path, "w") as f:
            json.dump(config_dict, f, indent=2)

        print(f"✅ Configuration saved to {config_path}")

    except Exception as e:
        print(f"❌ Error saving configuration to {config_path}: {e}")


def create_example_config(config_path: str = "config_example.json"):
    """
    Create an example configuration file with all available options

    Args:
        config_path: Path where to save the example configuration
    """
    config = TrackerConfig()
    save_config_to_file(config, config_path)
    print(f"📝 Example configuration created at {config_path}")
    print("💡 Copy this file to 'config.json' and modify as needed")


# Create a default global configuration instance
DEFAULT_CONFIG = TrackerConfig()
