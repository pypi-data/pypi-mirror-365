from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="InstaSpy",
    version="1.0.0",
    author="Ivan Firmansyah",
    description="Library Python untuk Instagram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jepluk/instaspy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
    ],
    keywords="instagram api library",
)
