#!/usr/bin/env python3
"""
CLI interface for Flight Display - Aircraft Tracker
"""

import sys
import argparse
import time
from typing import Optional

from .tracker import AircraftTracker
from .config import TrackerConfig, load_config_from_file, create_example_config


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI"""
    parser = argparse.ArgumentParser(
        prog="flight-display",
        description="Aircraft Tracker - Airport Departure Board Style Display for nearby aircraft",
        epilog="""
Examples:
  flight-display                              # Auto-detect location and start tracking
  flight-display --lat 40.7128 --lon -74.0060  # Use specific coordinates (NYC)
  flight-display --radius 100                 # Set custom search radius (100km)
  flight-display --interval 30                # Update every 30 seconds
  flight-display --no-online-db               # Skip online airline database
  flight-display --config my-config.json      # Use custom configuration file
  flight-display --create-config              # Create example configuration file

Configuration:
  The application supports configuration files for customizing all aspects of the display,
  including colors, thresholds, API endpoints, and more. Use --create-config to generate
  an example configuration file with all available options.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Configuration options
    config_group = parser.add_argument_group("Configuration Options")
    config_group.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to configuration file (default: config.json in current directory)",
    )
    config_group.add_argument(
        "--create-config",
        action="store_true",
        help="Create an example configuration file and exit",
    )

    # Location options
    location_group = parser.add_argument_group("Location Options")
    location_group.add_argument(
        "--lat",
        "--latitude",
        type=float,
        help="Your latitude coordinate (decimal degrees)",
    )
    location_group.add_argument(
        "--lon",
        "--longitude",
        type=float,
        help="Your longitude coordinate (decimal degrees)",
    )

    # Display options
    display_group = parser.add_argument_group("Display Options")
    display_group.add_argument(
        "--radius",
        "-r",
        type=float,
        help="Search radius in kilometers (default: from config or 50)",
    )
    display_group.add_argument(
        "--interval",
        "-i",
        type=int,
        help="Update interval in seconds (default: from config or 10)",
    )
    display_group.add_argument(
        "--max-radius",
        type=float,
        default=200,
        help="Maximum search radius for adaptive search (default: 200)",
    )

    # Data options
    data_group = parser.add_argument_group("Data Options")
    data_group.add_argument(
        "--no-online-db",
        action="store_true",
        help="Skip fetching online airline database (faster startup, less operator info)",
    )
    data_group.add_argument(
        "--no-adaptive",
        action="store_true",
        help="Disable adaptive radius search - use fixed radius only",
    )

    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--version", "-v", action="version", version="%(prog)s 0.1.0"
    )
    output_group.add_argument(
        "--quiet", "-q", action="store_true", help="Reduce output verbosity"
    )

    return parser


def validate_coordinates(lat: Optional[float], lon: Optional[float]) -> bool:
    """Validate latitude and longitude coordinates"""
    if lat is not None and lon is not None:
        if not (-90 <= lat <= 90):
            print(f"❌ Invalid latitude: {lat}. Must be between -90 and 90.")
            return False
        if not (-180 <= lon <= 180):
            print(f"❌ Invalid longitude: {lon}. Must be between -180 and 180.")
            return False
        return True
    elif lat is not None or lon is not None:
        print("❌ Both latitude and longitude must be provided together.")
        return False
    return True


def get_location(args, config: TrackerConfig) -> tuple[float, float, str]:
    """Get location coordinates based on arguments"""
    if args.lat is not None and args.lon is not None:
        location_name = "Manual Coordinates"
        if not args.quiet:
            print(f"📍 Using manual coordinates: {args.lat:.4f}°, {args.lon:.4f}°")
        return args.lat, args.lon, location_name
    else:
        if not args.quiet:
            print("🌍 Detecting your current location...")
        temp_tracker = AircraftTracker(0, 0, fetch_online_codes=False, config=config)
        return temp_tracker.get_current_location()


