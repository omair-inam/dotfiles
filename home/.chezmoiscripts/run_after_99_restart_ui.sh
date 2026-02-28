#!/bin/bash

set -eufo pipefail

# Restart UI processes to apply any changes from earlier scripts
killall Dock
killall Finder
killall SystemUIServer
