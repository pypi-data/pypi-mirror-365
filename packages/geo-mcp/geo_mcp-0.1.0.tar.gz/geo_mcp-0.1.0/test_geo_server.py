#!/usr/bin/env python3
"""
Simple test server for GEO functionality without MCP dependencies
Tests the core GEO search and download functionality
"""

import json
import sys
import os
from pathlib import Path

# Add the geomcp module to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from geomcp import geo_profiles, geo_downloader
    print("✓ Successfully imported GEO modules")
except ImportError as e:
    print(f"✗ Failed to import GEO modules: {e}")
    sys.exit(1)

def test_geo_search():
    """Test GEO search functionality"""
    print("\n=== Testing GEO Search Functionality ===")
    
    try:
        # Test universal search
        print("Testing universal search...")
        result = geo_profiles.search_geo("cancer", 3)
        print(f"✓ Universal search: Found {result['total_count']} results")
        
        # Test specific searches
        print("Testing specific searches...")
        
        series = geo_profiles.search_geo_series("cancer", 2)
        print(f"✓ Series search: Found {len(series.get('result', {}).get('uids', []))} results")
        
        datasets = geo_profiles.search_geo_datasets("cancer", 2)
        print(f"✓ Datasets search: Found {len(datasets.get('result', {}).get('uids', []))} results")
        
        profiles = geo_profiles.search_geo_profiles("TP53", 2)
        print(f"✓ Profiles search: Found results")
        
        return True
        
    except Exception as e:
        print(f"✗ Search test failed: {e}")
        return False

def test_geo_downloader():
    """Test GEO downloader functionality"""
    print("\n=== Testing GEO Downloader Functionality ===")
    
    try:
        # Test download status check
        print("Testing download status...")
        status = geo_downloader.get_download_status("GSE12345", "gse")
        print(f"✓ Download status check: {status['downloaded']}")
        
        # Test listing downloads
        print("Testing list downloads...")
        downloads = geo_downloader.list_downloaded_datasets()
        print(f"✓ List downloads: Found {downloads['count']} datasets")
        
        # Test download stats
        print("Testing download stats...")
        stats = geo_downloader.get_download_stats()
        print(f"✓ Download stats: {stats.get('download_dir', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Downloader test failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n=== Testing Configuration ===")
    
    try:
        from geomcp.geo_profiles import _get_config
        config = _get_config()
        print(f"✓ Config loaded successfully")
        print(f"  Base URL: {config.get('base_url', 'N/A')}")
        print(f"  Email: {config.get('email', 'Not configured')}")
        print(f"  API Key: {'Yes' if config.get('api_key') else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("GEO MCP Server Debug Test")
    print("=" * 50)
    
    # Test configuration first
    config_ok = test_config()
    
    # Test search functionality
    search_ok = test_geo_search()
    
    # Test downloader functionality  
    download_ok = test_geo_downloader()
    
    print("\n=== Test Summary ===")
    print(f"Configuration: {'✓ PASS' if config_ok else '✗ FAIL'}")
    print(f"Search functionality: {'✓ PASS' if search_ok else '✗ FAIL'}")
    print(f"Download functionality: {'✓ PASS' if download_ok else '✗ FAIL'}")
    
    if all([config_ok, search_ok, download_ok]):
        print("\n🎉 All core GEO functionality is working!")
        print("\nNext steps:")
        print("1. Upgrade to Python 3.10+ to use full MCP functionality")
        print("2. Install MCP package: pip install mcp")
        print("3. Run: python -m geomcp.main --init")
        print("4. Run: python -m geomcp.main")
        return 0
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())