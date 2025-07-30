from setuptools import setup, find_packages

setup(
    name="quoridor-env",
    version="0.1.2",
    description="Python Quoridor game engine with Gym environment for RL",
    author="Christian Contreras",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/quoridor_sim",  # Update if you have a repo
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "gymnasium>=0.28.0",
        "numpy>=1.23",
        # Add other dependencies your package requires
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Software Development :: Libraries",
    ],
    include_package_data=True,
)
