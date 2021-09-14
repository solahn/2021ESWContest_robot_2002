from Sensor.ImageProcessor import ImageProcessor
from Sensor.LineDetector import LineDetector
from Sensor.EdgeDetector import EdgeDetector
from Actuator.Motion import Motion
from Sensor.ColorChecker import get_pixel_rate4green
import numpy as np
import cv2
import time
import sys

class Robot:

    def __init__(self, video_path =""):
        self._motion = Motion()
        self._image_processor = ImageProcessor(video_path=video_path)
        self._line_detector = LineDetector()
        self._edge_detector = EdgeDetector()
        self.direction = None
        self.mode = None # motion Mode

    def detect_alphabet(self):
        self._motion.set_head('DOWN', 75)
        flag = True
        alphabet = None
        while alphabet is None:
            alphabet = self._image_processor.get_door_alphabet()
            
            if alphabet is not None:
                break

            if flag:
                self._motion.walk("RIGHT")
            else:
                self._motion.walk("LEFT")
        
            flag = not flag
        self._motion.notice_direction(dir=alphabet)

    def set_mode(self, src):
        line_info = self._image_processor.get_lines()
        if line_info["DEGREE"] == 0 # line 하나도 없을 때.
            self.mode = "find_line"

        elif self.mode == "find_line" and ine_info["DEGREE"] != 0:
            self.mode = "find_edge"

        elif line_info["V"] == True and line_info["H"] == False:
            if 300 < line_info["VPOS"] <340:
                self.mode = "walk_foward"
            else:
                if line_info["VPOS"] < 300:
                    self.mode = "walk_left"
                elif line_info["VPOS"] > 340:
                    self.mode = "walk_right"

        elif not line_info["V"] and not line_info["H"]:
            if line_info["DEGREE"] < 85:
