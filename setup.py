from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = {
    'packages': ['libs.protocol'],
    'excludes': [],
    'include_files': []
}

base = 'Console'

executables = [
    Executable('serial_test.py', base=base)
]

setup(name='serial_test',
      version = '0.1',
      description = 'Serial Port Device Test',
      options = dict(build_exe = buildOptions),
      executables = executables)
