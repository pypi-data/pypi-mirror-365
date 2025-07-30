from setuptools import setup,find_packages

setup(
    name='pjsonpath',
    version='1.5',
    packages=find_packages(),
    install_requires=[
    ],
    description=(
        'Python查找不限层级Json数据中某个key或者value的路径'
    ),
    author='yanqing.wang'
#     entry_points='''
# [console_scripts]
# pjs=parsjsonpath.parsjsonpath:parsjsonpath
# ''',
)
