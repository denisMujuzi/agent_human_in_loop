url = "" 

import asyncio
import aiohttp
import time

async def hit_endpoint(session, url, request_id):
    try:
        start_time = time.perf_counter()  # Start timing
        async with session.get(url) as response:
            elapsed = time.perf_counter() - start_time
            print(f"Request ID: {request_id}, Status: {response.status}, Time: {elapsed:.2f}s")
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        print(f"Request ID: {request_id}, Request failed after {elapsed:.2f}s: {e}")

async def main():
    url = f"{url}/threads/256700000000"

    async with aiohttp.ClientSession() as session:
        tasks = [
            hit_endpoint(session, url, request_id=i)
            for i in range(10)  # 200 concurrent GET requests
        ]
        await asyncio.gather(*tasks)

asyncio.run(main())


# import asyncio
# import aiohttp
# import time

# async def hit_endpoint(session, url, data, thread_id):
#     try:
#         # Update thread_id for this request
#         data["thread_id"] = str(thread_id)
#         start_time = time.perf_counter()
#         async with session.post(url, data=data) as response:  # form-encoded
#             elapsed = time.perf_counter() - start_time
#             print(f"Thread ID: {thread_id}, Status: {response.status}, Time: {elapsed:.2f}s")
#     except Exception as e:
#         elapsed = time.perf_counter() - start_time
#         print(f"Thread ID: {thread_id}, Request failed after {elapsed:.2f}s: {e}")

# async def main():
#     url = f"{url}/ai-query"

#     # Base POST data
#     base_data = {
#         "farmer_phone_number": "256700000000",
#         "farmer_name": "Denis Mujuzi",
#         "farmer_location": "Kampala",
#         "agent_mode": "chat",
#         "app": "farmer",
#         "question": "My crop leaves are yellowing, what should I do?",
#     }

#     async with aiohttp.ClientSession() as session:
#         # Unique thread_id per request
#         tasks = [
#             hit_endpoint(session, url, base_data.copy(), thread_id=3000+i)
#             for i in range(5)  # number of concurrent requests
#         ]
#         await asyncio.gather(*tasks)

# asyncio.run(main())