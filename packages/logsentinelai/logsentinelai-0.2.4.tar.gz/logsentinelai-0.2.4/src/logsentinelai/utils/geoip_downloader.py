#!/usr/bin/env python3
"""
GeoIP Database Download Helper Script

This script downloads the MaxMind GeoLite2-Country database required for
GeoIP enrichment functionality in LogSentinelAI.

Requirements:
- Internet connection
- requests library (included in requirements.txt)

Usage:
    python download_geoip_database.py [--output-dir /path/to/directory]
"""

import os
import sys
import argparse
import gzip
import shutil
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ ERROR: requests library not found")
    print("💡 Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)


def download_geoip_database(output_dir: str = None) -> bool:
    """
    Download MaxMind GeoLite2-City database (includes country, city, and coordinates)
    
    Args:
        output_dir: Directory to save the database file (default: ~/.logsentinelai)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if output_dir is None:
        output_dir = os.path.expanduser('~/.logsentinelai')
    
    # MaxMind GeoLite2-City database URLs (includes all country + city + coordinates data)
    database_urls = [
        "https://git.io/GeoLite2-City.mmdb",  # Redirects to latest release
        "https://github.com/P3TERX/GeoLite.mmdb/releases/latest/download/GeoLite2-City.mmdb",
        "https://github.com/alecthw/mmdb_china_ip_list/releases/latest/download/GeoLite2-City.mmdb"
    ]
    filename = "GeoLite2-City.mmdb"
    db_name = "City"
    
    output_path = Path(output_dir)
    final_file = output_path / filename
    
    print("=" * 60)
    print(f"GeoIP {db_name} Database Download")
    print("=" * 60)
    print(f"Output: {final_file}")
    print("Note: City database provides country, city, latitude, and longitude")
    print("-" * 60)
    
    try:
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Check if database already exists
        if final_file.exists():
            response = input(f"Database already exists at {final_file}. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("❌ Download cancelled")
                return False
        
        # Try different sources
        for i, database_url in enumerate(database_urls, 1):
            print(f"📡 Trying source {i}/{len(database_urls)}: {database_url}")
            
            try:
                # Determine if this is a compressed file
                is_compressed = database_url.endswith('.gz')
                temp_file = output_path / ("temp_download.mmdb.gz" if is_compressed else "temp_download.mmdb")
                
                # Download database
                response = requests.get(database_url, stream=True, timeout=30)
                response.raise_for_status()
                
                # Get file size for progress indication
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                
                # Download with progress indication
                with open(temp_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            if total_size > 0:
                                progress = (downloaded_size / total_size) * 100
                                print(f"\r📥 Progress: {progress:.1f}% ({downloaded_size:,} / {total_size:,} bytes)", end='')
                
                print(f"\n✅ Download completed from source {i}")
                
                # Handle compressed vs uncompressed files
                if is_compressed:
                    print("📦 Extracting compressed database...")
                    with gzip.open(temp_file, 'rb') as f_in:
                        with open(final_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    temp_file.unlink()  # Remove compressed file
                else:
                    # Rename uncompressed file
                    temp_file.rename(final_file)
                
                break  # Success, exit the loop
                
            except requests.RequestException as e:
                print(f"\n❌ Source {i} failed: {e}")
                if temp_file.exists():
                    temp_file.unlink()
                if i == len(database_urls):
                    # Last attempt failed
                    print("\n❌ All download sources failed")
                    return False
                print(f"🔄 Trying next source...")
                continue
        
        # Verify final database file
        if not final_file.exists():
            print("❌ Database file was not created successfully")
            return False
            
        file_size = final_file.stat().st_size
        if file_size < 1000:  # Sanity check - database should be larger than 1KB
            print(f"❌ Downloaded file seems too small ({file_size} bytes)")
            final_file.unlink()
            return False
        print(f"📊 Database size: {file_size:,} bytes ({file_size / 1024 / 1024:.1f} MB)")
        
        print("=" * 60)
        print("✅ GeoIP database download completed successfully!")
        print("=" * 60)
        print(f"Database location: {final_file.absolute()}")
        print("💡 Make sure GEOIP_DATABASE_PATH in config points to this file")
        print("💡 Example config setting:")
        print(f"   GEOIP_DATABASE_PATH={final_file.absolute()}")
        print("=" * 60)
        
        return True
        
    except requests.RequestException as e:
        print(f"\n❌ Download failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Download MaxMind GeoLite2-City database for LogSentinelAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_geoip_database.py                     # Download to default location
  python download_geoip_database.py --output-dir /etc/geoip

Database Type:
  GeoLite2-City: Provides comprehensive location data including:
  - Country information (code, name)
  - City information 
  - Latitude and longitude coordinates
  
  This is superior to the Country-only database as it includes all country
  data plus enhanced location details for geospatial analysis.

Note:
  The GeoLite2-City database is provided by MaxMind under Creative Commons
  Attribution-ShareAlike 4.0 International License. For production use,
  consider registering for a MaxMind account to get the most recent data.
        """
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=os.path.expanduser('~/.logsentinelai'),
        help='Directory to save the database file (default: ~/.logsentinelai)'
    )
    
    args = parser.parse_args()
    
    # Download database
    success = download_geoip_database(args.output_dir)
    
    if success:
        sys.exit(0)
    else:
        print("\n❌ Database download failed")
        print("💡 You can also manually download from:")
        print("   https://dev.maxmind.com/geoip/geolite2-free-geolocation-data")
        sys.exit(1)


if __name__ == "__main__":
    main()
