from setuptools import setup, find_packages

setup(
    name="search-mcp",
    version="1.0.0",
    description="Example MCP with internet search capabilities",
    author="Example Author",
    author_email="example@example.com",
    packages=find_packages(),
    install_requires=[
        "mcp[cli]>=1.3.0",
        "requests>=2.28.1",
    ],
    entry_points={
        "console_scripts": [
            "search-mcp=SearchMCP.server:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
) 