from setuptools import setup, find_packages

setup(
    name='hammadbhai-tools',
    version='0.1.0',
    description='Web search tool for Gemini users using OpenAI SDK style',
    author='Muhammad Hammad Zubair',
    author_email='your-email@example.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'agents>=0.1.18'
    ],
    python_requires='>=3.8',
)
