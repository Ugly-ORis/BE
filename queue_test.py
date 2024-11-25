import queue, time

# 큐 객체 생성

def test1(que:queue):    
    que = queue.Queue()
    que.put("안녕")
    que.put("하세요")
    que.put("반갑")
    que.put("습니다")
    
        
        
                
    
def test2(que:queue):

    que.get() 
    
    

if __name__ == "__main__":
    test1()
    
    
    
    
    # for i in range(4):
    #     if i == 0:
    #         print(que.get())
    #     if i == 1:
    #         print(que.get())
    #     if i == 2:
    #         print(que.get())
    #     if i == 3:
    #         print(que.get())