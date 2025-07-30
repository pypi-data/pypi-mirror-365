from setuptools import setup, find_packages

setup(
    name="linkmod",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        'requests',
        'keyring',
    ],
    entry_points={
        'console_scripts': [
            'linkMod=linkmod.linkmod:main',
        ],
    },
    author="Rishi Bhati",
    author_email="bhatirishi5@gmail.com",
    description="A simple tool to customize links.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Rishi-Bhati/linkmod.git",  # Update with your repository URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
