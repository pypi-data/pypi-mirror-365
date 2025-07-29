from setuptools import setup, find_packages

setup(
    name='hammadbhai-tools',
    version='0.1.1',
    description='Useful tools by Hammad Bhai 👑',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Muhammad Hammad Zubair',
    author_email='your-email@example.com',
    url='https://github.com/MUHAMMAD-HAMMAD-ZUBAIR/hammadbhai-tools.git',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
