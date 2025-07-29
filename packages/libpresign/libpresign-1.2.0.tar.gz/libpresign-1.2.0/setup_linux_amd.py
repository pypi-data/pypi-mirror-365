import os

from setuptools import Extension, setup

os.environ["CC"] = "g++"
os.environ["CXX"] = "g++"

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='libpresign',
    version='0.1.2',
    description='Package that just pre-signs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    ext_modules=[
        Extension(
            'libpresign',
            sources=['src/module.cpp', 'src/presign.cpp'],
            extra_compile_args=[
                '-std=gnu++14',
            ],
            extra_link_args=[
                '-std=gnu++14',
                '-lcrypto',
                '-ldl'
            ]
        ),
    ],
)
