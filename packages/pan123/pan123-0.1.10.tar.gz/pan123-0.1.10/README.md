<div align="center">

# Pan123

![Python Version](https://img.shields.io/badge/Python-3.x-blue)
![GitHub License](https://img.shields.io/github/license/SodaCodeSave/Pan123?)
![GitHub Release](https://img.shields.io/github/v/release/SodaCodeSave/Pan123)
![PyPI - Version](https://img.shields.io/pypi/v/pan123)
![Stars](https://img.shields.io/github/stars/SodaCodeSave/Pan123?style=flat&label=Stars&color=yellow)
![Build](https://img.shields.io/github/actions/workflow/status/SodaCodeSave/Pan123/python-package.yml)

Pan123是123云盘开放平台的非官方Python封装库，用于在Python中与123云盘开放平台进行交互

</div>


## 安装

使用pip进行安装

```
pip install pan123
```

### 导入

```python
# 全量导入
from pan123 import Pan123
from pan123.auth import get_access_token
# 如果已经获取了access_token，则可以直接导入Pan123模块
from pan123 import Pan123
```

### 文档

**[Pan123 文档](http://w.sodaopen.top)**

### 已经实现的内容

- 分享链接
- 文件管理
- 用户管理
- 离线下载
- 直链
- 视频转码
- 图床

### 正在编写的内容

- 第三方挂载应用接入
> 由于第三方挂载应用接入需要资质认证，所以暂不编写