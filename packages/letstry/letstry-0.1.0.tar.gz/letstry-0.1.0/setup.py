from setuptools import setup

setup(
    name="letstry",
    version="0.1.0",
    py_modules=["letstry"],
    author="Mukesh Kumar",
    author_email="creatorsk549@gmail.com",
    description="Toolkit for RCE testing, command execution, and file enumeration",
    # long_description=open("README.md").read(),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mukeshkumar-a",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
