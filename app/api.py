# Standard Libraey
import re

# Local Library
from . import util

# Third-Party Library
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

alpm = util.Alpm()

def regex_replace(string, find, replace):
    return re.sub(find, replace, string)

app = FastAPI()
template = Jinja2Templates("templates")
template.env.filters["regex_replace"] = regex_replace

@app.get("/")
async def root(request: Request):
    return template.TemplateResponse("root.html", {"request": request, "pkgs": alpm.get_pkgs(["firefox", "chromium", "discord"])})

@app.get("/package/{pkgname}")
async def package(request: Request, pkgname: str):
    pkg = alpm.get_pkg(pkgname)
    
    if pkg:
        return template.TemplateResponse("package.html", {"request": request, "pkg": pkg})
    else:
        pkgs = alpm.search(pkgname)
        return template.TemplateResponse("virtual_package.html", {"request": request, "name": pkgname, "pkgs": pkgs})