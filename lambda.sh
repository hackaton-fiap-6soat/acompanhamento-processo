#!/bin/bash

# Limpa pacotes anteriores
rm -rf build/ lambda-api.zip lambda-sqs.zip

# Cria pasta de build
mkdir -p build

# Instala dependências no build
pip install -r requirements.txt --platform manylinux2014_x86_64 --target build/ --only-binary=:all:

# Adiciona arquivos necessários para API Lambda
cp -r app/ build/
cd build
zip -r ../lambda-api.zip .

# Remove build
rm -rf build/
