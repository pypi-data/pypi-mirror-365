from setuptools import setup, find_packages

setup(
    name="rememory",
    version="0.3.4",
    description="A set of lightweight shared memory variable types for safe multiprocessing access",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Nichola Walch",
    author_email="littler.compression@gmail.com",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "no": ["py.typed"],
    },
    install_requires=[
        "posix-ipc>=1.2.0; sys_platform != 'win32'",
        "pywin32>=305; sys_platform == 'win32'",
    ],
    entry_points={
        "console_scripts": [
            "rememory = testScript.__init__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
