"""QVF Admin Dashboard Integration

Integrates the QVF admin interface with the existing DataScience Platform
dashboard generation system. Creates complete TypeScript/React applications
with the QVF admin interface embedded.

This module extends the dashboard generator to include QVF-specific admin
interfaces while maintaining compatibility with the existing dashboard system.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

from ...dashboard.generative.generator import DashboardGenerator, DashboardConfig
from ...dashboard.generative.components import ComponentGenerator

logger = logging.getLogger(__name__)


@dataclass
class QVFAdminConfig:
    """Configuration for QVF admin dashboard generation."""
    title: str = "QVF Administration Dashboard"
    description: str = "Quantified Value Framework Configuration Management"
    output_dir: Path = Path("./qvf_admin_dashboard")
    theme: str = "light"
    enable_dark_mode: bool = True
    include_api_integration: bool = True
    api_base_url: str = "/api/v1/qvf"
    responsive: bool = True
    accessibility: bool = True


class QVFAdminDashboardGenerator:
    """Generates complete QVF admin dashboard applications.
    
    Extends the existing dashboard generator to create comprehensive
    QVF administration interfaces with full TypeScript/React support.
    """
    
    def __init__(self, config: Optional[QVFAdminConfig] = None):
        """Initialize QVF admin dashboard generator.
        
        Args:
            config: QVF admin configuration
        """
        self.config = config or QVFAdminConfig()
        
        # Initialize base dashboard generator
        dashboard_config = DashboardConfig(
            title=self.config.title,
            description=self.config.description,
            output_dir=self.config.output_dir,
            theme=self.config.theme,
            responsive=self.config.responsive
        )
        self.dashboard_generator = DashboardGenerator(dashboard_config)
        self.component_generator = ComponentGenerator(use_tremor=True)
        
        logger.info(f"QVF Admin Dashboard Generator initialized: {self.config.title}")
    
    def generate_admin_dashboard(self) -> Path:
        """Generate complete QVF admin dashboard application.
        
        Returns:
            Path to generated dashboard
        """
        try:
            logger.info("Starting QVF admin dashboard generation...")
            
            # Create output directory structure
            self._create_directory_structure()
            
            # Generate React components
            self._generate_admin_components()
            
            # Generate API integration
            if self.config.include_api_integration:
                self._generate_api_integration()
            
            # Generate supporting files
            self._generate_supporting_files()
            
            # Copy admin-specific assets
            self._copy_admin_assets()
            
            # Generate Next.js configuration
            self._generate_nextjs_config()
            
            logger.info(f"QVF admin dashboard generated at: {self.config.output_dir}")
            return self.config.output_dir
            
        except Exception as e:
            logger.error(f"Failed to generate QVF admin dashboard: {e}")
            raise
    
    def _create_directory_structure(self):
        """Create the complete directory structure."""
        directories = [
            "src/app",
            "src/components/admin",
            "src/components/ui", 
            "src/hooks",
            "src/types",
            "src/utils",
            "src/styles",
            "public",
            "data"
        ]
        
        for directory in directories:
            (self.config.output_dir / directory).mkdir(parents=True, exist_ok=True)
        
        logger.info("Created directory structure")
    
    def _generate_admin_components(self):
        """Generate all React admin components."""
        src_dir = self.config.output_dir / "src"
        
        # Copy TypeScript types
        self._write_types_file(src_dir / "types" / "qvf.ts")
        
        # Generate hook files
        self._write_hooks_file(src_dir / "hooks" / "useQVFApi.ts")
        
        # Generate main admin components
        components_dir = src_dir / "components" / "admin"
        self._write_admin_dashboard_component(components_dir / "AdminDashboard.tsx")
        self._write_weight_editor_component(components_dir / "WeightEditor.tsx") 
        self._write_config_manager_component(components_dir / "ConfigurationManager.tsx")
        
        # Generate utility components
        ui_dir = src_dir / "components" / "ui"
        self._write_ui_components(ui_dir)
        
        logger.info("Generated React admin components")
    
    def _generate_api_integration(self):
        """Generate API integration code."""
        src_dir = self.config.output_dir / "src"
        
        # Generate API client
        api_client = f'''/**
 * QVF API Client
 * 
 * Type-safe API client for QVF administration endpoints.
 */

const API_BASE = '{self.config.api_base_url}';

export class QVFApiClient {{
  private baseUrl: string;
  
  constructor(baseUrl: string = API_BASE) {{
    this.baseUrl = baseUrl;
  }}
  
  async get<T>(endpoint: string): Promise<T> {{
    const response = await fetch(`${{this.baseUrl}}${{endpoint}}`);
    if (!response.ok) {{
      throw new Error(`API call failed: ${{response.statusText}}`);
    }}
    return response.json();
  }}
  
  async post<T>(endpoint: string, data: any): Promise<T> {{
    const response = await fetch(`${{this.baseUrl}}${{endpoint}}`, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(data),
    }});
    if (!response.ok) {{
      throw new Error(`API call failed: ${{response.statusText}}`);
    }}
    return response.json();
  }}
  
  async put<T>(endpoint: string, data: any): Promise<T> {{
    const response = await fetch(`${{this.baseUrl}}${{endpoint}}`, {{
      method: 'PUT',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(data),
    }});
    if (!response.ok) {{
      throw new Error(`API call failed: ${{response.statusText}}`);
    }}
    return response.json();
  }}
  
  async delete(endpoint: string): Promise<void> {{
    const response = await fetch(`${{this.baseUrl}}${{endpoint}}`, {{
      method: 'DELETE',
    }});
    if (!response.ok) {{
      throw new Error(`API call failed: ${{response.statusText}}`);
    }}
  }}
}}

export const apiClient = new QVFApiClient();
'''
        
        with open(src_dir / "utils" / "api.ts", 'w') as f:
            f.write(api_client)
        
        logger.info("Generated API integration")
    
    def _generate_supporting_files(self):
        """Generate package.json, tsconfig.json, and other supporting files."""
        # Enhanced package.json with admin-specific dependencies
        package_json = {
            "name": "qvf-admin-dashboard",
            "version": "2.0.0",
            "private": True,
            "description": "QVF Administration Dashboard",
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint",
                "type-check": "tsc --noEmit",
                "format": "prettier --write ."
            },
            "dependencies": {
                "@tremor/react": "^3.11.1",
                "@heroicons/react": "^2.0.18",
                "next": "14.0.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "zustand": "^4.4.7",
                "recharts": "^2.10.0",
                "@hookform/resolvers": "^3.3.2",
                "react-hook-form": "^7.47.0",
                "date-fns": "^2.30.0"
            },
            "devDependencies": {
                "@types/node": "^20.8.0",
                "@types/react": "^18.2.25",
                "@types/react-dom": "^18.2.11",
                "autoprefixer": "^10.4.16",
                "postcss": "^8.4.31",
                "tailwindcss": "^3.3.5",
                "typescript": "^5.2.2",
                "eslint": "^8.51.0",
                "eslint-config-next": "14.0.0",
                "prettier": "^3.0.3"
            }
        }
        
        with open(self.config.output_dir / "package.json", 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Enhanced TypeScript configuration
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "lib": ["dom", "dom.iterable", "esnext"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [{"name": "next"}],
                "paths": {
                    "@/*": ["./src/*"],
                    "@/components/*": ["./src/components/*"],
                    "@/hooks/*": ["./src/hooks/*"],
                    "@/types/*": ["./src/types/*"],
                    "@/utils/*": ["./src/utils/*"]
                }
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }
        
        with open(self.config.output_dir / "tsconfig.json", 'w') as f:
            json.dump(tsconfig, f, indent=2)
        
        # Tailwind configuration with admin-specific styling
        tailwind_config = f'''import type {{ Config }} from 'tailwindcss'

const config: Config = {{
  content: [
    './src/**/*.{{js,ts,jsx,tsx,mdx}}',
    './node_modules/@tremor/**/*.{{js,ts,jsx,tsx}}',
  ],
  theme: {{
    extend: {{
      colors: {{
        qvf: {{
          primary: '#3B82F6',
          secondary: '#6B7280',
          success: '#10B981',
          warning: '#F59E0B',
          danger: '#EF4444',
        }},
      }},
      fontFamily: {{
        sans: ['Inter', 'sans-serif'],
      }},
      animation: {{
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'slide-in-up': 'slideInUp 0.2s ease-out',
      }},
    }},
  }},
  plugins: [],
  darkMode: '{{"class" if self.config.enable_dark_mode else "media"}}',
}}

export default config'''
        
        with open(self.config.output_dir / "tailwind.config.ts", 'w') as f:
            f.write(tailwind_config)
        
        logger.info("Generated supporting configuration files")
    
    def _generate_nextjs_config(self):
        """Generate Next.js application structure."""
        app_dir = self.config.output_dir / "src" / "app"
        
        # Main page component
        page_tsx = '''import { QVFAdminApp } from '@/components/admin/AdminDashboard';

export default function AdminPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <QVFAdminApp />
    </main>
  );
}'''
        
        with open(app_dir / "page.tsx", 'w') as f:
            f.write(page_tsx)
        
        # Layout component
        layout_tsx = f'''import type {{ Metadata }} from 'next'
import {{ Inter }} from 'next/font/google'
import '@/styles/globals.css'
import '@/styles/admin.css'

const inter = Inter({{ subsets: ['latin'] }})

export const metadata: Metadata = {{
  title: '{self.config.title}',
  description: '{self.config.description}',
}}

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode
}}) {{
  return (
    <html lang="en"{' className="dark"' if self.config.enable_dark_mode else ''}>
      <body className={{inter.className}}>{{children}}</body>
    </html>
  )
}}'''
        
        with open(app_dir / "layout.tsx", 'w') as f:
            f.write(layout_tsx)
        
        # Global CSS
        globals_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Focus visible for accessibility */
.focus-visible:focus {
  @apply outline-none ring-2 ring-blue-500 ring-offset-2;
}

/* Custom animations */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideInUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}'''
        
        styles_dir = self.config.output_dir / "src" / "styles"
        with open(styles_dir / "globals.css", 'w') as f:
            f.write(globals_css)
        
        logger.info("Generated Next.js application structure")
    
    def _copy_admin_assets(self):
        """Copy admin-specific CSS and assets."""
        # Copy the admin.css file we created earlier
        admin_css_source = Path(__file__).parent / "styles" / "admin.css"
        admin_css_dest = self.config.output_dir / "src" / "styles" / "admin.css"
        
        try:
            if admin_css_source.exists():
                shutil.copy2(admin_css_source, admin_css_dest)
            else:
                # Create basic admin.css if source doesn't exist
                basic_admin_css = """/* QVF Admin Interface Styles */
