#!/usr/bin/env python3
"""
API Server Module for om - Start and manage the om API server
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def get_api_dir():
    """Get API directory"""
    return Path(__file__).parent.parent / "api"

def check_api_dependencies():
    """Check if API dependencies are installed"""
    try:
        import flask
        import flask_cors
        import jwt
        return True
    except ImportError:
        return False

def install_api_dependencies():
    """Install API dependencies"""
    api_dir = get_api_dir()
    requirements_file = api_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ API requirements file not found")
        return False
    
    print("📦 Installing API dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        print("✅ API dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install API dependencies")
        return False

def start_api_server(host='localhost', port=5000, debug=False, background=False):
    """Start the om API server"""
    api_dir = get_api_dir()
    server_script = api_dir / "server.py"
    
    if not server_script.exists():
        print("❌ API server script not found")
        return False
    
    # Check dependencies
    if not check_api_dependencies():
        print("⚠️  API dependencies not found")
        install = input("Install API dependencies? (y/N): ").strip().lower()
        if install == 'y':
            if not install_api_dependencies():
                return False
        else:
            print("Cannot start API server without dependencies")
            return False
    
    # Prepare command
    cmd = [
        sys.executable, str(server_script),
        "--host", host,
        "--port", str(port)
    ]
    
    if debug:
        cmd.append("--debug")
    
    print(f"🚀 Starting om API server on {host}:{port}")
    print(f"📖 API documentation: http://{host}:{port}/health")
    
    try:
        if background:
            # Start in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=api_dir
            )
            
            # Wait a moment to check if it started successfully
            time.sleep(2)
            if process.poll() is None:
                print(f"✅ API server started in background (PID: {process.pid})")
                
                # Save PID for later management
                pid_file = api_dir / "server.pid"
                with open(pid_file, 'w') as f:
                    f.write(str(process.pid))
                
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ API server failed to start:")
                if stderr:
                    print(stderr.decode())
                return False
        else:
            # Start in foreground
            subprocess.run(cmd, cwd=api_dir)
            return True
            
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
        return True
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return False

def stop_api_server():
    """Stop the om API server"""
    api_dir = get_api_dir()
    pid_file = api_dir / "server.pid"
    
    if not pid_file.exists():
        print("❌ No running API server found")
        return False
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # Try to terminate the process
        os.kill(pid, signal.SIGTERM)
        
        # Wait for process to terminate
        time.sleep(2)
        
        # Check if process is still running
        try:
            os.kill(pid, 0)  # Check if process exists
            # If we get here, process is still running, force kill
            os.kill(pid, signal.SIGKILL)
            print("🔥 API server force stopped")
        except OSError:
            # Process is gone
            print("✅ API server stopped successfully")
        
        # Remove PID file
        pid_file.unlink()
        return True
        
    except (ValueError, OSError) as e:
        print(f"❌ Failed to stop API server: {e}")
        # Clean up PID file anyway
        if pid_file.exists():
            pid_file.unlink()
        return False

def get_api_status():
    """Get API server status"""
    api_dir = get_api_dir()
    pid_file = api_dir / "server.pid"
    
    if not pid_file.exists():
        return {
            "running": False,
            "message": "API server is not running"
        }
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process is running
        try:
            os.kill(pid, 0)
            return {
                "running": True,
                "pid": pid,
                "message": f"API server is running (PID: {pid})"
            }
        except OSError:
            # Process is not running, clean up PID file
            pid_file.unlink()
            return {
                "running": False,
                "message": "API server is not running (stale PID file removed)"
            }
            
    except (ValueError, FileNotFoundError):
        return {
            "running": False,
            "message": "API server status unknown"
        }

def show_api_info():
    """Show API server information"""
    print("🚀 om API Server Information")
    print("=" * 40)
    
    # Check status
    status = get_api_status()
    print(f"Status: {status['message']}")
    
    # Check dependencies
    deps_installed = check_api_dependencies()
    print(f"Dependencies: {'✅ Installed' if deps_installed else '❌ Missing'}")
    
    # Show API directory
    api_dir = get_api_dir()
    print(f"API Directory: {api_dir}")
    
    # Show available endpoints
    if status["running"]:
        print("\n📖 Available Endpoints:")
        print("   http://localhost:5000/health")
        print("   http://localhost:5000/api/info")
        print("   http://localhost:5000/api/mood")
        print("   http://localhost:5000/api/checkin")
        print("   http://localhost:5000/api/dashboard")
        print("   http://localhost:5000/api/backup")
    
    # Show client libraries
    print("\n📚 Client Libraries:")
    print(f"   Python: {api_dir / 'client.py'}")
    print(f"   JavaScript: {api_dir / 'client.js'}")
    print(f"   Web Dashboard: {api_dir / 'web_dashboard.html'}")

def api_server_command(action="menu", *args):
    """API server command handler"""
    if action == "menu" or not action:
        show_api_menu()
    elif action == "start":
        host = args[0] if len(args) > 0 else "localhost"
        port = int(args[1]) if len(args) > 1 else 5000
        debug = "--debug" in args
        background = "--background" in args
        start_api_server(host, port, debug, background)
    elif action == "stop":
        stop_api_server()
    elif action == "status":
        status = get_api_status()
        print(status["message"])
    elif action == "info":
        show_api_info()
    elif action == "install":
        install_api_dependencies()
    elif action == "web":
        open_web_dashboard()
    else:
        show_api_menu()

def show_api_menu():
    """Show API server menu"""
    print("🚀 om API Server")
    print("=" * 25)
    print("1. Start API server")
    print("2. Stop API server")
    print("3. Server status")
    print("4. Server info")
    print("5. Install dependencies")
    print("6. Open web dashboard")
    
    try:
        choice = input("\nChoose an option (1-6): ").strip()
        
        if choice == "1":
            host = input("Host (localhost): ").strip() or "localhost"
            port = input("Port (5000): ").strip() or "5000"
            debug = input("Debug mode? (y/N): ").strip().lower() == 'y'
            background = input("Run in background? (y/N): ").strip().lower() == 'y'
            
            try:
                port = int(port)
                start_api_server(host, port, debug, background)
            except ValueError:
                print("❌ Invalid port number")
        elif choice == "2":
            stop_api_server()
        elif choice == "3":
            status = get_api_status()
            print(status["message"])
        elif choice == "4":
            show_api_info()
        elif choice == "5":
            install_api_dependencies()
        elif choice == "6":
            open_web_dashboard()
        else:
            print("Invalid choice")
    except KeyboardInterrupt:
        print("\n👋 Take care!")

def open_web_dashboard():
    """Open web dashboard in browser"""
    api_dir = get_api_dir()
    dashboard_file = api_dir / "web_dashboard.html"
    
    if not dashboard_file.exists():
        print("❌ Web dashboard file not found")
        return
    
    # Check if API server is running
    status = get_api_status()
    if not status["running"]:
        print("⚠️  API server is not running")
        start_server = input("Start API server? (y/N): ").strip().lower()
        if start_server == 'y':
            if start_api_server(background=True):
                time.sleep(2)  # Give server time to start
            else:
                return
        else:
            print("Web dashboard requires API server to be running")
            return
    
    # Try to open in browser
    try:
        import webbrowser
        file_url = f"file://{dashboard_file.absolute()}"
        webbrowser.open(file_url)
        print(f"🌐 Web dashboard opened: {file_url}")
        print("💡 Enter your API key to connect to the server")
    except Exception as e:
        print(f"❌ Failed to open web dashboard: {e}")
        print(f"📁 Manually open: {dashboard_file}")

if __name__ == "__main__":
    import sys
    args = sys.argv[1:] if len(sys.argv) > 1 else ["menu"]
    api_server_command(*args)
