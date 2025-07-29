import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="s1302003_learn",
    version="2025.07.29.1",
    author="Satvik GANESH",
    author_email="satvikganesh@gmail.com",
    description="This is a test software for class work.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://github.com/SatvG/s1302003_learn",
    license="GPLv3",

    install_requires=[
        'pami',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
    ],

    python_requires='>=3.5'
)