def adaptive_search(
    lat: float, lon: float, location_name: str, args, config: TrackerConfig
) -> tuple[AircraftTracker, list]:
    """Perform adaptive radius search to find aircraft"""
    initial_radius = args.radius
    max_radius = getattr(args, "max_radius", 200)  # Default max radius
    radius_step = 25  # Increase by 25km each time

    if getattr(args, "no_adaptive", False):
        # Use fixed radius only
        if not args.quiet:
            print(f"🔍 Using fixed radius: {initial_radius} km")

        tracker = AircraftTracker(
            lat,
            lon,
            initial_radius,
            fetch_online_codes=not getattr(args, "no_online_db", False),
            config=config,
        )
        tracker.location_name = location_name
        aircraft_data = tracker.fetch_aircraft_data()
        return tracker, aircraft_data

    if not args.quiet:
        print(f"🔍 Starting adaptive search from {initial_radius} km...")
        print("📡 Will automatically expand radius to find aircraft...")
        print("=" * 60)

    # Initialize tracker once with online database loading
    if not args.quiet:
        print("🌐 Initializing enhanced airline database...")

    tracker = AircraftTracker(
        lat,
        lon,
        initial_radius,
        fetch_online_codes=not getattr(args, "no_online_db", False),
        config=config,
    )
    tracker.location_name = location_name

    if not args.quiet:
        print("📊 Enhanced database ready!")

    aircraft_data = []
    optimal_radius = initial_radius

    for radius in range(int(initial_radius), int(max_radius) + 1, radius_step):
        if not args.quiet:
            print(f"🔍 Searching within {radius} km radius...")

        new_tracker = AircraftTracker(
            lat, lon, radius, fetch_online_codes=False, config=config
        )
        new_tracker.location_name = location_name
        # Copy the enhanced database from our initialized tracker
        new_tracker.airline_codes = tracker.airline_codes.copy()
        aircraft_data = new_tracker.fetch_aircraft_data()

        if aircraft_data:
            tracker = new_tracker  # Use the successful tracker
            optimal_radius = radius
            if not args.quiet:
                print(f"✅ Found {len(aircraft_data)} aircraft within {radius} km!")
            break
        else:
            if not args.quiet:
                print(f"❌ No aircraft found within {radius} km")
            # Add a longer delay to avoid hitting API rate limits too frequently
            if radius < max_radius:
                if not args.quiet:
                    print("⏳ Waiting 30 seconds before expanding search radius...")
                time.sleep(30)

    if not aircraft_data:
        if not args.quiet:
            print(f"⚠️  No aircraft found even within {max_radius} km.")
            print("🔄 This could be due to:")
            print("   • API rate limiting (429 errors)")
            print("   • Low air traffic in your area")
            print("   • Temporary API issues")
            print("")
            print("💡 Suggestions:")
            print("   • Wait a few minutes and try again")
            print("   • Check if you're near a major airport or flight path")
            print("   • Try running during peak travel hours")
            print("")
            print(
                f"🌐 Will monitor with maximum radius ({max_radius} km) - aircraft may appear later."
            )

        optimal_radius = max_radius
        tracker = AircraftTracker(
            lat, lon, max_radius, fetch_online_codes=False, config=config
        )
        tracker.location_name = location_name

    if not args.quiet:
        print("=" * 60)
        print(f"🎯 Using optimal radius: {optimal_radius} km")

    return tracker, aircraft_data


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    # Handle create-config option
    if args.create_config:
        create_example_config()
        sys.exit(0)

    # Load configuration
    config = load_config_from_file(args.config)

    # Use config defaults for unspecified arguments
    if args.radius is None:
        args.radius = config.location.default_radius_km
    if args.interval is None:
        args.interval = config.display.default_update_interval

    # Validate coordinates if provided
    if not validate_coordinates(args.lat, args.lon):
        sys.exit(1)

    try:
        if not args.quiet:
            print("🛩️  Aircraft Tracker - Airport Departure Board Style Display")
            print("=" * 60)

        # Get location
        latitude, longitude, location_name = get_location(args, config)

        # Provide usage tip
        if not args.quiet and args.lat is None:
            print("💡 Tip: You can manually set coordinates by running:")
            print(f"   flight-display --lat <latitude> --lon <longitude>")
            print("=" * 60)

        # Perform adaptive search or use fixed radius
        tracker, aircraft_data = adaptive_search(
            latitude, longitude, location_name, args, config
        )

        # Start the display
        if not args.quiet:
            print(f"🎯 Starting display with {args.interval}s update interval...")
            print("Press Ctrl+C to stop")
            print()

        tracker.run_display(update_interval=args.interval)

    except KeyboardInterrupt:
        if not args.quiet:
            print("\n👋 Stopping Aircraft Tracker...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