.qvf-admin-app {
  @apply min-h-screen bg-gray-50;
}

.weight-editor-container {
  @apply space-y-6;
}

.config-list-item {
  @apply border border-gray-200 rounded-lg p-4 hover:border-gray-300 hover:shadow-sm cursor-pointer transition-all;
}
"""
                with open(admin_css_dest, 'w') as f:
                    f.write(basic_admin_css)
                
        except Exception as e:
            logger.warning(f"Could not copy admin CSS: {e}")
        
        # Create placeholder favicon and other assets
        public_dir = self.config.output_dir / "public"
        
        # Create a basic README
        readme_content = f"""# {self.config.title}

This dashboard was automatically generated by the DataScience Platform QVF Admin Generator.

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Features

- **Configuration Management**: Create, edit, and delete QVF configurations
- **Weight Configuration**: Interactive sliders for category weight adjustment  
- **Real-time Validation**: Instant feedback on configuration validity
- **Export/Import**: Backup and share configurations
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Accessibility**: Full keyboard navigation and screen reader support

## API Integration

The dashboard integrates with the QVF API at `{self.config.api_base_url}`.

## Customization

Edit the components in `src/components/` to customize the interface.

Generated on: {self.config.title}
Version: 2.0.0
"""
        
        with open(self.config.output_dir / "README.md", 'w') as f:
            f.write(readme_content)
        
        logger.info("Copied admin assets and documentation")
    
    def _write_types_file(self, path: Path):
        """Write TypeScript types file."""
        # Copy the types from the existing admin interface
        types_source = Path(__file__).parent / "types.ts"
        
        try:
            if types_source.exists():
                shutil.copy2(types_source, path)
            else:
                # Create basic types if source doesn't exist
                basic_types = '''export interface QVFConfiguration {
  configuration_id: string;
  name: string;
  description?: string;
  // Add other fields as needed
}

export interface CriteriaWeights {
  business_value: number;
  strategic_alignment: number;
  customer_value: number;
  implementation_complexity: number;
  risk_assessment: number;
}'''
                with open(path, 'w') as f:
                    f.write(basic_types)
        except Exception as e:
            logger.warning(f"Could not copy types file: {e}")
    
    def _write_hooks_file(self, path: Path):
        """Write React hooks file."""
        # Copy the hooks from the existing admin interface
        hooks_source = Path(__file__).parent / "hooks" / "useQVFApi.ts"
        
        try:
            if hooks_source.exists():
                shutil.copy2(hooks_source, path)
            else:
                # Create basic hooks if source doesn't exist
                basic_hooks = '''import { useState, useEffect } from 'react';

export function useConfigurations() {
  const [configurations, setConfigurations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Basic implementation
  return { configurations, isLoading };
}'''
                with open(path, 'w') as f:
                    f.write(basic_hooks)
        except Exception as e:
            logger.warning(f"Could not copy hooks file: {e}")
    
    def _write_admin_dashboard_component(self, path: Path):
        """Write main admin dashboard component."""
        component_source = Path(__file__).parent / "components" / "AdminDashboard.tsx"
        
        try:
            if component_source.exists():
                shutil.copy2(component_source, path)
            else:
                # Create basic component if source doesn't exist
                basic_component = '''import React from 'react';

export const AdminDashboard: React.FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">QVF Admin Dashboard</h1>
      <p>Configuration management interface</p>
    </div>
  );
};

export const QVFAdminApp = AdminDashboard;'''
                with open(path, 'w') as f:
                    f.write(basic_component)
        except Exception as e:
            logger.warning(f"Could not copy admin dashboard component: {e}")
    
    def _write_weight_editor_component(self, path: Path):
        """Write weight editor component."""
        component_source = Path(__file__).parent / "components" / "WeightEditor.tsx"
        
        try:
            if component_source.exists():
                shutil.copy2(component_source, path)
        except Exception as e:
            logger.warning(f"Could not copy weight editor component: {e}")
    
    def _write_config_manager_component(self, path: Path):
        """Write configuration manager component."""
        component_source = Path(__file__).parent / "components" / "ConfigurationManager.tsx"
        
        try:
            if component_source.exists():
                shutil.copy2(component_source, path)
        except Exception as e:
            logger.warning(f"Could not copy configuration manager component: {e}")
    
    def _write_ui_components(self, ui_dir: Path):
        """Write reusable UI components."""
        # Create basic UI components
        loading_spinner = '''import React from 'react';

export const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ 
  size = 'md' 
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8', 
    lg: 'h-12 w-12'
  };
  
  return (
    <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-blue-600 ${sizeClasses[size]}`} />
  );
};'''
        
        with open(ui_dir / "LoadingSpinner.tsx", 'w') as f:
            f.write(loading_spinner)
        
        # Create toast notifications
        toast = '''import React from 'react';

interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ type, message, onClose }) => {
  const typeStyles = {
    success: 'bg-green-50 text-green-800 border-green-200',
    error: 'bg-red-50 text-red-800 border-red-200',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
    info: 'bg-blue-50 text-blue-800 border-blue-200'
  };
  
  return (
    <div className={`border rounded-lg p-4 ${typeStyles[type]}`}>
      <div className="flex justify-between items-center">
        <span>{message}</span>
        <button onClick={onClose} className="ml-4">×</button>
      </div>
    </div>
  );
};'''
        
        with open(ui_dir / "Toast.tsx", 'w') as f:
            f.write(toast)
        
        logger.info("Generated UI components")


# Factory function for easy dashboard generation
def generate_qvf_admin_dashboard(
    output_dir: str = "./qvf_admin_dashboard",
    title: str = "QVF Administration Dashboard",
    api_base_url: str = "/api/v1/qvf",
    theme: str = "light",
    enable_dark_mode: bool = True
) -> Path:
    """Generate QVF admin dashboard with default settings.
    
    Args:
        output_dir: Output directory path
        title: Dashboard title
        api_base_url: API base URL
        theme: Default theme
        enable_dark_mode: Enable dark mode support
        
    Returns:
        Path to generated dashboard
    """
    config = QVFAdminConfig(
        title=title,
        output_dir=Path(output_dir),
        api_base_url=api_base_url,
        theme=theme,
        enable_dark_mode=enable_dark_mode
    )
    
    generator = QVFAdminDashboardGenerator(config)
    return generator.generate_admin_dashboard()