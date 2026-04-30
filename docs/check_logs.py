"""
Task 7.6 — Check SystemLogs collection in MongoDB Atlas
Confirms all requests are logged with correct status codes and processing times.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import os, asyncio
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend', '.env'))

async def check_logs():
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db     = client["ai_detection_db"]

    total  = await db["system_logs"].count_documents({})
    ok_2xx = await db["system_logs"].count_documents({"status_code": {"$gte": 200, "$lt": 300}})
    err_4xx = await db["system_logs"].count_documents({"status_code": {"$gte": 400, "$lt": 500}})
    err_5xx = await db["system_logs"].count_documents({"status_code": {"$gte": 500}})

    # Timing stats
    pipeline = [
        {"$group": {
            "_id": None,
            "avg_ms": {"$avg": "$processing_time_ms"},
            "max_ms": {"$max": "$processing_time_ms"},
            "min_ms": {"$min": "$processing_time_ms"},
        }}
    ]
    stats_cursor = db["system_logs"].aggregate(pipeline)
    stats = await stats_cursor.to_list(length=1)

    # Latest 10 logs
    cursor = db["system_logs"].find().sort("timestamp", -1).limit(10)
    recent = await cursor.to_list(length=10)

    print("=" * 60)
    print("  TASK 7.6 — SYSTEM LOGS VERIFICATION")
    print("=" * 60)
    print(f"\n  Total log entries : {total}")
    print(f"  2xx Success       : {ok_2xx}")
    print(f"  4xx Client errors : {err_4xx}")
    print(f"  5xx Server errors : {err_5xx}")

    if stats:
        s = stats[0]
        print(f"\n  Processing times:")
        print(f"    Avg : {s['avg_ms']:.1f} ms")
        print(f"    Max : {s['max_ms']:.1f} ms")
        print(f"    Min : {s['min_ms']:.1f} ms")

    print(f"\n  Latest 10 requests:")
    print(f"  {'Method':<8} {'Endpoint':<28} {'Status':>6} {'ms':>8}")
    print(f"  {'-'*8} {'-'*28} {'-'*6} {'-'*8}")
    for log in recent:
        m   = log.get("method", "?")
        ep  = log.get("endpoint", "?")[:27]
        sc  = log.get("status_code", "?")
        ms  = log.get("processing_time_ms", "?")
        print(f"  {m:<8} {ep:<28} {sc:>6} {ms:>7.1f}ms")

    all_ok = total > 0 and err_5xx == 0
    print(f"\n  Status: {'PASS - All requests logged correctly' if all_ok else 'ISSUES FOUND'}")
    print("=" * 60)

asyncio.run(check_logs())
