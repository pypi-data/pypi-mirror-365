import asyncio
import json
import socket
import os
import time
import base64
from enum import Enum
from typing import Any, Optional, Dict
from pyolive.status import JobStatus
from pyolive.job_context import JobContext
from .adapter import Adapter


class ProducerChannel:
    def __init__(self, logger: Any, namespace: str, alias: str, devel: bool = False):
        self.logger = logger
        self.namespace = namespace
        self.alias = alias
        self.hostname = socket.gethostname()
        self.adapter = Adapter(logger)
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.devel = devel

    async def start(self):
        if self.devel:
            self.running = True
            return

        if not await self.adapter.open():
            self.logger.error("ProducerChannel: Failed to open adapter")
            return

        self.running = True
        self._task = asyncio.create_task(self._run_loop())
        self.logger.info("ProducerChannel: Started")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.adapter.close()
        self.logger.info("ProducerChannel: Stopped")

    async def _run_loop(self):
        while self.running:
            try:
                item = await self.queue.get()
                await self.adapter.publish(item["exchange"], item["routing_key"], item["body"])
            except Exception as e:
                self.logger.error("ProducerChannel: Publish failed - %s", e)
            await asyncio.sleep(0.001)

    async def publish_heartbeat(self, worker_name: str):
        data = {
            'metric_type': 4,
            'metric_status': 0,
            'metric_name': self.alias,
            'namespace': self.namespace,
            'process': worker_name,
            'psn': 0,
            'hostname': self.hostname,
            'timestamp': time.time()
        }
        rk = f'sys.{self.namespace}.heartbeat.agent'
        await self._enqueue(Adapter.EXCHANGE_METRIC, rk, json.dumps(data))

    async def publish_job(self, ctx: JobContext):
        if not ctx.msglist:
            ctx.msgbox = {"type": "ascii", "size": 0, "data": ""}
            await self._nextjob(ctx, self._build_data(ctx))
            return

        for msg in ctx.msglist.copy():
            if isinstance(msg, bytes):
                # binary 메시지 → base64 인코딩
                encoded = base64.b64encode(msg).decode('ascii')
                ctx.msgbox = {
                    "type": "binary",
                    "size": len(msg),
                    "data": encoded
                }
            elif isinstance(msg, str):
                msg_bytes = msg.encode('utf-8')
                ctx.msgbox = {
                    "type": "ascii",
                    "size": len(msg_bytes),
                    "data": msg
                }
            else:
                # fallback: 문자열로 강제 변환
                msg_str = str(msg)
                msg_bytes = msg_str.encode('utf-8')
                ctx.msgbox = {
                    "type": "ascii",
                    "size": len(msg_bytes),
                    "data": msg_str
                }

            await self._nextjob(ctx, self._build_data(ctx))

    def _build_data(self, ctx: JobContext) -> Dict[str, Any]:
        return {
            'regkey': ctx.regkey,
            'topic': ctx.topic,
            'action_id': ctx.action_id,
            'action_ns': ctx.action_ns,
            'action_app': ctx.action_app,
            'action_params': ctx.action_params,
            'job_id': ctx.job_id,
            'job_hostname': ctx.job_hostname,
            'job_seq': ctx.job_seq,
            'timestamp': ctx.timestamp,
            'filenames': ctx.filenames,
            'msgbox': ctx.msgbox,
        }

    async def _nextjob(self, ctx: JobContext, data: Dict[str, Any]):
        key = f'job.des.msm.early.{ctx.topic}' if ctx.timestamp == 0 else f'job.des.msm.now.{ctx.topic}'
        await self._enqueue(Adapter.EXCHANGE_ACTION, key, json.dumps(data))

    async def publish_notify(self, ctx: JobContext, text: str = '', status: Enum = JobStatus.RUNNING, elapsed: int = 0):
        job_status_value = status.value if isinstance(status, Enum) else int(status)
        data = {
            'job_id': ctx.job_id,
            'job_status': job_status_value,
            'job_elapsed': elapsed,
            'reg_subject': ctx.regkey.split('@')[0],
            'reg_version': ctx.regkey.split('@')[1],
            'reg_topic': ctx.topic,
            'action_id': ctx.action_id,
            'action_app': ctx.action_app,
            'action_ns': ctx.action_ns,
            'hostname': self.hostname,
            'timestamp': int(time.time()),
            'filesize': 0,
            'filenames': ctx.filenames,
            'err_code': 0,
            'err_mesg': text
        }

        for f in ctx.filenames:
            try:
                data['filesize'] += os.stat(f).st_size
            except Exception as e:
                self.logger.debug("ProducerChannel: Failed to stat file %s - %s", f, e)

        await self._enqueue(Adapter.EXCHANGE_LOGS, f'log.{ctx.action_ns}', json.dumps(data))

    async def _enqueue(self, exchange: str, routing_key: str, body: str):
        await self.queue.put({
            "exchange": exchange,
            "routing_key": routing_key,
            "body": body
        })