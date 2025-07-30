from setuptools import setup, find_packages

setup(
    name="asad-websearch",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "ddgs>=1.0.7",
        "agents-sdk>=0.1.0",
    ],
    author="Asad Shabir",
    description="A simple DuckDuckGo web search tool using ddgs and OpenAI Agents SDK.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/asad-websearch/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
