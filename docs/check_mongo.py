import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

async def check():
    client = AsyncIOMotorClient(os.getenv('MONGO_URI'))
    db = client['ai_detection_db']

    results_count = await db['detection_results'].count_documents({})
    logs_count    = await db['system_logs'].count_documents({})
    users_count   = await db['users'].count_documents({})

    print(f"Users            : {users_count}")
    print(f"Detection Results: {results_count}")
    print(f"System Logs      : {logs_count}")

    latest_result = await db['detection_results'].find_one(sort=[('timestamp', -1)])
    latest_log    = await db['system_logs'].find_one(sort=[('timestamp', -1)])

    if latest_result:
        r = latest_result['result']
        t = latest_result['input_type']
        c = latest_result['confidence']
        print(f"Latest result    : {r} ({t}) conf={c}")

    if latest_log:
        m  = latest_log['method']
        ep = latest_log['endpoint']
        sc = latest_log['status_code']
        ms = latest_log['processing_time_ms']
        print(f"Latest log       : {m} {ep} -> {sc} ({ms}ms)")

asyncio.run(check())
