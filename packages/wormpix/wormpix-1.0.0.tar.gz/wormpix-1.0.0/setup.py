from setuptools import setup, find_packages

setup(
    name="wormpix",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["PyQt6"],
    entry_points={"console_scripts": ["wormpix=wormpix.wormpix:main"]},
    author="Lunar Labs",
    author_email="aadil025@yahoo.com",
    description="🐉 WormPix Pro - Advanced Eye Comfort Tool for Linux",
    url="https://github.com/LunarLumos/wormpix",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Topic :: Desktop Environment",
    ],
    python_requires=">=3.7",
)
