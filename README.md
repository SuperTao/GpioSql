使用python,mysql,sqlserver存储开发板gpio的状态。

### main.py

* 将开发板的gpio状态数据保存到mysql中。

* 将本地的mysql数据读取，上传远程的sqlserver服务器中。

* 定时发送心跳数据到sqlserver中。确保连接没有断开。 

由于开发板中没有移植python操作sqlserver的库，所以只能使用C语言连接sqlserver，再通过python调用C语言实现。生成C动态库的方法。

`arm-linux-gcc sqlserver.c -fPIC -shared -o libsqlserver.so -L /usr/local/freetds-arm/lib -lsybdb -I /usr/local/freetds-arm/include/`

将生成的libsqlserver.so放在当前目录即可。

连接数据库的参数都写在配置文件中，如果配置文件不存在就会自动生成。

监听配置文件的变化，可以实时改变配置文件中的一些参数。

### LocalDetect

添加本地检测参数。

在板子上运行LocalDetect.py，在windows上运行LocalDetect.exe。

如果在一个局域网中，并且分配了ip，那么windows上的运行的LocalDetect.exe就会显示板子的ip地址和mac地址。
