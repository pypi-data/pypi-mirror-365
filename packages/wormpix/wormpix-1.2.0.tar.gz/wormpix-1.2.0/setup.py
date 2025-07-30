from setuptools import setup, find_packages

setup(
    name="wormpix",
    version="1.2.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={"wormpix": ["wormpix_icon.png"]},
    install_requires=["PyQt6"],
    entry_points={
        "console_scripts": [
            "wormpix=wormpix.wormpix:main",
        ],
    },
    author="Lunar Labs",
    author_email="aadil025@yahoo.com",
    description="🐉 WormPix - Advanced Eye Comfort & Screen Warmth Tool with Eye Rest Alarm",
    url="https://github.com/LunarLumos/wormpix",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Topic :: Desktop Environment",
    ],
    python_requires=">=3.7",
)
