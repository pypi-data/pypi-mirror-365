FROM quay.io/pypa/manylinux_2_28_x86_64:latest as build
LABEL authors="Mykola"

RUN yum makecache --refresh

RUN yum -y install openssl-devel
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
RUN export PATH="$HOME/.cargo/bin:$PATH"

WORKDIR /build

COPY install-deps.sh .
RUN ./install-deps.sh

COPY src src
COPY setup_linux_amd.py setup.py
COPY README.md .

COPY build-wheels.sh .
RUN ./build-wheels.sh

FROM scratch as export
COPY --from=build /build/dist /
