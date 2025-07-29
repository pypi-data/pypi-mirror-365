#!/usr/bin/python
# -*- coding:UTF-8 -*-
from typing import Optional
import aioredis
from crawlo import Request
from crawlo.filters import BaseFilter
from crawlo.utils.log import get_logger
from crawlo.utils.request import request_fingerprint


class AioRedisFilter(BaseFilter):
    """使用Redis集合实现的异步请求去重过滤器（适用于分布式爬虫）"""

    def __init__(
            self,
            redis_key: str,
            client: aioredis.Redis,
            stats: dict,
            debug: bool,
            log_level: str,
            cleanup_fp: bool = False
    ):
        """初始化过滤器"""
        self.logger = get_logger(self.__class__.__name__, log_level)
        super().__init__(self.logger, stats, debug)

        self.redis_key = redis_key
        self.redis = client
        self.cleanup_fp = cleanup_fp

    @classmethod
    def create_instance(cls, crawler) -> 'BaseFilter':
        """从爬虫配置创建过滤器实例"""
        redis_url = crawler.settings.get('REDIS_URL', 'redis://localhost:6379')
        decode_responses = crawler.settings.get_bool('DECODE_RESPONSES', False)  # 关键：改为False

        try:
            redis_client = aioredis.from_url(
                redis_url,
                decode_responses=decode_responses,
                max_connections=20,
                encoding='utf-8'
            )
        except Exception as e:
            raise RuntimeError(f"Redis连接失败 {redis_url}: {str(e)}")

        return cls(
            redis_key=f"{crawler.settings.get('PROJECT_NAME', 'default')}:{crawler.settings.get('REDIS_KEY', 'request_fingerprints')}",
            client=redis_client,
            stats=crawler.stats,
            cleanup_fp=crawler.settings.get_bool('CLEANUP_FP', False),
            debug=crawler.settings.get_bool('FILTER_DEBUG', False),
            log_level=crawler.settings.get('LOG_LEVEL', 'INFO')
        )

    async def requested(self, request: Request) -> bool:
        """
        检查请求是否重复
        """
        try:
            fp = request_fingerprint(request)
            self.logger.debug(f"Checking fingerprint: {fp}")

            # 确保fp是字符串类型
            if not isinstance(fp, str):
                fp = str(fp)

            # 检查Redis连接状态
            if not self.redis:
                raise RuntimeError("Redis client is not initialized")

            # 检查指纹是否已存在
            is_member = await self.redis.sismember(self.redis_key, fp)
            self.logger.debug(f"Fingerprint {fp} exists: {is_member}")

            if is_member:
                if self.debug:
                    self.logger.debug(f"Filtered duplicate request: {fp}")
                return True

            # 添加新指纹
            result = await self.redis.sadd(self.redis_key, fp)

            if self.debug:
                if result == 1:
                    self.logger.debug(f"Added new fingerprint: {fp}")
                else:
                    self.logger.warning(f"Failed to add fingerprint: {fp}")

            return False

        except Exception as e:
            self.logger.error(f"Filter check failed for {getattr(request, 'url', 'unknown')}: {str(e)}")
            # 可以选择抛出异常或返回False（不过滤）
            raise

    async def add_fingerprint(self, fp: str) -> bool:
        """向Redis集合添加新指纹"""
        try:
            if not isinstance(fp, str):
                fp = str(fp)

            result = await self.redis.sadd(self.redis_key, fp)
            if self.debug:
                self.logger.debug(f"Added fingerprint {fp}, result: {result}")
            return result == 1
        except Exception as e:
            self.logger.error(f"Failed to add fingerprint {fp}: {str(e)}")
            raise

    async def get_stats(self) -> dict:
        """获取当前过滤器统计信息"""
        try:
            count = await self.redis.scard(self.redis_key)
            return {
                'total_fingerprints': count,
                'redis_key': self.redis_key,
                **self.stats
            }
        except Exception as e:
            self.logger.error(f"Failed to get stats: {str(e)}")
            return self.stats

    async def clear_all(self) -> int:
        """清空所有指纹数据"""
        try:
            deleted = await self.redis.delete(self.redis_key)
            self.logger.info(f"Cleared {deleted} keys")
            return deleted
        except Exception as e:
            self.logger.error(f"Failed to clear fingerprints: {str(e)}")
            raise

    async def closed(self, reason: Optional[str] = None) -> None:
        """爬虫关闭时的处理"""
        try:
            if self.cleanup_fp:
                deleted = await self.redis.delete(self.redis_key)
                self.logger.info(
                    f"Cleaned {deleted} fingerprints from {self.redis_key} "
                    f"(reason: {reason or 'manual'})"
                )
            else:
                # 显示统计信息
                count = await self.redis.scard(self.redis_key)
                self.logger.info(f"Total fingerprints preserved: {count}")
        except Exception as e:
            self.logger.warning(f"Close operation failed: {e}")
        finally:
            await self._close_redis()

    async def _close_redis(self) -> None:
        """安全关闭Redis连接"""
        try:
            if hasattr(self.redis, 'close'):
                await self.redis.close()
        except Exception as e:
            self.logger.warning(f"Redis close error: {e}")