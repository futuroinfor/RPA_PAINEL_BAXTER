import sys
import os
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win64':
    base = 'Win64GUI'

executables = [
    Executable( 'appLPCBOT.py', base=base, target_name="appMonitoraPaineis")
]

buildOptions = dict(
    packages = [],
    includes = [],
    include_files = ['img/', 'configs/', 'logs/'],
    excludes = ['tkinter']
)

setup(
    name = "App Monitoramento dos Paineis",
    version = "2.0",
    description = "Aplicativo de Monitoramento",
    options = dict(build_exe = buildOptions),
    executables = executables
)