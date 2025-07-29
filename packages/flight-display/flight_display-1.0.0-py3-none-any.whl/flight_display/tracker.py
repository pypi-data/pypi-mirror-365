#!/usr/bin/env python3
"""
Aircraft Tracker - Airport Departure Board Style Display
Fetches nearby aircraft data and displays it like an airport departure board
"""

import requests
import json
import time
import math
import sys
from datetime import datetime
from typing import List, Dict, Optional
from tabulate import tabulate
from colorama import Fore, Back, Style, init
import re

from .config import TrackerConfig, load_config_from_file

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class AircraftTracker:
    def __init__(
        self,
        lat: float,
        lon: float,
        radius_km: float = 50,
        fetch_online_codes: bool = True,
        config: Optional[TrackerConfig] = None,
    ):
        """
        Initialize the aircraft tracker

        Args:
            lat: Your latitude
            lon: Your longitude
            radius_km: Search radius in kilometers
            fetch_online_codes: Whether to fetch airline codes from online sources
            config: Configuration object (if None, loads from file or uses defaults)
        """
        # Load configuration
        self.config = config if config is not None else load_config_from_file()

        self.lat = lat
        self.lon = lon
        self.radius_km = radius_km
        self.location_name = "Unknown Location"  # Will be set later

        # Cache for aircraft operator data to avoid repeated API calls
        self.operator_cache = {} if self.config.enable_caching else None

        # Initialize empty airline codes dictionary - will be populated from online sources
        self.airline_codes = {}

        # Fetch airline codes from online sources (only if requested)
        if fetch_online_codes and self.config.fetch_online_codes:
            self.update_airline_database_online()

    def haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = self.config.conversion.earth_radius_km  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    def fetch_aircraft_data(self) -> List[Dict]:
        """Fetch aircraft data from ADS-B Exchange API with enhanced error handling"""
        max_retries = self.config.retry.max_retries
        base_delay = (
            self.config.retry.base_delay
        )  # Base delay in seconds for ADS-B Exchange

        for attempt in range(max_retries):
            try:
                # Use OpenSky Network API (free, no key required, more reliable)
                # Get aircraft in a bounding box around our location
                # Calculate bounding box (rough approximation)
                lat_offset = (
                    self.radius_km / self.config.conversion.km_per_degree_lat
                )  # ~111 km per degree latitude
                lon_offset = self.radius_km / (
                    self.config.conversion.km_per_degree_lat
                    * math.cos(math.radians(self.lat))
                )

                min_lat = self.lat - lat_offset
                max_lat = self.lat + lat_offset
                min_lon = self.lon - lon_offset
                max_lon = self.lon + lon_offset

                # OpenSky Network API endpoint - more reliable than ADS-B Exchange
                opensky_url = f"{self.config.api.opensky_base_url}?lamin={min_lat}&lomin={min_lon}&lamax={max_lat}&lomax={max_lon}"

                print(
                    f"🌐 Fetching aircraft data from OpenSky Network (attempt {attempt + 1}/{max_retries})..."
                )

                # Try OpenSky Network API
                response = requests.get(
                    opensky_url, timeout=self.config.api.aircraft_data_timeout
                )

                # If OpenSky fails, we could try other sources
                if response.status_code != 200:
                    print("⚠️ OpenSky Network unavailable, this may be temporary...")
                    # Could try other sources here in the future
                    pass

                # Handle rate limiting (429 error)
                if response.status_code == 429:
                    retry_after = response.headers.get(
                        "Retry-After", base_delay * (2**attempt)
                    )
                    try:
                        wait_time = int(retry_after)
                    except (ValueError, TypeError):
                        wait_time = base_delay * (2**attempt)  # Exponential backoff

                    if attempt < max_retries - 1:
                        print(
                            f"⏳ API rate limit hit (HTTP 429). Waiting {wait_time} seconds before retry..."
                        )
                        print(
                            "   📊 OpenSky Network API has usage limits - this is normal during peak times"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ Rate limit exceeded after {max_retries} attempts.")
                        print(
                            f"💡 Please wait {wait_time} seconds before trying again."
                        )
                        print(
                            "   🌐 The OpenSky Network API is free but has rate limits to ensure fair usage"
                        )
                        return []

                response.raise_for_status()
                data = response.json()

                if not data or "states" not in data or not data["states"]:
                    print("⚠️ No aircraft data received from OpenSky Network")
                    return []

                aircraft_list = []

                for state in data["states"]:
                    if not state or len(state) < 17:
                        continue

                    # OpenSky Network format - state vector array
                    # [0] icao24, [1] callsign, [5] longitude, [6] latitude,
                    # [7] baro_altitude, [9] velocity, [10] true_track, [11] vertical_rate
                    icao24 = state[0].strip().upper() if state[0] else ""
                    callsign = state[1].strip() if state[1] else ""
                    longitude = state[5]
                    latitude = state[6]
                    altitude = state[7]  # barometric altitude in meters
                    velocity = state[9]  # ground speed in m/s
                    track = state[10]  # true track in degrees
                    vertical_rate = state[11]  # vertical rate in m/s

                    # Skip if missing essential data
                    if not icao24 or not latitude or not longitude:
                        continue

                    # Calculate distance from your location
                    distance = self.haversine_distance(
                        self.lat, self.lon, latitude, longitude
                    )

                    # Filter by radius (double check since API might return broader area)
                    if distance <= self.radius_km:
                        callsign_clean = callsign if callsign else f"ICAO{icao24}"

                        # Get operator information
                        operator_info = "Unknown"
                        aircraft_type_short = "UNK"
                        registration = (
                            "Unknown"  # OpenSky doesn't provide registration directly
                        )

                        # Try to get operator from callsign (faster)
                        if callsign:
                            operator_info = self.get_operator_from_callsign(
                                callsign_clean
                            )

                        # Convert units from OpenSky format
                        altitude_ft = (
                            int(altitude * self.config.conversion.meters_to_feet)
                            if altitude
                            else 0
                        )  # meters to feet
                        velocity_kt = (
                            int(velocity * self.config.conversion.ms_to_knots)
                            if velocity
                            else 0
                        )  # m/s to knots
                        vertical_rate_fpm = (
                            int(vertical_rate * self.config.conversion.ms_to_fpm)
                            if vertical_rate
                            else 0
                        )  # m/s to ft/min

                        aircraft = {
                            "icao24": icao24,
                            "callsign": callsign_clean,
                            "operator": operator_info,
                            "registration": registration,
                            "aircraft_type": aircraft_type_short,
                            "latitude": latitude,
                            "longitude": longitude,
                            "altitude": altitude_ft,
                            "velocity": velocity_kt,
                            "track": int(track) if track else 0,
                            "vertical_rate": vertical_rate_fpm,
                            "distance": distance,
                        }
                        aircraft_list.append(aircraft)

                # Sort by distance (closest first)
                aircraft_list.sort(key=lambda x: x["distance"])
                print(
                    f"✅ Successfully fetched data for {len(aircraft_list)} nearby aircraft"
                )
                return aircraft_list

            except requests.exceptions.RequestException as e:
                if "429" in str(e):
                    wait_time = base_delay * (2**attempt)
                    if attempt < max_retries - 1:
                        print(
                            f"⏳ Rate limit detected. Waiting {wait_time} seconds before retry..."
                        )
                        print(
                            "   📊 OpenSky API has usage limits - this is normal during peak times"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ Rate limit exceeded after all retries.")
                        print(f"💡 Please wait a few minutes before trying again.")
                        return []
                else:
                    print(f"⚠️ Network error (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt == max_retries - 1:
                        print("❌ All retry attempts failed due to network errors")
                        return []
                    time.sleep(base_delay)
                    continue

            except Exception as e:
                print(f"⚠️ Unexpected error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    print("❌ All retry attempts failed due to unexpected errors")
                    return []
                time.sleep(base_delay)
                continue

        # If we get here, all retries failed
        print("❌ Failed to fetch aircraft data after all retry attempts")
        print(
            "💡 The OpenSky Network API may be experiencing high load. Try again in a few minutes."
        )
        return []

    def format_departure_board(self, aircraft_list: List[Dict]) -> str:
        """Format aircraft data as departure board display with tabulate"""
        if not aircraft_list:
            return f"{Fore.RED}NO AIRCRAFT IN RANGE{Style.RESET_ALL}"

        # Prepare data for tabulate
        table_data = []
        current_time = datetime.now().strftime("%H:%M:%S")

        for aircraft in aircraft_list[
            : self.config.display.max_aircraft_displayed
        ]:  # Show top aircraft (configurable limit)
            callsign = aircraft["callsign"][
                : self.config.display.max_callsign_length
            ]  # Limit callsign length
            icao24 = aircraft["icao24"].upper()

            # Format operator name (truncate if too long)
            operator = aircraft.get("operator", "Unknown")
            if len(operator) > self.config.display.max_operator_length:
                operator = (
                    operator[
                        : self.config.display.max_operator_length
                        - len(self.config.display.operator_truncate_suffix)
                    ]
                    + self.config.display.operator_truncate_suffix
                )

            # Format aircraft type
            aircraft_type = aircraft.get(
                "aircraft_type", self.config.aircraft_types.unknown_aircraft_code
            )

            # Format altitude with color coding
            if aircraft["altitude"] > 0:
                if aircraft["altitude"] > self.config.display.high_altitude_threshold:
                    altitude = (
                        f"{Fore.CYAN}{aircraft['altitude']:,} ft{Style.RESET_ALL}"
                    )
                elif (
                    aircraft["altitude"] > self.config.display.medium_altitude_threshold
                ):
                    altitude = (
                        f"{Fore.YELLOW}{aircraft['altitude']:,} ft{Style.RESET_ALL}"
                    )
                else:
                    altitude = (
                        f"{Fore.GREEN}{aircraft['altitude']:,} ft{Style.RESET_ALL}"
                    )
            else:
                altitude = f"{Fore.RED}GROUND{Style.RESET_ALL}"

            # Format speed
            speed = f"{aircraft['velocity']} kt" if aircraft["velocity"] > 0 else "--"

            # Format track/heading
            track = f"{aircraft['track']:03d}°" if aircraft["track"] > 0 else "---"

            # Vertical speed with arrows and colors
            vs = aircraft["vertical_rate"]
            if vs > self.config.display.high_climb_threshold:
                vs_str = f"{Fore.GREEN}↑{abs(vs):4d}{Style.RESET_ALL}"
            elif vs < self.config.display.high_descent_threshold:
                vs_str = f"{Fore.RED}↓{abs(vs):4d}{Style.RESET_ALL}"
            elif vs > self.config.display.low_climb_threshold:
                vs_str = f"{Fore.LIGHTGREEN_EX}↗{abs(vs):4d}{Style.RESET_ALL}"
            elif vs < self.config.display.low_descent_threshold:
                vs_str = f"{Fore.LIGHTRED_EX}↘{abs(vs):4d}{Style.RESET_ALL}"
            else:
                vs_str = f"{Fore.WHITE}═══{Style.RESET_ALL}"

            # Format distance with color coding
            dist = aircraft["distance"]
            if dist < self.config.display.close_distance_threshold:
                distance = f"{Fore.RED}{dist:.1f} km{Style.RESET_ALL}"
            elif dist < self.config.display.medium_distance_threshold:
                distance = f"{Fore.YELLOW}{dist:.1f} km{Style.RESET_ALL}"
            else:
                distance = f"{Fore.GREEN}{dist:.1f} km{Style.RESET_ALL}"

            table_data.append(
                [
                    callsign,
                    operator,
                    aircraft_type,
                    altitude,
                    speed,
                    track,
                    vs_str,
                    distance,
                ]
            )

        # Create header
        headers = [
            f"{Fore.WHITE}{Style.BRIGHT}CALLSIGN{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}OPERATOR{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}TYPE{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}ALTITUDE{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}SPEED{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}TRACK{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}V/SPEED{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}DISTANCE{Style.RESET_ALL}",
        ]

        # Create the table
        table = tabulate(
            table_data,
            headers=headers,
            tablefmt=self.config.display.table_format,
            stralign=self.config.display.table_alignment,
            numalign=self.config.display.table_alignment,
        )

        # Add title and footer
        title = f"{Back.BLUE}{Fore.WHITE}{Style.BRIGHT}{self.config.display.departure_board_title:^{self.config.display.departure_board_width}}{Style.RESET_ALL}\n"
        footer = f"\n{Fore.CYAN}Last Update: {current_time} | Aircraft Count: {len(aircraft_list)} | Radius: {self.radius_km}km{Style.RESET_ALL}"
        footer += f"\n{Fore.MAGENTA}Monitoring: {self.location_name} ({self.lat:.4f}°, {self.lon:.4f}°){Style.RESET_ALL}"
        footer += f"\n{Fore.LIGHTBLUE_EX}Note: Operator info cached for performance. Some private aircraft may show 'Unknown'.{Style.RESET_ALL}"

        return title + table + footer

    def run_display(self, update_interval: int = 10):
        """Run the continuous display"""
        print("Starting Aircraft Tracker...")
        print(
            f"Monitoring aircraft within {self.radius_km}km of {self.lat:.4f}, {self.lon:.4f}"
        )
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                # Clear screen (works on most terminals)
                print("\033[2J\033[H")

                aircraft_data = self.fetch_aircraft_data()
                display = self.format_departure_board(aircraft_data)
                print(display)

                time.sleep(update_interval)

        except KeyboardInterrupt:
            print("\nStopping Aircraft Tracker...")

    def get_operator_from_callsign(self, callsign: str) -> str:
        """Extract operator from callsign using ICAO airline codes"""
        if not callsign or len(callsign) < 3:
            return "Unknown"

        # Extract the airline code (first 3 characters for most airlines)
        airline_code = callsign[:3].upper()

        # Check if it's in our airline codes database
        if airline_code in self.airline_codes:
            return self.airline_codes[airline_code]

        # If not found, try 2-character codes (some airlines use 2-char codes)
        if len(callsign) >= 2:
            airline_code_2 = callsign[:2].upper()
            if airline_code_2 in self.airline_codes:
                return self.airline_codes[airline_code_2]

        # Check for common patterns
        if callsign.startswith("N") and len(callsign) >= 4:
            return "Private/Corporate"
        elif any(
            callsign.startswith(prefix)
            for prefix in self.config.registration.private_registration_patterns or []
        ):
            return "Private/Corporate"
        elif any(
            callsign.startswith(prefix)
            for prefix in self.config.registration.private_callsign_patterns or []
        ):
            return "Private/Corporate"

        return "Unknown"

    def fetch_aircraft_details(self, icao24: str) -> Dict[str, str]:
        """
        Fetch additional aircraft details using the ICAO24 code
        This uses alternative methods to get operator info
        """
        # Check cache first
        if self.operator_cache is not None and icao24 in self.operator_cache:
            return self.operator_cache[icao24]

        details = {
            "registration": "Unknown",
            "operator": "Unknown",
            "aircraft_type": "Unknown",
            "country": "Unknown",
        }

        # Try multiple sources for aircraft data
        sources_tried = []

        try:
            # Source 1: Try FlightAware API (if available)
            # Note: This would require API key registration
            # We'll skip this for now to keep it free
            pass

        except Exception:
            pass

        try:
            # Source 2: Try ADS-B Exchange aircraft database
            adsbx_db_url = f"{self.config.api.adsbx_db_base_url}?icao={icao24}"
            response = requests.get(
                adsbx_db_url, timeout=self.config.api.aircraft_details_timeout
            )
            sources_tried.append("ADS-B Exchange")

            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    aircraft_info = data[0]
                    details["registration"] = aircraft_info.get("r", "Unknown")
                    details["aircraft_type"] = aircraft_info.get("t", "Unknown")
                    details["operator"] = aircraft_info.get("ownop", "Unknown")

                    # If we got good data, we can stop here
                    if details["operator"] != "Unknown":
                        if self.operator_cache is not None:
                            self.operator_cache[icao24] = details
                        return details

        except Exception:
            pass

        try:
            # Source 2: Try alternative aviation databases
            # We can add more sources here as needed
            pass

        except Exception:
            pass

        try:
            # Source 3: Try pattern matching and country detection
            # This is our fallback method that doesn't require external APIs
            pass

        except Exception:
            pass

        # If still no operator found, try pattern matching on registration
        if details["operator"] == "Unknown" and details["registration"] != "Unknown":
            reg = details["registration"]

            # Check against configured registration patterns
            if self.config.registration.registration_patterns:
                for prefix, (
                    operator,
                    country,
                ) in self.config.registration.registration_patterns.items():
                    if reg.upper().startswith(prefix.upper()):
                        details["operator"] = operator
                        details["country"] = country
                        break

        # Cache the result
        if self.operator_cache is not None:
            self.operator_cache[icao24] = details
        return details

    def get_aircraft_type_short(self, aircraft_type: str) -> str:
        """Convert long aircraft type names to shorter versions for display"""
        if not aircraft_type or aircraft_type == "Unknown":
            return self.config.aircraft_types.unknown_aircraft_code

        # Common aircraft type mappings
        type_mappings = self.config.aircraft_types.type_mappings or {}

        for full_name, short_name in type_mappings.items():
            if full_name.lower() in aircraft_type.lower():
                return short_name

        # If no mapping found, try to extract model number
        import re

        match = re.search(
            self.config.aircraft_types.model_number_pattern, aircraft_type.upper()
        )
        if match:
            return match.group()

        # Return first 4 characters if nothing else works
        return aircraft_type[: self.config.aircraft_types.fallback_code_length].upper()

    def get_current_location(self) -> tuple[float, float, str]:
        """
        Get current location using IP-based geolocation
        Returns (latitude, longitude, location_string) tuple
        """
        try:
            # Try ipapi.co first (reliable and free)
            response = requests.get(
                self.config.api.ipapi_url, timeout=self.config.api.geolocation_timeout
            )
            if response.status_code == 200:
                data = response.json()
                lat = data.get("latitude")
                lon = data.get("longitude")
                if lat and lon:
                    city = data.get("city", "Unknown")
                    region = data.get("region", "Unknown")
                    country = data.get("country_name", "Unknown")
                    location_str = f"{city}, {region}, {country}"
                    print(f"📍 Location detected: {location_str}")
                    print(f"🌐 Coordinates: {lat:.4f}°, {lon:.4f}°")
                    return float(lat), float(lon), location_str
        except:
            pass

        try:
            # Fallback to httpbin.org/ip + ipinfo.io
            ip_response = requests.get(self.config.api.httpbin_ip_url, timeout=5)
            if ip_response.status_code == 200:
                ip = ip_response.json().get("origin", "").split(",")[0]

                location_response = requests.get(
                    f"{self.config.api.ipinfo_base_url}/{ip}/json", timeout=5
                )
                if location_response.status_code == 200:
                    data = location_response.json()
                    loc = data.get("loc", "")
                    if loc and "," in loc:
                        lat, lon = map(float, loc.split(","))
                        city = data.get("city", "Unknown")
                        region = data.get("region", "Unknown")
                        country = data.get("country", "Unknown")
                        location_str = f"{city}, {region}, {country}"
                        print(f"📍 Location detected: {location_str}")
                        print(f"🌐 Coordinates: {lat:.4f}°, {lon:.4f}°")
                        return lat, lon, location_str
        except:
            pass

        # If all fails, use default configured coordinates
        print("⚠️  Could not detect location automatically.")
        print(
            f"🏙️  Using default coordinates ({self.config.location.default_location_name}): {self.config.location.default_latitude:.4f}°, {self.config.location.default_longitude:.4f}°"
        )
        print("💡 You can manually set coordinates in the main() function if needed.")
        return (
            self.config.location.default_latitude,
            self.config.location.default_longitude,
            self.config.location.default_location_name,
        )

    def fetch_airline_codes_online(self) -> Dict[str, str]:
        """
        Fetch airline ICAO codes from online sources
        Returns a dictionary of ICAO codes to airline names
        """
        online_codes = {}

        print("🌐 Fetching airline codes from online sources...")

        # Source 1: Try OpenFlights airline database (community maintained)
        try:
            openflights_url = self.config.api.openflights_airlines_url
            response = requests.get(
                openflights_url, timeout=self.config.api.airline_codes_timeout
            )
            if response.status_code == 200:
                lines = response.text.strip().split("\n")
                for line in lines:
                    try:
                        parts = line.split(",")
                        if len(parts) >= 4:
                            # OpenFlights format: ID,Name,Alias,IATA,ICAO,Callsign,Country,Active
                            icao_code = parts[4].strip('"').strip()
                            airline_name = parts[1].strip('"').strip()
                            if icao_code and len(icao_code) == 3 and icao_code != "\\N":
                                online_codes[icao_code.upper()] = airline_name
                    except:
                        # Skip malformed lines
                        continue

                if online_codes:
                    print(
                        f"✅ Fetched {len(online_codes)} airline codes from OpenFlights database"
                    )
                    return online_codes

        except Exception as e:
            print(f"⚠️ OpenFlights source failed: {e}")

        # Source 2: Try a different aviation database
        try:
            # Alternative source - could try other aviation APIs here
            # For now, we skip to avoid hardcoding more sources
            pass

        except Exception as e:
            print(f"⚠️ Alternative source failed: {e}")

        # Source 3: Try Wikipedia's airline codes (if available as structured data)
        try:
            # This would require parsing Wikipedia or finding a structured data source
            # For now, we'll skip this to avoid hardcoding
            pass

        except Exception as e:
            print(f"⚠️ Wikipedia source failed: {e}")

        # If no online sources work, return empty dict
        if not online_codes:
            print(
                "⚠️ All online sources failed. Aircraft operator identification will be limited."
            )
            print(
                "💡 The system will rely on OpenSky metadata and registration patterns for operator detection."
            )

        return online_codes

    def update_airline_database_online(self):
        """Update the airline database with codes fetched from online sources"""
        try:
            online_codes = self.fetch_airline_codes_online()
            if online_codes:
                # Merge with existing codes (online codes take precedence for conflicts)
                original_count = len(self.airline_codes)
                self.airline_codes.update(online_codes)
                new_count = len(self.airline_codes)
                added_count = new_count - original_count
                print(
                    f"📊 Airline database updated: {original_count} → {new_count} codes (+{added_count} new)"
                )
            else:
                print("📊 No airline codes fetched from online sources.")
                print("🔍 Operator identification will rely on:")
                print("   • ADS-B Exchange aircraft metadata")
                print("   • Aircraft registration pattern matching")
                print("   • Country-based operator classification")
        except Exception as e:
            print(f"⚠️ Error updating airline database: {e}")
            print("🔍 Falling back to metadata-based operator detection.")
