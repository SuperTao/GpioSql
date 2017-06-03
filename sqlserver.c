#include <stdio.h>  
#include <string.h>  
#include <stdlib.h>  
#include <unistd.h>  
#include <sybfront.h>  
#include <sybdb.h>  

DBPROCESS *dbprocess;

int openSqlserver()
{
    int ret;
    char szUsername[32]= "wangzg";  
    char szPassword[32]= "Wangzg123456";  
    char szDBName[32]= "wangzg";  
    char szServer[32]= "115.29.245.156:40949";  
    char szTable[32]= "real_date_log";  

    //初始化db-library  
    printf("dbinin--------\n");
    dbinit();  
    //连接数据库  
    printf("dblogin---------\n");
    LOGINREC *loginrec=dblogin();  
    //连接数据库  
	// 设置登录的用户名
    printf("username---------\n");
    DBSETLUSER(loginrec,szUsername);  
	// 设置登录密码
    printf("password---------\n");
    DBSETLPWD(loginrec,szPassword);  
	// 连接sqlserver服务器地址和端口号,这里才是连接
    printf("open---------\n");
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

int insertInto(int device_id, char *real_id, char *name, char *val, long timestamp, int flag)  
//int insertInto(int device_id, char *real_id, int id_len, char *name, int name_len, char *val, int val_len, int flag)  
{    
    int ret;
    char cmd[256];
    memset(cmd, 0, sizeof(cmd));

//    printf("time: %ld\n", timestamp);
//    printf("device_id: %d\n", device_id);
//    printf("real_id: %s\n", real_id);
//    printf("name: %s\n", name);
//    printf("val: %s\n", val);
//    printf("flag: %d\n", flag);
    // 查询数据库中表中的内容
    sprintf(cmd, "INSERT INTO real_date_log (device_id, real_id, name, val, update_time, flag) VALUES (%d, '%s', '%s', '%s', DATEADD(s, %d + 28800, '1970-01-01 00:00:00'), %d)", device_id, real_id, name, val, timestamp, flag);  
//    printf("cmd:%s\n", cmd);
    dbcmd(dbprocess, cmd);

	// 执行命令
    if(dbsqlexec(dbprocess) == FAIL){  
        ret = 0;
        printf("Query table error\n");  
    }  
    else {
        ret = 1;
        printf("Query table success\n");  
    }
  
    return ret;  
}

void closeSqlserver()
{
    dbclose(dbprocess);  
}
