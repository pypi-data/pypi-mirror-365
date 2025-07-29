from time import time
import setuptools
# c:\Python38\python.exe setup.py clean --all
# c:\Python38\python.exe setup.py sdist
# c:\Python38\python.exe -m build
# c:\Python38\python.exe -m twine upload dist/* --skip-existing
# 用户名 jerry1979

# pypi-AgEIcHlwaS5vcmcCJGE5OWJhOTg1LWYzODAtNDUwZC1hNjhhLTlkZWZhYWFhMjg1ZQACKlszLCIzNWQzNjY4My0xMTllLTQ1MGItYjcxOC01ODEyNzM5YWRhYTAiXQAABiCwNAt78Brwwrqd90FC5vH78uhTyNllGrCzjuaVB-xtGw

# 在HOME目录下建立.pypirc文件可以更为便捷的配置token
'''
d1815a30159a81fd
691362c6f6f71b38
a9a1df09e6cf5c22
3b09f1a0d8f6c52a
4d52b7b60c6d15ae
3e4f93aada7a3901
5b95b9ab769f9e58
72097631bef24c76
'''

# (myBase) E:\BaiduSyncdisk\pyLib\mxupyPackage>python setup.py sdist bdist_wheel

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

# 要注意，每个包下面必须有__init__.py文件，find_packages需要

setuptools.setup(
    name="mxupy",
    version="1.0.10",
    author="jerry1979",
    author_email="6018421@qq.com",
    description="An many/more extension/utils for python",
    url="http://www.xtbeiyi.com/",
    packages=setuptools.find_packages(),
)
