FROM mcr.microsoft.com/devcontainers/python:3.10

RUN apt-get update && apt-get install -y \
    curl \
    libxi6 \
    libxrender1 \
    libxxf86vm1 \
    libxfixes3 \
    libgl1 \
    wayland-protocols \
    libsm6 \
    libxkbcommon0 \
    libepoxy0 \
    && rm -rf /var/lib/apt/lists/*

# Blender 4.5 LTS をダウンロード・解凍して配置
# path: /usr/local/bin/blender/blender
RUN mkdir -p /usr/local/bin/blender && \
    curl -SL "https://download.blender.org/release/Blender4.5/blender-4.5.5-linux-x64.tar.xz" -o blender.tar.xz && \
    tar -xvf blender.tar.xz -C /usr/local/bin/blender --strip-components=1 && \
    rm blender.tar.xz

# 実行パスを通す
ENV PATH="/usr/local/bin/blender:$PATH"