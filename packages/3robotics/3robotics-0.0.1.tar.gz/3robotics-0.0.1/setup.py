from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="3robotics",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        'roslibpy>=1.3.0',
        'dataclasses>=0.6;python_version<"3.7"',
        'typing-extensions>=4.0.0',
    ],

    # Project metadata
    author="3robotics",
    author_email="towardsrwby@gmail.com",
    description="A Python library for controlling AlphaDog robotic dogs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/3robotics/3robotics",
    project_urls={
        "Bug Tracker": "https://github.com/3robotics/3robotics/issues",
        "Documentation": "https://github.com/3robotics/3robotics/wiki",
        "Source Code": "https://github.com/3robotics/3robotics",
    },    # Classification info
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    # Python version requirement - Only Python 3.9 is supported
    python_requires='==3.9.*',

    # Additional dependencies
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=22.0',
            'isort>=5.0',
            'flake8>=3.9',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=0.5',
        ],
    },

    # Include additional files
    package_data={
        '3robotics': ['py.typed'],
    },
    include_package_data=True,

    # Entry points
    entry_points={
        'console_scripts': [
            '3robotics-demo=examples.simple_demo:main',
        ],
    },

    # Keywords
    keywords='robotics, alphadog, ros, robot control, python',
)
