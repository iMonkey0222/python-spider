# python-spider

本系列代码包含各个爬虫项目小实战，如：

- Requests+正则表达式爬取猫眼电影
- 使用Selenium模拟浏览器抓取淘宝商品美食信息
- 使用Redis+Flask维护动态代理池
- ...

# 开发环境如下

采用`pipenv`方式管理开发环境

安装环境步骤如下：

下载`Pipfile`文件，在其所在目录运行以下命令：

```python
# step1：创建python3.6的环境
pipenv --python 3.6

# step2：创建pipenv环境
pipenv shell

# step3：安装Pipfile文件中依赖的包
pipenv install
```

