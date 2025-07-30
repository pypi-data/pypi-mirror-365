#!/usr/bin/env python3
"""
纯Python版YIRAGE安装脚本 (回退版本)
"""

from setuptools import setup, find_packages
import os

def get_version():
    version_file = os.path.join('python', 'yirage', 'version.py')
    
    # 动态读取版本信息
    try:
        version_globals = {}
        with open(version_file, 'r') as f:
            exec(f.read(), version_globals)
        
        if '__version__' in version_globals:
            return version_globals['__version__']
    except Exception:
        pass
    
    # 备用方法：正则解析
    try:
        with open(version_file, 'r') as f:
            content = f.read()
            import re
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    except Exception:
        pass
    
    return "dev-unknown"

setup(
    name="yica-yirage",
    version=get_version(),
    description="YICA-Yirage: AI Computing Optimization Framework (Pure Python)",
    long_description="YICA-Yirage Pure Python version without C++ extensions",
    long_description_content_type="text/plain",
    author="YICA Team",
    author_email="contact@yica.ai",
    
    package_dir={"": "python"},
    packages=find_packages(where="python"),
    
    install_requires=[
        "numpy>=1.19.0",
        "torch>=1.12.0",
        "z3-solver>=4.8.0",
    ],
    
    extras_require={
        "dev": ["pytest>=6.0", "black>=21.0", "flake8>=3.8"],
        "triton": ["triton>=2.0.0; sys_platform=='linux'"],
        "full": ["torch>=1.12.0", "matplotlib>=3.0.0", "tqdm>=4.0.0"],
    },
    
    python_requires=">=3.8",
    zip_safe=False,
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
