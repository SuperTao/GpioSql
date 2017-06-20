#include <stdio.h>  
#include <string.h>  
#include <stdlib.h>  
#include <unistd.h>  
#include <sybfront.h>  
#include <sybdb.h>  

DBPROCESS *dbprocess;
char tableName[32];

/* 打开数据库
 * 将一些数据保存到全局变量中,由于要用python调用C,在python中实现结构体比较麻烦，
 * 所以就没有采用返回值给python，所以采用全局变量
*/
int openSqlserver(char *szUsername, char *szPassword, char *szDBName, char *szServer, char *szTable)
{
    int ret;

    memset(tableName, 0, sizeof(tableName));
    // 将数据库的表名保存到全局变量中
    strcpy(tableName, szTable);
    
    printf("name: %s\n", szUsername);
    printf("password: %s\n", szPassword);
    printf("szDbname: %s\n", szDBName);
    printf("szServer: %s\n", szServer);
    printf("tableName: %s\n", tableName);
    //初始化db-library  
    dbinit();  
    //连接数据库  
    LOGINREC *loginrec=dblogin();  
    //连接数据库  
	// 设置登录的用户名
    DBSETLUSER(loginrec,szUsername);  
	// 设置登录密码
    DBSETLPWD(loginrec,szPassword);  
	// 连接sqlserver服务器地址和端口号,这里才是连接
    printf("open sqlserver...\n");
    dbprocess=dbopen(loginrec,szServer);  
    if(dbprocess==FAIL){  
        printf("Connect MSSQLSERVER fail\n");  
        return 0;  
    }else{  
        printf("Connect MSSQLSERVER success\n");  
    }  
	// 连接数据库
    if(dbuse(dbprocess,szDBName)==FAIL){  
        printf("Open data basename fail\n");  
        return 0;
    }else{  
        printf("Open data basename success\n");  
    }  
    return 1;
}

int heartbeat(int device_id, char *real_id, char *name, char *val, int flag) 
{    
    int ret;
    char cmd[256];
    memset(cmd, 0, sizeof(cmd));

    // 查询数据库中表中的内容
    sprintf(cmd, "INSERT INTO %s (device_id, real_id, name, val, update_time, flag) VALUES (%d, '%s', '%s', '%s', getdate(), %d)", tableName, device_id, real_id, name, val, flag); 

    if (dbcmd(dbprocess, cmd) == FAIL) {
        printf("dbcmd....\n");
        return 0;
    }

	// 执行命令
    if(dbsqlexec(dbprocess) == FAIL){  
        ret = 0;
    //    printf("heartbeat error\n");  
    }  
    else {
        ret = 1;
    //    printf("heartbeat ok\n");  
    }
  
    return ret;  
}

// 插入一下数据到sqlserver中
int insertInto(int device_id, char *real_id, char *name, char *val, long timestamp, int flag) 
{    
    int ret;
    char cmd[256];
    memset(cmd, 0, sizeof(cmd));

    // 查询数据库中表中的内容
    // 时间传进来的是时间戳，需要转换成datetime类型
    sprintf(cmd, "INSERT INTO %s (device_id, real_id, name, val, update_time, flag) VALUES (%d, '%s', '%s', '%s', DATEADD(s, %d + 28800, '1970-01-01 00:00:00'), %d)", tableName, device_id, real_id, name, val, timestamp, flag);  

    dbcmd(dbprocess, cmd);

	// 执行命令
    if(dbsqlexec(dbprocess) == FAIL){  
        ret = 0;
        printf("insert sqlserver table error\n");  
    }  
    else {
        ret = 1;
    }
  
    return ret;  
}

// 关闭数据库
void closeSqlserver()
{
    dbclose(dbprocess); 
}
