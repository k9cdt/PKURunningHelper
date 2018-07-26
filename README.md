# PKURunningHelper

这是一个慢性腰痛但是开不出证明的苦逼大学生为了能够毕业而写的小工具，用于自动生成和上传跑步记录，目前支持 PB 。

该项目改写自我的一个学长的项目 [PKULayer](https://github.com/tegusi/PKULayer)


## 依赖环境

+ 该项目目前仅支持 Python 3
```
$ apt-get install python3.6
```

+ 安装依赖包 requests
```
$ pip3 install requests
```

+ 可选择安装 simplejson
```
$ pip3 install simplejson
```

## 下载

+ 下载这个分支到本地:
```
$ git clone https://github.com/zhongxinghong/PKURunningHelper
```

## 用法

+ 进入项目根目录
```
$ cd PKURunningHelper/
```

+ 首先根据提示，修改配置文件 config.ini
```
$ vim config.ini
```

+ 运行 runner.py 查看命令行界面，输入参数 --help 查看用法
```
$ python3 runner.py --help

Usage: PKU running helper ! Check your config first, then enjoy yourself !

Options:
  -h, --help   show this help message and exit
  -c, --check  show 'config.ini' file
  -s, --start  run the runner's client
```

+ 输入参数 --check 检查配置文件的解析情况
```
$ python3 runner.py --check

Section [Base]
{
    "software": "PB",
    "mobile": "Android"
}


Section [PB]
{
    "studentid": "1x000xxxxx",
    "password": "1x000xxxxx",
    "distance": "1.20",
    "pace": "4.50",
    "stride_frequncy": "160"
}
```

+ 确保配置文件书写，然后输入 --start，即可完成一次上传
```
$ python3 runner.py --start

Upload record successfully !
```

## 文件夹结构与工作原理
```
PKURunningHelper/
├── PB
│   ├── __init__.py
│   ├── client.py               // PBclient 类，伪造 HTTP 请求，生成 Running Record
│   └── data
│       └── 400m.locus.json     // 在五四操场跑一圈对应的经纬度数据，抽离和修改自我曾经的跑步记录
├── config.ini
├── runner.py
├── test
│   └── PB                      // 主要是 Fiddler 抓到的 PB App 数据包，其中 gz 文件提取自 request body
│       ├── 11km.locus.json
│       ├── 309.gz
│       ├── ......
│       └── 867_Request.txt
└── util
    ├── __init__.py
    ├── error.py
    ├── utilclass.py
    └── utilfuncs.py
```

### PBclient 的工作原理
+ 首先伪装登录，获取 session token 和个人标识 biggerId
+ 根据 Fiddler 抓包结果，伪造数据包，并引入随机量
+ 利用 gzip 压缩数据包，然后伪造 multipart-form/data 请求，上传数据包

如果你需要查看 gzip 数据包，可以通过以下命令解压，将结果输出至终端
```
$ gzip -d 867.gz -c
```
也可以直接写入到 json 文件
```
$ gzip -d 867.gz -c > 867.json
```

## 声明
本项目仅供参考学习，请自行承担使用不当导致的一切后果。