# 项目名称：视具体项目修改

# 模板目录说明

# 开发约定

## 功能开发约定
* 针对各平台个性需求，可在页面模板中通过平台标识判断是否展示。在handler和biz层级，代码必须独立。若需要复用代码，使用继承方式

## 配置文件约定
* config_master.ini 为线服务主配置文件，需存入git库。 上线后应复制为config_online.ini。程序中对于主配置文件，只读取config_online.ini。

## 命名约定

###后缀：
> 类型：_type
> 代码：_code
> 编å·：_no
> 数量：_num
