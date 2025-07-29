from setuptools import setup

setup(
    name="mimasv2configtool",
    version="2025.0.3",
    author="Habib Ullah",
    author_email="khaalidi@icloud.com",
    description="SPI Flash configuration tool for Numato Lab Mimas V2 FPGA board",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",  
    url="https://github.com/khaalidi/mimasv2configtool",
    install_requires=[
        "pyserial",
    ],
    entry_points={
        "console_scripts": [
            "mimasv2configtool=mimasv2configtool.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
