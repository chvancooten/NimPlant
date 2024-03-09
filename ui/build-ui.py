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

import os
import shutil
import subprocess

# Compile the Next frontend
print("Building Nimplant frontend...")

process = subprocess.Popen("npm run build", shell=True)
process.wait()

# Put the output files in the right structure for flask
print("Structuring files...")

source_directory = "out/"
target_directory = "out/static/"
files = [
    "_next",
    "404.html",
    "favicon.png",
    "favicon.svg",
    "nimplant-logomark.svg",
    "nimplant.svg",
]

os.mkdir(target_directory)
for f in files:
    shutil.move(source_directory + f, target_directory + f)

# Move the output files to the right location
print("Moving files to Nimplant directory...")

target_directory = "../server/web"
shutil.rmtree(target_directory)
shutil.move(source_directory, target_directory)

print("Done!")
