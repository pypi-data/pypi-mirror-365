from setuptools import setup, find_packages

setup(
    name="lang_voter",
    version="0.1.0",
    author="Yash Ingle",
    description="Voting-based sentence-level language classifier for Indian languages",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yashingle-ai/lang_voter",  # Replace with your repo
    packages=find_packages(),
    install_requires=[
        "scikit-learn",
        "requests",
        "numpy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
