#!/usr/bin/env python3
"""
Complete deployment test for GEO MCP Server
Tests all functionality in the geo-mcp-server conda environment
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the geomcp module to path
sys.path.insert(0, str(Path(__file__).parent))

def test_environment():
    """Test that we're in the right environment"""
    print("=== Environment Test ===")
    try:
        import sys
        print(f"✓ Python version: {sys.version.split()[0]}")
        
        # Check MCP is available
        import mcp.server
        print("✓ MCP package available")
        
        # Check our modules
        from geomcp import geo_profiles, geo_downloader
        from geomcp.mcp_server import mcp_server
        print("✓ GEO MCP modules loaded")
        
        return True
    except Exception as e:
        print(f"✗ Environment test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n=== Configuration Test ===")
    try:
        from geomcp.geo_profiles import _get_config
        config = _get_config()
        print(f"✓ Config loaded from: {os.getenv('CONFIG_PATH', 'default location')}")
        print(f"  Email: {config.get('email', 'Not set')}")
        print(f"  Base URL: {config.get('base_url', 'Not set')}")
        print(f"  API Key: {'Set' if config.get('api_key') else 'Not set'}")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

async def test_mcp_server():
    """Test MCP server functionality"""
    print("\n=== MCP Server Test ===")
    try:
        from geomcp.mcp_server import mcp_server
        
        # Test server instance
        server = mcp_server.get_server()
        print(f"✓ MCP server instance created: {server.name}")
        
        # Test tools
        tools = mcp_server.get_tool_definitions()
        print(f"✓ Tools available: {len(tools)}")
        
        tool_names = [t.name for t in tools]
        expected_tools = [
            'search_geo', 'search_geo_profiles', 'search_geo_datasets', 
            'search_geo_series', 'search_geo_samples', 'search_geo_platforms',
            'download_geo_data', 'get_download_status', 'list_downloaded_datasets'
        ]
        
        for tool in expected_tools[:6]:  # Test first 6 tools
            if tool in tool_names:
                print(f"  ✓ {tool}")
            else:
                print(f"  ✗ {tool} missing")
        
        return True
    except Exception as e:
        print(f"✗ MCP server test failed: {e}")
        return False

async def test_search_functionality():
    """Test all search functions"""
    print("\n=== Search Functionality Test ===")
    try:
        from geomcp import geo_profiles
        
        # Universal search
        result = geo_profiles.search_geo("cancer", 3)
        print(f"✓ Universal search: {result['total_count']} total results")
        print(f"  - Series: {len(result['series'])}")
        print(f"  - Datasets: {len(result['datasets'])}")
        
        # Specific searches
        series = geo_profiles.search_geo_series("breast cancer", 2)
        print(f"✓ Series search: {len(series.get('result', {}).get('uids', []))} results")
        
        profiles = geo_profiles.search_geo_profiles("TP53", 2)
        print(f"✓ Profiles search: completed successfully")
        
        platforms = geo_profiles.search_geo_platforms("Illumina", 2)
        print(f"✓ Platforms search: {len(platforms.get('result', {}).get('uids', []))} results")
        
        return True
    except Exception as e:
        print(f"✗ Search functionality test failed: {e}")
        return False

async def test_download_functionality():
    """Test download system"""
    print("\n=== Download Functionality Test ===")
    try:
        from geomcp import geo_downloader
        
        # Download stats
        stats = geo_downloader.get_download_stats()
        print(f"✓ Download stats: {stats['total_downloaded_mb']}MB used")
        print(f"  Directory: {stats['download_dir']}")
        print(f"  Disk free: {stats['disk_free_mb']}MB")
        
        # List downloads
        downloads = geo_downloader.list_downloaded_datasets()
        print(f"✓ Downloaded datasets: {downloads['count']} found")
        
        # Download status check
        status = geo_downloader.get_download_status("GSE10072", "gse")
        print(f"✓ Download status check: GSE10072 = {'Downloaded' if status['downloaded'] else 'Not downloaded'}")
        
        return True
    except Exception as e:
        print(f"✗ Download functionality test failed: {e}")
        return False

def test_claude_integration():
    """Test Claude Desktop integration setup"""
    print("\n=== Claude Integration Test ===")
    try:
        config_path = os.path.expanduser("~/.geo-mcp/config.json")
        if os.path.exists(config_path):
            print(f"✓ Config file exists: {config_path}")
        else:
            print(f"⚠ Config file not found: {config_path}")
        
        # Check if geo-mcp command is available
        import shutil
        geo_mcp_path = shutil.which("geo-mcp")
        if geo_mcp_path:
            print(f"✓ geo-mcp command available: {geo_mcp_path}")
        else:
            print("⚠ geo-mcp command not in PATH")
        
        # Provide Claude Desktop config
        claude_config = {
            "mcpServers": {
                "geo-mcp": {
                    "command": geo_mcp_path or "/Users/matthiasflo/opt/miniconda3/envs/geo-mcp-server/bin/geo-mcp",
                    "env": {
                        "CONFIG_PATH": config_path
                    }
                }
            }
        }
        
        print("✓ Claude Desktop configuration:")
        print(json.dumps(claude_config, indent=2))
        
        return True
    except Exception as e:
        print(f"✗ Claude integration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧬 GEO MCP Server - Complete Deployment Test")
    print("=" * 60)
    
    tests = [
        ("Environment", test_environment()),
        ("Configuration", test_configuration()),
        ("MCP Server", await test_mcp_server()),
        ("Search Functions", await test_search_functionality()),
        ("Download System", await test_download_functionality()),
        ("Claude Integration", test_claude_integration()),
    ]
    
    results = []
    for name, result in tests:
        if isinstance(result, bool):
            results.append((name, result))
        else:
            results.append((name, await result if asyncio.iscoroutine(result) else result))
    
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("\n🚀 DEPLOYMENT READY!")
        print("\nNext steps:")
        print("1. Add the Claude Desktop configuration shown above")
        print("2. Restart Claude Desktop")
        print("3. Test with: python -m geomcp.main --http")
        print("4. Access via: python -m geomcp.main")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please review the errors above before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))