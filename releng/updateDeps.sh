#!/usr/bin/env sh

wget -O kiAssemblyVariant/sexpr.py https://raw.githubusercontent.com/yaqwsx/KiKit/master/kikit/sexpr.py
wget -O kiAssemblyVariant/eeschema.py https://raw.githubusercontent.com/yaqwsx/KiKit/master/kikit/eeschema_v6.py

sed -i 's/from kikit.sexpr import/from .sexpr import/g' kiAssemblyVariant/eeschema.py
