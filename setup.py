import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="plot_likert",
    version="0.3.3",
    author="nmalkin",
    description="Library to visualize results from Likert-style survey questions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords = 'plot graph visualize likert survey matplotlib',
    url="https://github.com/nmalkin/plot-likert",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Visualization"
    ],
    python_requires='>=3.6',
    install_requires=[
        'matplotlib',
        'numpy',
        'pandas',
    ],
)
