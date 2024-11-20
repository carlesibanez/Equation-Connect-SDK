from setuptools import setup, find_packages

setup(
    name="EquationConnectSDK",
    version="0.2.0",
    author="Carles Ibáñez",
    author_email="carles.ibanez.trullen@gmail.com",
    description="A Python SDK for interacting with Equation Connect devices.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/carlesibanez/Equation-Connect-SDK",
    packages=find_packages(),
    install_requires=[
        "requests>=2.32.3",
        "Pyrebase4>=4.8.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
