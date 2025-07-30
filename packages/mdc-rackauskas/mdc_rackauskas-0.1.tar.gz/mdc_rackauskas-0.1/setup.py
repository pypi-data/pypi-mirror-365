from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mdc-rackauskas",  # ← UNIKALUS! Jei "mdc" užimtas
    version="0.1",
    author="Matas Račkauskas",
    description="Minecraft Developer CLI Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["colorama"],
    entry_points={
        "console_scripts": [
            "mdc=mdc_tool.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
