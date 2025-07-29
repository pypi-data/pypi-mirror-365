from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='my-package-himanshi',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='Himanshi',
    author_email='your.email@example.com',
    description='A Python package to interface with local LLM Gemma:2b via Ollama',
    keywords='zunno chatbot ollama gemma',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my-package-himanshi',  # Optional: replace with actual link if available
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
