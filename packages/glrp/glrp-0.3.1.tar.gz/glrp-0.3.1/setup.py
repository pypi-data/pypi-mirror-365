import setuptools
import subprocess
import os

glrp_version = (
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)

if "-" in glrp_version:
    # when not on tag, git describe outputs: "1.3.3-22-gdf81228"
    # pip has gotten strict with version numbers
    # so change it to: "1.3.3+22.git.gdf81228"
    # See: https://peps.python.org/pep-0440/#local-version-segments
    v, i, s = glrp_version.split("-")
    glrp_version = v + "+" + i + ".git." + s

assert "-" not in glrp_version
assert "." in glrp_version

assert os.path.isfile("glrp/version.py")
with open("glrp/VERSION", "w", encoding="utf-8") as fh:
    fh.write("%s\n" % glrp_version)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="glrp",
    version=glrp_version,
    author="Ole Herman Schumacher Elgesem",
    author_email="",
    description="Parser for git log --raw",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/olehermanse/glrp",
    packages=setuptools.find_packages(),
    package_data={"glrp": ["VERSION"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    entry_points={"console_scripts": ["glrp = glrp.cli:main"]},
    install_requires=[],
)
