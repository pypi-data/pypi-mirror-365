from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vkb-lib",
    version="0.1.0",
    author="VKB Architector",
    description="Resource-aware architecture library for building cognitive computing systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jobsbka/VKB_Lib",
    packages=find_packages(where="vkb_lib"),
    package_dir={"": "vkb_lib"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "test": ["pytest>=6.0", "pytest-cov"],
    },
    include_package_data=True,
    keywords="ai architecture resource-oriented cognitive computing",
    project_urls={
        "Documentation": "https://github.com/Jobsbka/VKB_Lib/docs",
        "Source": "https://github.com/Jobsbka/VKB_Lib/vkb_lib",
    },
)