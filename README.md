# 浙大硕士学位论文盲审意见轮询

自动化监测学位论文的意见，若有增加则通过[pushplus](https://www.pushplus.plus/)推送至微信。脚本保存session减少重复登录，保存推送记录避免相同信息重复推送

由于暂未找到长时间保持登录状态的方法，使用时必须输入统一认证密码，同时脚本保存的session权限较高，因此不建议代挂机


## 服务器运行

可以部署在实验室/腾讯/阿里/境外等服务器上，所有资源均在本地，执行任务和ip都更稳定，建议优先选择这种方法

1. 安装Python3环境
2. 安装requests, BeautifulSoup4包 `python3 -m pip install requests, BeautifulSoup4 lxml`
3. 注册[pushplus](https://www.pushplus.plus/)推送平台并获取token
4. 下载getReviews-local.py，并修改代码最后部分的个人信息以及脚本所在路径（在Windows上路径也需要用`/`连接）
5. 添加定时任务`crontab -e`，新增一行`分钟 9-22 * * * path/python3 path/getReviews-local.py`（Windows用`任务计划程序`）。注意查看服务器的时区，如果不是UTC+8则更改9-22为对应的小时，一般为`1-14`。`分钟`自己随便写一个0到59之间的数字，即在9-22点的第几分钟分钟自动执行脚本


## Github Action

使用坚果云的webdav保存session和推送记录。经测试保存的session不能用于较大跨度的地区，使用校内保存的session时，可以在上海ip下使用，但是无法在Github Action下使用（Azure美国）。使用Github Action可能会较为频繁地登录

GitHub Action高负载时任务可能延迟甚至被取消，同时每次查询的ip会发生变化。测试两天未发生异常

1. fork此仓库
2. 注册[pushplus](https://www.pushplus.plus/)推送平台并获取token
3. 注册[坚果云](https://www.jianguoyun.com/)，在云盘中新建文件夹`PythonAPI`（或其他），在`账户信息`-`安全选项`中点击`添加应用`后记住密码
4. 在fork后你自己的仓库下依次点击`Setting`-`Secrets and variables`-`Actions`
5. 点击`New repository secret`添加`USER`为学号；`PASSWORD`为密码；`PUSHKEY`为pushplus的token；`DAVUSR`为坚果云邮箱；`DAVPWD`为第3步生成密码；`DAVPATH`为`/dav/PythonAPI`，如果第3步改为其他的也一起修改
6. 修改`.github/workflows/github-actions.yml`第11行的`分钟`为你想要运行的时间并保存，非5的倍数通常负载低一些

## Thanks

登录部分参考[ZJU-nCov-Hitcarder](https://github.com/Tishacy/ZJU-nCov-Hitcarder)

easydav.py使用[easywebdav](https://pypi.org/project/easywebdav/1.0.1/)，更新代码兼容python3
