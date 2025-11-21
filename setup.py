from setuptools import setup, find_packages
import os

# Read requirements
def read_requirements():
    requirements_file = 'requirements.txt'
    if os.path.exists(requirements_file):
        with open(requirements_file) as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Read README
def read_readme():
    readme_file = 'README.md'
    if os.path.exists(readme_file):
        with open(readme_file, encoding='utf-8') as f:
            return f.read()
    return ""

setup(
    name="professor-profiler",
    version="1.0.0",
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=read_requirements(),
    python_requires='>=3.10',
    author="Professor Profiler Team",
    description="Multi-agent exam analysis system powered by Google Gemini",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
)
