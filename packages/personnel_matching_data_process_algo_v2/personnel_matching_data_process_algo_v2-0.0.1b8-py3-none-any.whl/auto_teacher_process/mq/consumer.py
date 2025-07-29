import asyncio
import json
import logging
from collections.abc import Callable
from typing import Any

import aio_pika
import redis.asyncio as redis

from auto_teacher_process.logger import setup_logger
from auto_teacher_process.config import Config

from .sender import send_messages

logger = setup_logger(system="mq", stage="consumer")


class RedisAggregator:
    def __init__(self, redis_url, sources):
        self.redis_url = redis_url
        self.sources = set(sources)
        self.redis = None

    async def setup(self):
        if not self.redis:
            self.redis = await redis.from_url(self.redis_url, decode_responses=True)

    async def aggregate(self, source, task_id, body):
        await self.setup()
        key = f"agg:{task_id}"
        logger.info(f"Aggregating {source} for {task_id}")
        await self.redis.hset(key, source, json.dumps(body))
        await self.redis.expire(key, 86400)  # 1 day
        fields = await self.redis.hkeys(key)
        if set(fields) == self.sources:
            all_msgs = await self.redis.hgetall(key)
            await self.redis.delete(key)
            return [json.loads(all_msgs[src]) for src in self.sources]
        return None


def start_consumer(
    listen_queues: list[str],
    send_queues: list[str],
):
    use_redis_agg = len(listen_queues) > 1
    aggregator = None
    if use_redis_agg:
        aggregator = RedisAggregator(redis_url=Config.MQ.AGGREGATOR_URL, sources=listen_queues)

    def decorator(main: Callable[[list[Any]], Any | list[Any]]):
        async def wrapper():
            connection = await aio_pika.connect_robust(Config.MQ.CONNECTION_URL)
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=10)

            for idx, queue_name in enumerate(listen_queues):
                queue = await channel.declare_queue(queue_name, durable=True)

                async def handler(msg: aio_pika.IncomingMessage, qidx=idx, queue_name=queue_name):
                    async with msg.process():
                        try:
                            body = json.loads(msg.body.decode())
                        except Exception as e:
                            logger.error(f"Failed to decode message from {queue_name}: {e}")
                            return

                        task_id = body.get("task_id")
                        if not task_id:
                            logger.warning(f"Missing task_id in message from {queue_name}")
                            return

                        if use_redis_agg:
                            # 用Redis聚合
                            agg_result = await aggregator.aggregate(queue_name, task_id, body)
                            if agg_result is None:
                                return
                            messages = agg_result
                        else:
                            # 单队列，直接处理
                            messages = [body]
                        try:
                            result = await main(messages)
                            if result is None:
                                return
                            results = result if isinstance(result, list) else [result]

                            if len(results) != len(send_queues):
                                logger.warning(f"Expected {len(send_queues)} outputs, got {len(results)}")
                                return

                            outbound = [
                                {"queue_name": send_queues[i], "message": results[i]} for i in range(len(results))
                            ]
                            await send_messages(outbound, channel)

                        except Exception as e:
                            logger.exception(f"Exception in main: {e}")

                await queue.consume(handler)
                logger.info(f"Consuming from queue: {queue_name}")

            logger.info("All consumers started.")
            await asyncio.Future()

        def run_main():
            try:
                asyncio.run(wrapper())
            except KeyboardInterrupt:
                logger.info("Consumer stopped by user.")

        run_main()
        return main

    return decorator
