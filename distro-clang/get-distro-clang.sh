#!/usr/bin/env bash

trap 'exit' INT

# Make sure we have the required binaries
for NAME in podman docker; do
    command -v "${NAME}" &>/dev/null && BINARY=${NAME}
done
if [[ -z ${BINARY} ]]; then
    echo "Neither podman nor docker could be found on your system! Please install one to use this script."
    exit 1
fi

DOCKER_DISTROS=(
    archlinux/archlinux
    debian:oldstable-slim
    debian:stable-slim
    debian:testing-slim
    debian:unstable-slim
    fedora
    fedora:rawhide
    opensuse/leap
    opensuse/tumbleweed
    ubuntu:18.04
    ubuntu:20.04
    ubuntu
    ubuntu:rolling
    ubuntu:devel
)

BASE=$(dirname "$(readlink -f "${0}")")

rm "${BASE}"/results.log

for DISTRO in "${DOCKER_DISTROS[@]}"; do
    DISTRO=docker.io/${DISTRO}
    "${BINARY}" pull "${DISTRO}"
    "${BINARY}" run \
        --rm \
        --init \
        --volume="${BASE}:${BASE}" \
        --workdir="${BASE}" \
        "${DISTRO}" \
        "${BASE}"/install-check-clang-version.sh "${DISTRO}"
done

echo
cat "${BASE}"/results.log
