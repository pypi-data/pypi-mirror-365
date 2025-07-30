from setuptools import setup, find_packages

setup(
    name="quoridor-env",
    version="0.1.4",
    description="Python Quoridor game engine with Gym environment for RL",
    author="Christian Contreras",
    author_email="chrisjcc@users.noreply.github.com",
    url="https://github.com/chrisjcc/quoridor",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "gymnasium>=0.28.0",
        "numpy>=1.23",
        "fastapi>=0.104.0",
        "pydantic>=2.0.0",
        "uvicorn[standard]>=0.24.0",
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
