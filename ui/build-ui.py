#!/usr/bin/python3

# -----
#
#   NimPlant - A light-weight stage 1 implant and C2 written in Nim and Python
#   By Cas van Cooten (@chvancooten)
#
#   This is a helper script to build the Next.JS frontend
#   and move it to the right directory for use with Nimplant.
#   End-users should not need to use this script, unless frontend
#   modifications have been made.
#
# -----

import os, shutil, subprocess

# Compile the Next frontend
print("Building Nimplant frontend...")

process = subprocess.Popen("npm run build", shell=True)
process.wait()

# Put the output files in the right structure for flask
print("Structuring files...")

sourcedir = "out/"
targetdir = "out/static/"
files = [
    "_next",
    "404.html",
    "favicon.png",
    "favicon.svg",
    "nimplant-logomark.svg",
    "nimplant.svg",
]

os.mkdir(targetdir)
for f in files:
    shutil.move(sourcedir + f, targetdir + f)

# Move the output files to the right location
print("Moving files to Nimplant directory...")

targetdir = "../server/web"
shutil.rmtree(targetdir)
shutil.move(sourcedir, targetdir)

print("Done!")