self.mode = "modify_angle_left"
            elif line_info["DEGREE"] > 95:
                print('MODIFY angle --RIGHT', line_info)
                self._motion.turn(dir='RIGHT', loop=1)

        else:
            if line_info["HPOS"] > 200: 
                if line_info["H_MIN_X"] < 50 and line_info["H_MAX_X"] < 340:
                    print('┒', line_info)
                    if self.direction == 'LEFT':
                        print(self.direction, "모드여서 좌회전 안하고 직진합니다.")
                        self._motion.walk(dir='FORWARD', loop=4)
                        #self.count += 1
                    elif self.direction == 'RIGHT':
                        self._motion.turn('LEFT', loop=8)
                    else:
                        print("화살표 인식 전입니다.")

                elif line_info["H_MIN_X"] > 300 and line_info["H_MAX_X"]>600:
                    print('┎', line_info)
                    if self.direction == 'LEFT':
                        self._motion.turn('RIGHT', loop=8)
                    elif self.direction == 'RIGHT':
                        print(self.direction, "모드여서 우회전 안하고 직진합니다.")
                        self._motion.walk(dir='FORWARD', loop=4)
                        #self.count += 1
                    else:
                        print("화살표 인식 전입니다.")
                        
                else:
                    print('T', line_info)
                    self._motion.set_head("DOWN", 100)
                    self.direction = self._image_processor.get_arrow_direction()
                    print('MODE::', self.direction)
                    time.sleep(0.1)
                    while self.direction == None:
                        self._motion.walk("BACKWARD", 1)
                        self.direction = self._image_processor.get_arrow_direction()
                        print('MODE::', self.direction)
                        time.sleep(0.1)
                    self._motion.set_head('DOWN', 10)
                    self._motion.walk('FORWARD', 2)
                    self._motion.walk(self.direction, 4)
                    self._motion.turn(self.direction, 8)
            else:
                self._motion.walk('FORWARD')
                print('low then 150')





        # return: 직선 보이면 True, 안보이면 False 전달


    def line_tracing(self):
        self._motion.set_head('DOWN', 30)
        while True:
            src = self._image_processor.get_image(visualization=False)
            src = cv2.resize(src, dsize=(640,480))
            line_info, result_img = self._line_detector.get_all_lines(src)
            cv2.imshow('src', result_img)
            cv2.waitKey(1)
            
            if line_info["V"] and not line_info["H"]:
                if 300 < line_info["VPOS"] <340:
                    print('FORWARD', line_info)
                    self._motion.walk(dir='FORWARD', loop=1)
                else:
                    if line_info["VPOS"] < 300:
                        print('MODIFY walk --LEFT', line_info)
                        self._motion.walk(dir='LEFT', loop=1)
                    elif line_info["VPOS"] > 340:
                        print('MODIFY walk --RIGHT', line_info)
                        self._motion.walk(dir='RIGHT', loop=1)

            elif not line_info["V"] and not line_info["H"]:
                if line_info["DEGREE"] < 85:
                    print('MODIFY angle --LEFT', line_info)
                    self._motion.turn(dir='LEFT', loop=1)
                elif line_info["DEGREE"] > 95:
                    print('MODIFY angle --RIGHT', line_info)
                    self._motion.turn(dir='RIGHT', loop=1)

            else:
                if line_info["HPOS"] > 200: 
                    if line_info["H_MIN_X"] < 50 and line_info["H_MAX_X"] < 340:
                        print('┒', line_info)
                        if self.direction == 'LEFT':
                            print(self.direction, "모드여서 좌회전 안하고 직진합니다.")
                            self._motion.walk(dir='FORWARD', loop=4)
                            #self.count += 1
                        elif self.direction == 'RIGHT':
                            self._motion.turn('LEFT', loop=8)
                        else:
                            print("화살표 인식 전입니다.")

                    elif line_info["H_MIN_X"] > 300 and line_info["H_MAX_X"]>600:
                        print('┎', line_info)
                        if self.direction == 'LEFT':
                            self._motion.turn('RIGHT', loop=8)
                        elif self.direction == 'RIGHT':
                            print(self.direction, "모드여서 우회전 안하고 직진합니다.")
                            self._motion.walk(dir='FORWARD', loop=4)
                            #self.count += 1
                        else:
                            print("화살표 인식 전입니다.")
                        
                    else:
                        print('T', line_info)
                        self._motion.set_head("DOWN", 100)
                        self.direction = self._image_processor.get_arrow_direction()
                        print('MODE::', self.direction)
                        time.sleep(0.1)
                        while self.direction == None:
                            self._motion.walk("BACKWARD", 1)
                            self.direction = self._image_processor.get_arrow_direction()
                            print('MODE::', self.direction)
                            time.sleep(0.1)
                        self._motion.set_head('DOWN', 10)
                        self._motion.walk('FORWARD', 2)
                        self._motion.walk(self.direction, 4)
                        self._motion.turn(self.direction, 8)
                else:
                    self._motion.walk('FORWARD')
                    print(ans[4], 'try ┃ until upper then 150')


    def return_line(self, direction):
        # + 고개를 든다 (고개 각도도 보면서 정해야할 듯)
        self._motion.set_head('UP')
        # edge를 찾는다 ans:: ans[0] edge를 찾았으면 not None 없으면 None,ans[1] edge_line 갯수,ans[2] edge_line의 y좌표,ans[3] 수직선 찾으면 not None 못찾으면 None
        while True:
            src = self._image_processor.get_image(visualization=False)
            src = cv2.resize(src, dsize=(640,480))
            ans, result_img = self._edge_detector.find_edge(src)
            cv2.imshow('result_img', result_img)
            cv2.waitKey(1)

            if ans[1]<6:
                self.mode = 'find_edge'
            else:
                if ans[2] < 150:
                    self.mode = 'find_edge_closer'


            if self.mode == 'find_edge_closer' and ans[2] < 150:
                    self.mode = 'find_edge_closer'
            elif self.mode == 'find_edge_closer' and ans[2] > 150:
                if self.mode == 'find_edge_closer' and ans[3] is None:
                    self.mode = 'find_vertical'

            if self.mode = 'find_vertical' and ans[3] is not None:
                self.line_tracing()


            print(self.mode)
            
            # edge_line이 5개 이상 검출될 때까지 몸을 회전시킨다
            if self.mode='find_edge':
                self._motion.turn(dir='LEFT')          
            elif self.mode = 'find_edge_closer':
                self._motion.walk(dir='FORWARD')
            elif self.mode = 'find_vertical':
                self._motion.turn(dir=direction)


        # 검출되면? 검출된 edge line이 로봇 발 앞에 올때까지 걷는다. (판단은 edge line의 y좌표가 일정 범위 안에 들어올 때까지) --> 많이 멀면 넓게 걷고, 가까우면 보통으로 걷는다.

        # answer[4]: 직선이 보이나? 직선 보일 때까지 direction따라 회전



    def recognize_area_color(self):
        self._motion.set_head(self.direction, 45)
        self._motion.set_head('DOWN', 60)
        time.sleep(1)
        color = self._image_processor.get_area_color()
        self._motion.notice_area(area=color)
        self._motion.set_head("UPDOWN_CENTER")
        self._motion.set_head("LEFTRIGHT_CENTER")
        return
        