#!/bin/bash
#---
# author:  Jose Luis Pueyo Viltres
# e-mail:  joseluis.pueyo@estudiants.urv.cat
# date:    Tue Apr  9 03:26:46 PM UTC 2024
# version: 0.1
#---
# CLI tool to help manage some configurations of the assembler
# As of v0.1 it is capable of:
#   1. Edit the instructions of the ISA
#   2. Run 

#TODO: Read parameters
#TODO: Validate parameters

#TODO: 

functionality="$(realpath ./src/cli/${1})"

[[ $# -lt 1 ]] && exit 1

[[ ! -f "$functionality" ]] && \
  echo "ERROR: Couldn't find the \`${1}\` functionality" >&2 && \
  echo "Expected to find \`$functionality\`" && \
  exit 2

shift
source ${functionality} $@
