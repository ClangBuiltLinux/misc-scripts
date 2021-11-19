#!/usr/bin/env bash

function is_installed() {
    command -v "$1" &>/dev/null
}

results=$(dirname "$(readlink -f "${0}")")/results.log

set -x

# Debian/Ubuntu
if is_installed apt-get; then
    export DEBIAN_FRONTEND=noninteractive

    apt-get update
    apt-get upgrade -y
    apt-get install --no-install-recommends -y clang
# Fedora
elif is_installed dnf; then
    dnf update -y
    dnf install -y clang
# Arch
elif is_installed pacman; then
    pacman -Syyu --noconfirm
    pacman -S --noconfirm clang
# OpenSUSE Leap/Tumbleweed
elif is_installed zypper; then
    zypper -n up
    zypper -n in clang
fi

echo "$1: $(clang --version | head -n1)" >>"$results"
