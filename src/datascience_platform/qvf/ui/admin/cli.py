#!/usr/bin/env python3
"""QVF Admin Interface CLI

Command-line interface for generating and managing QVF admin dashboards.
Provides easy access to dashboard generation, server management, and configuration.

Usage:
    python -m datascience_platform.qvf.ui.admin.cli generate
    python -m datascience_platform.qvf.ui.admin.cli serve
    python -m datascience_platform.qvf.ui.admin.cli --help
"""

import argparse
import sys
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional
import json
import logging

from .dashboard_integration import QVFAdminDashboardGenerator, QVFAdminConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_dashboard(args):
    """Generate QVF admin dashboard."""
    logger.info("Generating QVF admin dashboard...")
    
    try:
        config = QVFAdminConfig(
            title=args.title,
            description=args.description,
            output_dir=Path(args.output),
            theme=args.theme,
            enable_dark_mode=args.dark_mode,
            api_base_url=args.api_url,
            responsive=True,
            accessibility=True
        )
        
        generator = QVFAdminDashboardGenerator(config)
        output_path = generator.generate_admin_dashboard()
        
        logger.info(f"✅ Dashboard generated successfully at: {output_path}")
        logger.info(f"📁 To start development server, run:")
        logger.info(f"   cd {output_path}")
        logger.info(f"   npm install")
        logger.info(f"   npm run dev")
        
        if args.auto_install:
            install_dependencies(output_path)
        
        if args.auto_open:
            start_dev_server_and_open(output_path)
            
    except Exception as e:
        logger.error(f"❌ Dashboard generation failed: {e}")
        sys.exit(1)


def install_dependencies(dashboard_path: Path):
    """Install npm dependencies."""
    logger.info("Installing npm dependencies...")
    
    try:
        result = subprocess.run(
            ["npm", "install"],
            cwd=dashboard_path,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install dependencies: {e}")
        logger.error(f"Output: {e.stdout}")
        logger.error(f"Error: {e.stderr}")


def start_dev_server_and_open(dashboard_path: Path):
    """Start development server and open browser."""
    logger.info("Starting development server...")
    
    try:
        # Start the Next.js dev server in background
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=dashboard_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        logger.info("🚀 Development server starting...")
        logger.info("   Server will be available at: http://localhost:3000")
        logger.info("   Press Ctrl+C to stop the server")
        
        # Wait a moment then open browser
        import time
        time.sleep(3)
        webbrowser.open("http://localhost:3000")
        
        # Monitor the process
        try:
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    print(line.strip())
        except KeyboardInterrupt:
            logger.info("Shutting down development server...")
            process.terminate()
            process.wait()
            
    except FileNotFoundError:
        logger.error("❌ npm not found. Please install Node.js and npm first.")
    except Exception as e:
        logger.error(f"❌ Failed to start development server: {e}")


def serve_api(args):
    """Start the FastAPI server."""
    logger.info("Starting QVF Admin API server...")
    
    try:
        from ..api.main import run_development_server
        run_development_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload
        )
    except ImportError as e:
        logger.error(f"❌ Failed to import API server: {e}")
        logger.error("Make sure FastAPI and uvicorn are installed:")
        logger.error("pip install fastapi uvicorn")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed to start API server: {e}")
        sys.exit(1)


def create_config_template(args):
    """Create configuration template."""
    config_template = {
        "title": "My QVF Admin Dashboard",
        "description": "Custom QVF configuration management",
        "theme": "light",
        "enable_dark_mode": True,
        "api_base_url": "/api/v1/qvf",
        "features": {
            "weight_editor": True,
            "configuration_manager": True,
            "validation_summary": True,
            "export_import": True
        },
        "customization": {
            "primary_color": "#3B82F6",
            "logo_url": "/logo.png",
            "company_name": "Your Company"
        }
    }
    
    config_path = Path(args.output) / "qvf-admin-config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config_template, f, indent=2)
    
    logger.info(f"✅ Configuration template created at: {config_path}")
    logger.info("📝 Edit this file and use --config to apply custom settings")


def validate_installation():
    """Validate that all required dependencies are available."""
    logger.info("Validating installation...")
    
    # Check Python dependencies
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Missing Python packages: {', '.join(missing_packages)}")
        logger.error("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        node_version = result.stdout.strip()
        logger.info(f"✅ Node.js: {node_version}")
    except FileNotFoundError:
        logger.warning("⚠️  Node.js not found. Install from https://nodejs.org")
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        npm_version = result.stdout.strip()
        logger.info(f"✅ npm: {npm_version}")
    except FileNotFoundError:
        logger.warning("⚠️  npm not found. Usually comes with Node.js")
        return False
    
    logger.info("✅ Installation validation passed")
    return True


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="QVF Admin Interface CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate dashboard with defaults
  python -m datascience_platform.qvf.ui.admin.cli generate
  
  # Generate with custom settings
  python -m datascience_platform.qvf.ui.admin.cli generate --title "My QVF Admin" --output ./my-dashboard
  
  # Generate and auto-start
  python -m datascience_platform.qvf.ui.admin.cli generate --auto-install --auto-open
  
  # Start API server
  python -m datascience_platform.qvf.ui.admin.cli serve --port 8080
  
  # Validate installation
  python -m datascience_platform.qvf.ui.admin.cli validate
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate QVF admin dashboard')
    generate_parser.add_argument('--title', default='QVF Administration Dashboard',
                                help='Dashboard title')
    generate_parser.add_argument('--description', 
                                default='Quantified Value Framework Configuration Management',
                                help='Dashboard description')
    generate_parser.add_argument('--output', default='./qvf_admin_dashboard',
                                help='Output directory')
    generate_parser.add_argument('--theme', choices=['light', 'dark'], default='light',
                                help='Default theme')
    generate_parser.add_argument('--dark-mode', action='store_true',
                                help='Enable dark mode support')
    generate_parser.add_argument('--api-url', default='/api/v1/qvf',
                                help='API base URL')
    generate_parser.add_argument('--auto-install', action='store_true',
                                help='Automatically install npm dependencies')
    generate_parser.add_argument('--auto-open', action='store_true',
                                help='Automatically start dev server and open browser')
    generate_parser.add_argument('--config', type=Path,
                                help='JSON configuration file')
    generate_parser.set_defaults(func=generate_dashboard)
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start QVF API server')
    serve_parser.add_argument('--host', default='127.0.0.1', help='Server host')
    serve_parser.add_argument('--port', type=int, default=8000, help='Server port')
    serve_parser.add_argument('--no-reload', action='store_true',
                             help='Disable auto-reload')
    serve_parser.set_defaults(func=serve_api)
    
    # Config template command
    config_parser = subparsers.add_parser('config-template', 
                                         help='Create configuration template')
    config_parser.add_argument('--output', default='.', help='Output directory')
    config_parser.set_defaults(func=create_config_template)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate installation')
    validate_parser.set_defaults(func=lambda args: validate_installation())
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Special handling for validate command
    if args.command == 'validate':
        if not validate_installation():
            sys.exit(1)
        return
    
    # Execute command
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()