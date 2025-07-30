import os
import subprocess
from setuptools import setup, find_packages, Extension

def pkgconfig_flags(package, flag_type):
    """ Get output of pkg-config --cflags/--libs [package] """
    try:
        command = ['pkg-config', f'--{flag_type}', package]
        output = subprocess.check_output(command).decode('utf-8').strip()
        return output.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"WARNING: Could not found pkg-config or '{package}' packages.")
        return []

opt_cflags = ["-Werror=format-security"]
# GTK 2.0
gtk2_cflags = pkgconfig_flags('gtk+-2.0', 'cflags')
gtk2_libs = pkgconfig_flags('gtk+-2.0', 'libs')
# GLib 2.0
glib2_cflags = pkgconfig_flags('glib-2.0', 'cflags')
glib2_libs = pkgconfig_flags('glib-2.0', 'libs')
# (!) ALL
all_cflags = gtk2_cflags + glib2_cflags + opt_cflags
all_libs = gtk2_libs + glib2_libs + opt_cflags
# Ignore Duplicated
all_cflags = list(dict.fromkeys(all_cflags))
all_libs = list(dict.fromkeys(all_libs))

gtk_dialog_module = Extension(
    'sdgp.gtk.dialog',                 # Module name
    sources=['src/sdgp/gtk/dialog.c'], # C sourtce file
    extra_compile_args=all_cflags,     # cflags is there
    extra_link_args=all_libs,          # libs is there
)

setup(
    name='sdgp',
    version='0.91.0',
    packages=find_packages(exclude=['tests']),
    ext_modules=[
        gtk_dialog_module
    ],
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'my_command = sdgp.module:main_func',
        ],
    },
    # ... 他のメタデータ ...
)
