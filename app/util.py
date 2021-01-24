# Standard Library
import re, subprocess
from collections import Counter
from itertools import chain
from typing import Optional

# Third-Party Library
import pyalpm

Package = Optional[pyalpm.Package]
Package_List = list[Package]
Package_Dict = dict[str, Package_List]

def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

class Alpm(object):
    def __init__(self, root_path: str="/", db_path: str="/var/lib/pacman", conf_path: str="/etc/pacman.conf"):
        self.handle: pyalpm.Handle = pyalpm.Handle(root_path, db_path)
        self.syncdbs: list = []

        with open(conf_path) as f:
            lines: list = [line.strip() for line in f.readlines()]
        
        for number, line in enumerate(lines):
            match: re.Match = re.match(r"^\[(?P<REPO_NAME>.*)\]$", line)

            if match and "SigLevel" in  lines[number + 1]:
                self.syncdbs.append(
                    self.handle.register_syncdb(
                        match.group("REPO_NAME"),
                        pyalpm.SIG_DATABASE_OPTIONAL
                    )
                )

        self.installed = sorted(run_cmd(["pacman", "-Qq"]).stdout.split())

    def get_pkg(self, pkgname: str) -> Package:
        for syncdb in self.syncdbs:
            pkg: pyalpm.Package = syncdb.get_pkg(pkgname)
            
            if pkg: return pkg

        return None

    def get_pkgs(self, pkgnames: list[str]) -> Package_List:
        return [
            self.get_pkg(pkgname)
            for pkgname in pkgnames
        ]

    def get_depends(self, pkgname: str) -> list[Optional[str]]:
        return [
            pkg
            for pkg in  run_cmd(["pactree", "--sync", "--unique", pkgname]).stdout.split()
            if not pkg in self.installed
        ]

    def get(self, pkgnames: list[str]) -> Package_Dict:
        pkgs = {
            pkgname: self.get_depends(pkgname)
            for pkgname in pkgnames
        }

        pkgs["common"] = [
            key
            for key, value in Counter(chain.from_iterable(pkgs.values())).items()
            if value > 1
        ]

        for key, value in pkgs.items():
            if key != "common":
                pkgs[key] = [
                    self.get_pkg(pkg)
                    for pkg in value
                    if not pkg in pkgs["common"]
                ]

        pkgs["common"] = [
            self.get_pkg(pkg)
            for pkg in pkgs["common"]
        ]

        return pkgs
    
    def download(self, pkgnames: list[str]) -> Package_Dict:
        pkgs = {
            key: [
                run_cmd(["pacman", "-Sp", pkg.name]).stdout.split()[0]
                for pkg in value
            ]
            for key, value in self.get(pkgnames).items()
        }

        return pkgs
    
    def search(self, pkgname: str) -> Package_List:
        pkgs = []

        for syncdb in self.syncdbs:
            for pkg in syncdb.search(pkgname):
                if pkgname in [re.sub(r"=.*$", "", value) for value in pkg.provides]:
                    pkgs.append(pkg.name)

        return pkgs
