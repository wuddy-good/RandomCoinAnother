import datetime

from arq import ArqRedis


async def create_end_lottery_job(arqredis: ArqRedis, lottery_id: int, defer_until: datetime.datetime):
    await arqredis.enqueue_job(
        'end_lottery',
        # _job_id=f'end_lottery:{lottery_id}',
        _defer_until=defer_until,
        lottery_id=lottery_id
    )


async def create_channel_notification_job(arqredis: ArqRedis, text, lottery_id: int):
    await arqredis.enqueue_job(
        'new_lottery_notification',
        _defer_by=datetime.timedelta(minutes=5),
        text=text,
        lottery_id=lottery_id
    )
#
#
# async def create_start_new_lottery_job(arqredis: ArqRedis, lottery_id: int, defer_by: datetime.timedelta):
#     await arqredis.enqueue_job(
#         'create_lottery',
#         _job_id=f'create_lottery:{lottery_id}',
#         _defer_by=defer_by,
#         lottery_id=lottery_id
#     )
