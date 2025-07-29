from setuptools import setup, find_packages

setup(
    name="cleanmypc",
    version="1.0.3",
    author="Mandel123e",
    author_email="mandel123e@gmail.com",
    description="A Python library to clean cache and temporary files from your PC",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mandel123e/cleanmypc",
    packages=find_packages(),
    install_requires=[
        "send2trash",
        "shutil",
        "tempfile"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
