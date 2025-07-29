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
            include_dirs=[
                '/opt/homebrew/Frameworks/Python.framework/Versions/3.10/include',
                '/opt/homebrew/Cellar/openssl@3/3.1.0/include',
            ],
            library_dirs=[
                '/opt/homebrew/Cellar/openssl@3/3.1.0/lib/',
            ],
            sources=['src/module.cpp', 'src/presign.cpp'],
            extra_compile_args=[
                '-std=gnu++14',
                '-mmacosx-version-min=13.0',
                '-stdlib=libc++',
            ],
            extra_link_args=[
                '-std=gnu++14',
                '-mmacosx-version-min=13.0',
                '-stdlib=libc++',
                '-lcrypto',
                '-ldl'
            ]
        ),
    ],
)
