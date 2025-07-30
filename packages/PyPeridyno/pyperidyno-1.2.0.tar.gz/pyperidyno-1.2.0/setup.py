'''
Author: unibeam98 beyondevery@live.com
Date: 2025-02-21 15:54:24
LastEditors: unibeam98 beyondevery@live.com
LastEditTime: 2025-07-30 17:16:14
FilePath: \PyPeridyno-package\setup.py
Description: Package PyPeridyno
'''
import setuptools
from setuptools import setup, find_packages, Extension
from setuptools.command.install import install
from setuptools.command.build_ext import build_ext
import os
import sys
import glob
import shutil


class CustomInstallCommand(install):
    def run(self):
        # copy data
        os.makedirs('C:/ProgramData/Peridyno/data/font', exist_ok=True)
        font_dir = os.getcwd()
        source_path = os.path.join(font_dir, 'src/font')
        destination_path = 'C:/ProgramData/Peridyno/data/font'
        shutil.copytree(source_path, destination_path, dirs_exist_ok=True)

        # copy example
        os.makedirs('C:/ProgramData/Peridyno/data/example', exist_ok=True)
        example_dir = os.getcwd()
        source_path = os.path.join(example_dir, 'src/example/')
        destination_path = 'C:/ProgramData/Peridyno/data/example'
        shutil.copytree(source_path, destination_path, dirs_exist_ok=True)

        # copy cufft
        cuda_path = os.getenv('CUDA_PATH')
        # 如果CUDA_PATH环境变量没有被设置，则退出脚本
        if cuda_path is None:
            print("CUDA_PATH 环境变量未设置")
            exit()
        cuda_path_bin = cuda_path + '\\bin'
        cuda_path_lib = cuda_path + '\\lib\\x64'
        python_install_path = sys.prefix
        cufft_file_dll = [f for f in os.listdir(cuda_path_bin) if 'cufft' in f]
        cufft_file_lib = [f for f in os.listdir(cuda_path_lib) if 'cufft' in f]
        for file in cufft_file_dll:
            shutil.copy(os.path.join(cuda_path_bin, file), python_install_path)
            print(os.path.join(cuda_path_bin, file))

        for file in cufft_file_lib:
            shutil.copy(os.path.join(cuda_path_lib, file), python_install_path)
            print(os.path.join(cuda_path_lib, file))
        install.run(self)


setuptools.setup(
    name="PyPeridyno",
    version="1.2.0",
    author="unibeam",
    author_email="xiaowei@iscas.ac.cn",
    description="A python package for Peridyno",
    long_description=open('README.rst').read(),
    long_description_content_type="text/markdown",
    license='Apache License, Version 2.0',
    url="https://peridyno.com/",
    packages=find_packages(),
    # package_dir={'PyPeridyno':'src'}
    package_data={
        'PyPeridyno': ['*.dll', '*.pyd', '*.lib', '*.exe'],
    },
    data_files=[
        ('.', [f for pattern in ['src/*.dll', 'src/*.pyd', 'src/*.lib',
         'src/*.exe', 'src/*.exp'] for f in glob.glob(pattern)])
    ],
    install_requires=[  # 如果需要其他依赖，请列出
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
    python_requires='>=3.12',
)
