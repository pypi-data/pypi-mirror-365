"""
GoSQL - High-Performance Database Connector Library
Setup configuration for PyPI packaging
"""

import os
import sys
import platform
from setuptools import setup, find_packages, Extension
from setuptools.command.build_py import build_py
from setuptools.command.install import install
import subprocess
import shutil

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "psutil>=5.8.0",
        ]

# Get version from git tags or use default
def get_version():
    try:
        # Try to get version from git tags
        result = subprocess.run(['git', 'describe', '--tags', '--exact-match'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip().lstrip('v')
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Try to get version from git commit count
            result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], 
                                  capture_output=True, text=True, check=True)
            commit_count = result.stdout.strip()
            return f"1.0.{commit_count}"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "1.0.0"

class CustomBuild(build_py):
    """Custom build command to compile Go shared library"""
    
    def run(self):
        # Build Go shared library
        self.build_go_library()
        super().run()
    
    def build_go_library(self):
        """Build the Go shared library"""
        print("Building Go shared library...")
        
        # Determine the Go source directory
        go_src_dir = os.path.join(os.path.dirname(__file__), "..", "go")
        go_src_dir = os.path.abspath(go_src_dir)
        
        if not os.path.exists(go_src_dir):
            print(f"Warning: Go source directory not found at {go_src_dir}")
            print("Skipping Go library build. Pre-compiled library should be included.")
            return
        
        # Determine output library name based on platform
        system = platform.system().lower()
        if system == "windows":
            lib_name = "gosql.dll"
        elif system == "darwin":
            lib_name = "libgosql.dylib"
        else:
            lib_name = "libgosql.so"
        
        # Build the shared library
        try:
            # Set environment variables
            env = os.environ.copy()
            env["CGO_ENABLED"] = "1"
            
            # Run go build
            cmd = [
                "go", "build", 
                "-buildmode=c-shared",
                f"-o={lib_name}",
                "main.go"
            ]
            
            subprocess.run(cmd, cwd=go_src_dir, env=env, check=True)
            
            # Create lib directory in gosql package
            lib_dir = os.path.join(self.build_lib, "gosql", "lib")
            os.makedirs(lib_dir, exist_ok=True)
            
            # Copy the shared library
            src_lib = os.path.join(go_src_dir, lib_name)
            dst_lib = os.path.join(lib_dir, lib_name)
            shutil.copy2(src_lib, dst_lib)
            
            print(f"✓ Go shared library built: {lib_name}")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to build Go library: {e}")
            print("Please ensure Go 1.18+ is installed and CGO is enabled")
            # Don't fail the build, assume pre-compiled library exists
        except FileNotFoundError:
            print("Go compiler not found. Please install Go 1.18+ or use pre-compiled library")

class CustomInstall(install):
    """Custom install command"""
    
    def run(self):
        super().run()
        # Post-installation setup if needed
        print("GoSQL installation completed successfully!")

# Package configuration
setup(
    name="gosql-connector",
    version=get_version(),
    author="CoffeeCMS Team",
    author_email="dev@coffeecms.com",
    description="High-performance Go-based SQL connector library for Python with 2-3x better performance",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/coffeecms/gosql",
    project_urls={
        "Bug Tracker": "https://github.com/coffeecms/gosql/issues",
        "Documentation": "https://gosql.readthedocs.io",
        "Source Code": "https://github.com/coffeecms/gosql",
        "Changelog": "https://github.com/coffeecms/gosql/blob/main/CHANGELOG.md",
        "Benchmarks": "https://github.com/coffeecms/gosql/tree/main/benchmarks",
    },
    packages=find_packages(exclude=["tests*", "benchmarks*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Go",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Flask",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-asyncio>=0.15",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "isort>=5.0",
            "pre-commit>=2.0",
        ],
        "benchmark": [
            "mysql-connector-python>=8.0",
            "psycopg2-binary>=2.8",
            "pyodbc>=4.0",
            "matplotlib>=3.0",
            "pandas>=1.0",
            "seaborn>=0.11",
            "jupyter>=1.0",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-asyncio>=0.15",
            "pytest-xdist>=2.0",
            "docker>=5.0",
            "testcontainers>=3.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
            "sphinx-autodoc-typehints>=1.12",
        ],
        "all": [
            # Include all extra dependencies
            "pytest>=6.0", "pytest-cov>=2.0", "pytest-asyncio>=0.15",
            "black>=21.0", "flake8>=3.8", "mypy>=0.800", "isort>=5.0",
            "mysql-connector-python>=8.0", "psycopg2-binary>=2.8", "pyodbc>=4.0",
            "matplotlib>=3.0", "pandas>=1.0", "seaborn>=0.11",
            "docker>=5.0", "testcontainers>=3.0",
            "sphinx>=4.0", "sphinx-rtd-theme>=1.0", "myst-parser>=0.15",
        ]
    },
    entry_points={
        "console_scripts": [
            "gosql-benchmark=gosql.benchmarks.benchmark:main",
            "gosql-test=gosql.tests.test_runner:main",
        ],
    },
    package_data={
        "gosql": [
            "lib/*.so",      # Linux shared library
            "lib/*.dll",     # Windows shared library  
            "lib/*.dylib",   # macOS shared library
            "lib/*.h",       # C header files
            "py.typed",      # Type hints marker
        ],
    },
    include_package_data=True,
    zip_safe=False,  # Required for shared libraries
    cmdclass={
        "build_py": CustomBuild,
        "install": CustomInstall,
    },
    keywords=[
        "database", "sql", "mysql", "postgresql", "postgres", "mssql", "sqlserver",
        "connector", "driver", "go", "performance", "high-performance", "fast",
        "connection-pooling", "cgo", "native", "optimization", "benchmark"
    ],
    platforms=["any"],
    license="MIT",
    
    # Additional metadata
    provides=["gosql"],
    obsoletes=[],
    
    # Wheel configuration
    options={
        "bdist_wheel": {
            "universal": False,  # Platform-specific due to shared libraries
        }
    },
)
