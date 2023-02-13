import os, sys, toml

# Parse server configuration
configPath = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'config.toml'))
config = toml.load(configPath)