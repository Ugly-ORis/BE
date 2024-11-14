from utils.motion_Aris import ArisController
import time
import asyncio
controller = ArisController('192.168.1.167')
# 주문 응답을 처리하고 로봇 동작을 수행하는 비동기 함수
async def process_order_response_async(response_text):
    lines = response_text.strip().split("\n")
    last_line = lines[-1].strip()
    if "주문되었습니다." in last_line:
        for line in lines[:-1]:
            line = line.strip()
            print(f"Processed line: {line}")
            if "코코볼" in line:
                print("Detected: 코코볼")
                print("\n아이스크림 기계가 작동중입니다. 뒤로 물러나 주세요")
                await asyncio.to_thread(controller.move_to_initial_position)
                print("Moved to initial position")
                await asyncio.to_thread(controller.Pickup_Ice1)
                await asyncio.to_thread(controller.deliverIceCream)
                await asyncio.to_thread(controller.ToppingChoice, '1')
                await asyncio.to_thread(controller.ice1_Putback)
                print("아이스크림이 완료 되었습니다. 맛있게 드세요")
                await asyncio.to_thread(controller.pressEnd)
                print("감사합니다.")
########3########3########3########3########3########3########3########3########3########3########3########3########3
# import asyncio
# import time

# async def say_after(delay, what):
#     await asyncio.sleep(delay)
#     print(what)

# async def main():
#     task1 = asyncio.create_task(
#         say_after(1, 'hello'))

#     task2 = asyncio.create_task(
#         say_after(2, 'world'))

#     print(f"started at {time.strftime('%X')}")

#     # Wait until both tasks are completed (should take
#     # around 2 seconds.)
#     await task1
#     await task2

#     print(f"finished at {time.strftime('%X')}")
    
# if __name__=="__main__":
#     asyncio.run(main())
    
################################
