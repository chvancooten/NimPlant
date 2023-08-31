# Package information
# NimPlant isn't really a package, Nimble is mainly used for easy dependency management
version       = "1.2"
author        = "Cas van Cooten"
description   = "A Nim-based, first-stage C2 implant"
license       = "MIT"
srcDir        = "."
skipDirs      = @["bin", "commands", "util"]

# Dependencies
requires "nim >= 1.6.12"
requires "nimcrypto >= 0.6.0"
requires "parsetoml >= 0.7.1"
requires "pixie >= 5.0.6"
requires "ptr_math >= 0.3.0"
requires "puppy >= 2.1.0"
requires "winim >= 3.9.2"
requires "winregistry >= 2.0.0"