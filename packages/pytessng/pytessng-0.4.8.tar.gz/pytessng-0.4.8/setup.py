import setuptools
from wheel.bdist_wheel import bdist_wheel


# 读取README.md文件
with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

# 读取requirements.txt文件
with open('requirements.txt', "r", encoding="utf-8") as file:
    install_requires = file.read().splitlines()

# 重写bdist_wheel
class CustomBdistWheel(bdist_wheel):
    def get_tag(self):
        return "cp36", "cp36m", "win_amd64"

# 设置包信息
setuptools.setup(
    name="pytessng",
    version="0.4.8",
    author="Xinghao Su",
    author_email="948117072@qq.com",
    description="TESS NG Toolkit for Network Edit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.jidatraffic.com/",
    python_requires="==3.6.*",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    cmdclass={
        "bdist_wheel": CustomBdistWheel
    },
    zip_safe=False,
    include_package_data=True,
)
