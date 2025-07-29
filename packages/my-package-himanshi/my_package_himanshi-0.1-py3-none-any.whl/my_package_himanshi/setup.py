from setuptools import setup, find_packages

setup(
    name='my-package-himanshi',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='Himanshi',
    author_email='your-email@example.com',
    description='Python wrapper to interact with Ollama-served Gemma LLM',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my-package-himanshi',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
