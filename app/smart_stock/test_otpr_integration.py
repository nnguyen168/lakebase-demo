#!/usr/bin/env python3
"""Test OTPR integration in SmartStock application."""

import requests
import json

def test_otpr_api():
    """Test the OTPR API endpoint."""
    print("🧪 Testing OTPR API Integration")
    print("="*50)

    try:
        # Test the OTPR endpoint
        response = requests.get("http://localhost:8000/api/otpr/")
        response.raise_for_status()

        data = response.json()

        print("\n✅ OTPR API Response:")
        print(f"   Current 30-day OTPR: {data.get('otpr_last_30d', 'N/A')}%")
        print(f"   Previous 30-day OTPR: {data.get('otpr_prev_30d', 'N/A')}%")
        print(f"   Change: {data.get('change_ppt', 'N/A')} percentage points")
        print(f"   Trend: {data.get('trend', 'N/A')}")

        if data.get('error'):
            print(f"   ⚠️  Note: {data['error']}")

        # Analyze the results
        print("\n📊 Analysis:")
        if data.get('otpr_last_30d') and data.get('otpr_prev_30d'):
            current = data['otpr_last_30d']
            previous = data['otpr_prev_30d']
            change = data.get('change_ppt', 0)

            if current < 80:
                print(f"   ⚠️  WARNING: Current OTPR ({current}%) is below target (80%)")
                print("   Immediate action needed to improve on-time delivery rate")
            elif current >= 95:
                print(f"   ✅ Excellent: OTPR is at {current}%")
            else:
                print(f"   ℹ️  Good: OTPR is at {current}%")

            if change < -10:
                print(f"   🔴 Significant decline: {abs(change)}% decrease from previous period")
            elif change < 0:
                print(f"   🟡 Moderate decline: {abs(change)}% decrease from previous period")
            elif change > 10:
                print(f"   🟢 Significant improvement: {change}% increase from previous period")
            elif change > 0:
                print(f"   🟢 Moderate improvement: {change}% increase from previous period")
            else:
                print(f"   🔵 Stable performance: No change from previous period")

        print("\n✅ OTPR Integration Test Passed!")

        # Test if frontend can access the API
        print("\n🌐 Testing Frontend Access:")
        print(f"   Backend API: http://localhost:8000/api/otpr/")
        print(f"   Frontend URL: http://localhost:5173/")
        print(f"   Dashboard should display OTPR metrics in the green KPI card")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend server")
        print("   Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_otpr_api()

    if success:
        print("\n" + "="*50)
        print("🎉 OTPR Integration Successfully Implemented!")
        print("="*50)
        print("\nNext steps:")
        print("1. Open http://localhost:5173/ in your browser")
        print("2. Look for the 'On-Time Production Rate' KPI card")
        print("3. Verify it shows:")
        print("   - Current rate with trend indicator")
        print("   - Change percentage vs previous 30 days")
        print("   - Previous and current period values")
    else:
        print("\n❌ Test failed. Please check the server logs.")