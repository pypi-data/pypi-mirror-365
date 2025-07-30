# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import os
import logging
import json
import pymysql
logger = logging.getLogger('mcp')
settings = {
    'log_level': 'INFO'
}
# 初始化mcp服务
mcp = FastMCP('pg-db-operation-mcp-server', log_level='INFO', settings=settings)

pg_conn = None

def init_pg_conn(host, port, user, password, dbname):
    global pg_conn
    try:
        if pg_conn is None:
            pg_conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=dbname
            )

            logger.info("创建mysql链接成功")
    except Exception as e:
        logger.error(e)

@mcp.tool(name='创建表', description='执行传入的创建表sql')
def create_table(create_table_sql:str = Field(description='创建表sql语句')) -> str:
    table_dict = {}
    global pg_conn
    init_pg_conn(os.getenv("MYSQL_HOST"), os.getenv("MYSQL_PORT"), os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD"), os.getenv("MYSQL_DBNAME"))
    cursor = pg_conn.cursor()
    
    logger.info("执行创建表sql" + create_table_sql)
    cursor.execute(create_table_sql)
    pg_conn.commit()
    return "创建成功"


@mcp.tool(name='执行sql查询', description='执行查询语句')
def query_table(query_sql:str = Field(description='查询sql语句')) -> str:
    init_pg_conn(os.getenv("MYSQL_HOST"), os.getenv("MYSQL_PORT"), os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD"),
                 os.getenv("MYSQL_DBNAME"))
    cursor = pg_conn.cursor()
    
    cursor.execute(query_sql)
    columns = [col[0] for col in cursor.description]  # 获取列名
    rows = cursor.fetchall()
    data = []
    for row in rows:
        data.append(dict(zip(columns, row)))
    return json.dumps(data,ensure_ascii=False)

@mcp.tool(name='执行sql更新', description='执行更新语句')
def update_table(update_sql:str = Field(description='更新sql语句')) -> str:
    init_pg_conn(os.getenv("MYSQL_HOST"), os.getenv("MYSQL_PORT"), os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD"),os.getenv("MYSQL_DBNAME"))
    cursor = pg_conn.cursor()
    
    logger.info("执行sql更新" + update_sql)
    cursor.execute(update_sql)
    pg_conn.commit()
    return "更新成功"

@mcp.tool(name='执行sql删除', description='执行删除语句')
def delete_table(delete_sql:str = Field(description='删除sql语句')) -> str:
    init_pg_conn(os.getenv("MYSQL_HOST"), os.getenv("MYSQL_PORT"), os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD"),os.getenv("MYSQL_DBNAME"))
    cursor = pg_conn.cursor()
    
    logger.info("执行sql删除" + delete_sql)
    cursor.execute(delete_sql)
    pg_conn.commit()
    return "删除成功"

def run():
    mcp.run(transport='stdio')

if __name__ == '__main__':
    init_pg_conn(os.getenv("MYSQL_HOST"), os.getenv("MYSQL_PORT"), os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD"), os.getenv("MYSQL_DBNAME"))
    run()
