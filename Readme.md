# 服务说明

## 配置服务

### config目录

#### 服务总配置文件 config_work.ini (config_online.ini)
线上部署后需要*手工*复制为*config_online.ini*
修改后需要*重启服务*
```
cd config
cp config_work.ini config_online.ini
```

#### ruokuai.ini
若快平台配置文件，修改后*无需*重启服务

#### ruokuai.ini
Dama2平台配置文件，修改后*无需*重启服务

## 启动服务
```
sudo supervisord -c /home/kyfw/workspace/code_recognition/config/supervisord.conf
```
