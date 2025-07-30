from setuptools import setup, find_packages

setup(
    name='mdc-rackauskas',
    version='0.4',
    packages=find_packages(),
    install_requires=[
        'colorama'
    ],
    entry_points={
        'console_scripts': [
            'mdc=mdc_tool.main:main'
        ]
    },
    author='Tavo vardas',
    description='Minecraft server downloader ir launcher',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
