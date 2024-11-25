import time, cv2, asyncio




async def get_topcam_id():
    
    # ArUco 마커 사전 및 파라미터 초기화
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    parameters = cv2.aruco.DetectorParameters()
    cap = cv2.VideoCapture(0)
    # 감지할 마커 ID와 타이머 초기화
    target_marker_ids = {0, 5, 7}
    marker_lost_times = {marker_id: None for marker_id in target_marker_ids}
    timeout_duration = 3  # 감지 안 된 상태를 확인할 시간 (초)
    while cap.isOpened():
        ret, frame = await asyncio.to_thread(cap.read)
        if not ret:
            break
        # Grayscale 변환
        gray = await asyncio.to_thread(cv2.cvtColor, frame, cv2.COLOR_BGR2GRAY)
        # ArUco 마커 감지
        def detect_markers():
            return cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        corners, ids, _ = await asyncio.to_thread(detect_markers)
        detected_ids = set(ids.flatten()) if ids is not None else set()
        # 감지되지 않은 마커 처리
        for marker_id in target_marker_ids:
            if marker_id in detected_ids:
                # 마커가 감지되면 타이머 초기화
                marker_lost_times[marker_id] = None
            else:
                # 마커가 감지되지 않으면 타이머 시작
                if marker_lost_times[marker_id] is None:
                    marker_lost_times[marker_id] = time.time()  # 사라진 시간 기록
                elif time.time() - marker_lost_times[marker_id] > timeout_duration:
                    # 타임아웃 경과 시 ID 출력
                    print(f"Marker ID {marker_id} not detected!")
                    # 실행 완료 후 타이머 초기화
                    marker_lost_times[marker_id] = None
        
        # 'q' 키를 누르면 종료
        cv2.imshow("ArUco Marker Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    # 자원 정리
    cap.release()
    cv2.destroyAllWindows()
    
    
if __name__ == "__main__":
    asyncio.run(get_topcam_id())
