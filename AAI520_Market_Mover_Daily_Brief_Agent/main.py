"""
Main Entry Point for Market Movers Dashboard
Run this file to start the dashboard application
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the dashboard
from data_visualization.simple_dashboard import app, socketio

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Market Movers Dashboard...")
    print("=" * 60)
    print("\nDashboard will be available at:")
    print("  http://localhost:5000")
    print("  http://127.0.0.1:5000")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 60)
    
    # Run the dashboard
    socketio.run(app, 
                host='0.0.0.0', 
                port=5000, 
                debug=True, 
                use_reloader=False,
                allow_unsafe_werkzeug=True)
