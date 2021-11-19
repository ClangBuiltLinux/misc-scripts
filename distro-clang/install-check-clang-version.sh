#!/usr/bin/env bash

results=$(dirname "$(readlink -f "${0}")")/results.log

set -x

# Debian/Ubuntu
if command -v apt-get &>/dev/null; then
    export DEBIAN_FRONTEND=noninteractive

    apt-get update
    apt-get upgrade -y
    apt-get install --no-install-recommends -y clang
# Fedora
elif command -v dnf &>/dev/null; then
    dnf update -y
    dnf install -y clang
# Arch
elif command -v pacman &>/dev/null; then
    pacman -Syyu --noconfirm
    pacman -S --noconfirm clang
# OpenSUSE Leap/Tumbleweed
elif command -v zypper &>/dev/null; then
    zypper -n up
    zypper -n in clang
fi

echo "$1: $(clang --version | head -n1)" >> "$results"
