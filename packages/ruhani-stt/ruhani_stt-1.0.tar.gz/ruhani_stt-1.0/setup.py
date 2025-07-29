from setuptools import setup, find_packages

setup(
    name="ruhani-stt",  # This is the name that will appear on PyPI
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    author="Farhan Raza Shaikh",
    author_email="itsnobody@zohomail.in",
    description="Offline speech-to-text tool using browser frontend and Python backend",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
