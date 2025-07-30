# pytessng -- TESS NG 路网编辑工具

## 简介

`pytessng`是基于微观交通仿真软件`TESS NG`二次开发的仿真路网编辑工具，旨在为`TESS NG`的用户提供一个更为便捷、高效的路网编辑解决方案，其主要包括三类功能：

1. **多源数据导入建网**
   - 能够快速构建高精度仿真路网，支持复杂道路拓扑结构自动解析；
   - 支持将 OpenDrive、Shapefile、OpenStreetMap、Excel 等格式的数据一键导入。

2. **多格式路网输出**
   - 具备坐标系自动转换功能（WGS84），支持三维高程数据输出，满足数字孪生场景需求；
   - 支持将路网导出为 OpenDrive、Shapefile、GeoJSON、JSON 等多种格式。

3. **智能路网优化**
   - 指定连接段长度打断路段、移动代码创建的路段的点位等路段级操作；
   - 合并相同车道路段、简化路段点位等路网级操作。


## 安装

1. **环境要求**

   - 需使用 Python 3.6 环境。

2. **安装命令**

   - 在命令行中执行以下命令进行安装：
   
    `pip install pytessng -i https://pypi.tuna.tsinghua.edu.cn/simple/`


## 快速入门

1. 编写如下代码：

```python
from pytessng import TessngObject
TessngObject(True)
```
2. 按以下步骤完成激活操作：
   - 运行上述代码后，将弹出软件激活弹窗；
   - 在弹窗中，点击导入激活码选项；
   - 选择提供的**试用版 license**，然后点击提交按钮；
   - 提交完成后，关闭当前激活弹窗；
   - 再次启动代码，即可正常运行软件。


## 其他说明

1. 启动代码后，会在启动代码同级目录下生成 WorkSpace 文件夹，其中包含 Cert、SimuResult 等子文件夹。

2. 若试用版 license 到期，将弹出权限提示弹窗显示`没有权限加载插件`，**但只要点击 OK 即可**。

3. 更多详细使用说明，请查看济达交通官网(https://www.jidatraffic.com/)。
