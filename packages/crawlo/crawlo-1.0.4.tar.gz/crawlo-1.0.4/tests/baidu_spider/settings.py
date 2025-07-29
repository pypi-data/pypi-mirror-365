#!/usr/bin/python
# -*- coding:UTF-8 -*-

PROJECT_NAME = 'baidu_spider'

CONCURRENCY = 4

USE_SESSION = True

# 下载延迟
DOWNLOAD_DELAY = 0.5
RANDOMNESS = False

# --------------------------------------------------- 公共MySQL配置 -----------------------------------------------------
MYSQL_HOST = '43.139.14.225'
MYSQL_PORT = 3306
MYSQL_USER = 'picker'
MYSQL_PASSWORD = 'kmcNbbz6TbSihttZ'
MYSQL_DB = 'stock_pro'
MYSQL_TABLE = 'articles'  # 可选，默认使用spider名称
MYSQL_BATCH_SIZE = 500

# asyncmy专属配置
MYSQL_POOL_MIN = 5  # 连接池最小连接数
MYSQL_POOL_MAX = 20  # 连接池最大连接数

# 选择下载器
# DOWNLOADER = "crawlo.downloader.httpx_downloader.HttpXDownloader"

MIDDLEWARES = [
    'crawlo.middleware.download_delay.DownloadDelayMiddleware',
    'crawlo.middleware.default_header.DefaultHeaderMiddleware',
    'crawlo.middleware.response_filter.ResponseFilterMiddleware',
    'crawlo.middleware.retry.RetryMiddleware',
    'crawlo.middleware.response_code.ResponseCodeMiddleware',
    'crawlo.middleware.request_ignore.RequestIgnoreMiddleware',
    # 'baidu_spider.middleware.TestMiddleWare',
    # 'baidu_spider.middleware.TestMiddleWare2'
]

EXTENSIONS = [
    'crawlo.extension.log_interval.LogIntervalExtension',
    'crawlo.extension.log_stats.LogStats',
]

PIPELINES = [
    'crawlo.pipelines.console_pipeline.ConsolePipeline',
    'crawlo.pipelines.mysql_pipeline.AsyncmyMySQLPipeline',  # 或 AiomysqlMySQLPipeline
    # 'crawlo.pipelines.mysql_batch_pipline.AsyncmyMySQLPipeline',  # 或 AiomysqlMySQLPipeline
    # 'baidu_spider.pipeline.TestPipeline',
    # 'baidu_spider.pipeline.MongoPipeline',
]

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
DEFAULT_HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    # "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}

# --------------------------------------DB ---------------------------------------------
Mongo_Params = ''
MONGODB_DB = 'news'

REDIS_TTL = 0
CLEANUP_FP = False

FILTER_CLASS = 'crawlo.filters.aioredis_filter.AioRedisFilter'
# FILTER_CLASS = 'crawlo.filters.redis_filter.RedisFilter'
# FILTER_CLASS = 'crawlo.filters.memory_filter.MemoryFileFilter'
