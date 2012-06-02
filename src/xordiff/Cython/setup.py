from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy
import os
includes = [numpy.get_include()]
inclibraries = []
extralinkargs = []
extrabuildargs = []

files = ["xordiff.pyx"]

ext_modules = [Extension("_xordiff", 
						files,
						language="c++",
						include_dirs=includes,
						libraries=inclibraries,
						extra_link_args=extralinkargs,
						extra_compile_args=extrabuildargs

						)]

setup(
  name = 'xordiff',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
