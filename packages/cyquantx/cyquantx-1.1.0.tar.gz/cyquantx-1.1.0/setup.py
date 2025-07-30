from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as build_ext_orig
import os

try:
    from Cython.Distutils import build_ext
    use_cython = True
except ImportError:
    from setuptools.command.build_ext import build_ext
    use_cython = False

package_name = "cyquant"

def make_sources(*module_names):
    file_ext = ".pyx" if use_cython else ".cpp"
    return {
        f"{package_name}.{mod}": os.path.join(package_name, mod + file_ext)
        for mod in module_names
    }

modules = ["dimensions", "quantities", "util", "qmath"]
sources = make_sources(*modules)

extensions = [
    Extension(
        name=mod_name,
        sources=[source_path],
        language="c++",
        include_dirs=[package_name],
        extra_compile_args=["-O3"],
    )
    for mod_name, source_path in sources.items()
]

cmdclass = {}
if use_cython:
    cmdclass["build_ext"] = build_ext

setup(
    name="cyquantx",
    version="1.1.0",
    packages=[package_name],
    ext_modules=extensions,
    cmdclass=cmdclass,
    package_data={package_name: ["*.pyx", "*.pxd", "*.cpp"]},
    zip_safe=False,
)

