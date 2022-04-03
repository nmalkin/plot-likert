import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="plot-likert",
    version="0.4.0",
    author="nmalkin",
    description="Library to visualize results from Likert-style survey questions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="plot graph visualize likert survey matplotlib",
    url="https://github.com/nmalkin/plot-likert",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
)
