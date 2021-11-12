from Brain.Robot import Robot
from Constant import Direction, AreaColor, LineColor, WalkInfo
from enum import Enum, auto
from collections import deque
import time
import numpy as np

class Mode(Enum):
    START = auto()
    DETECT_ALPHABET = auto()
    FIND_BOX = auto()
    TRACK_BOX = auto()
    TURN_TO_AREA = auto()
    DROP_BOX = auto()
    GO_TO_AREA = auto()
    FIND_YELLOW_LINE = auto()
    GO_OUT_AREA = auto()
    FIND_CONRER = auto()
    GO_TO_CORNER = auto()
    OUT_ROOM = auto()
    END = auto()

class BoxPos(Enum):
    RIGHT = auto()
    MIDDLE = auto()
    LEFT = auto()

def get_distance_from_baseline(pos: tuple, baseline: tuple = (320, 370)):
    """
    :param box_info: 우유팩 위치 정보를 tuple 형태로 받아온다. 우유팩 영역 중심 x좌표와 y좌표 순서
    :param baseline: 우유팩 위치 정보와 비교할 기준점이다.
    :return: 우유팩이 지정한 기준점으로부터 떨어진 상대적 거리를 tuple로 반환한다.
    """
    bx, by = baseline
    cx, cy = pos
    return bx - cx, by - cy

def corner_filtering(corner:tuple, line_info:list):
    if corner is None:
        return False
    cx, cy = corner[0], corner[1]
    max_y = line_info["ALL_Y"][1]
    dy = abs(max_y-cy)
    return dy <= 40

class RoomMission:

    mode: Mode = Mode.START
    robot: Robot

    alphabet_color: str
    alphabet: str
    area_color: AreaColor
    
    @classmethod
    def reset(cls):
        cls.mode = Mode.START
        cls.set_robot(robot=cls.robot)

    @classmethod
    def set_robot(cls, robot:Robot):
        cls.robot = robot
        
        cls.robot.curr_head4room_alphabet = deque([90, 85, 80])
        cls.robot.curr_head4box = deque([75, 60, 35])


    @classmethod
    def check_area_color(cls):
        cls.robot._motion.set_head(dir=cls.robot.direction.name, angle=45)
        cls.robot._motion.set_head(dir="DOWN", angle=45)
        time.sleep(0.5)
        cls.robot.color = LineColor.GREEN
        cls.robot.set_line_and_edge_info()
        
        print(cls.robot.edge_info)
        print(cls.robot.line_info)
        cls.area_color = AreaColor.GREEN if cls.robot.edge_info["EDGE_DOWN"] else AreaColor.BLACK
        
        cls.robot._motion.notice_area(area=cls.area_color.name)
        cls.robot._motion.set_head(dir="LEFTRIGHT_CENTER")
        cls.robot.color = LineColor.GREEN if cls.area_color == AreaColor.GREEN else LineColor.BLACK
        return True
    
    @classmethod
    def detect_alphabet(cls) -> bool:
        head_angle = cls.robot.curr_head4room_alphabet[0]
        cls.robot._motion.set_head("DOWN", angle=head_angle)
        time.sleep(0.3)
        cls.robot.set_line_and_edge_info()
        alphabet_info = cls.robot._image_processor.get_alphabet_info4room(visualization=False,edge_info=cls.robot.edge_info)
        if alphabet_info:
            cls.alphabet_color, cls.alphabet = alphabet_info
            return True
        else:
            cls.robot.curr_head4room_alphabet.rotate(-1)
            return False

    @classmethod
    def find_box(cls) -> bool:
        pass
    
    @classmethod
    def track_box(cls) -> bool:
        """

        :return: if grab box return True else False
        """
        head_angle = cls.robot.curr_head4box[0]
        cls.robot._motion.set_head("DOWN", angle=head_angle)
        time.sleep(0.2)
        cls.robot.set_line_and_edge_info()
        box_info = cls.robot._image_processor.get_milk_info(color=cls.alphabet_color)
        
        width = False if head_angle == 35 else True
        if box_info:
            (dx, dy) = get_distance_from_baseline(pos=box_info)

            if dy > 10:  # 기준선 보다 위에 있다면
                if -40 <= dx <= 40:
                    print("기준점에서 적정범위. 전진 전진")
                    cls.robot._motion.walk(dir='FORWARD', loop=1, width=width)
                elif dx <= -90:
                    cls.robot._motion.turn(dir='RIGHT', loop=1)
                elif -90 < dx <= -50:  # 오른쪽
                    print("기준점에서 오른쪽으로 많이 치우침. 조정한다")
                    cls.robot._motion.walk(dir='RIGHT', loop=2)
                elif -50 < dx < -40:
                    cls.robot._motion.walk(dir='RIGHT', loop=1)
                    print("기준점에서 오른쪽으로 치우침. 조정한다")
                elif 90 > dx >= 50:  # 왼쪽
                    print("기준점에서 왼쪽으로 많이 치우침. 조정한다")
                    cls.robot._motion.walk(dir='LEFT', loop=2)
                elif 50 > dx > 40:  # 왼쪽
                    print("기준점에서 왼쪽으로 치우침. 조정한다")
                    cls.robot._motion.walk(dir='LEFT', loop=2)

                elif dx >= 90:
                    cls.robot._motion.turn(dir='LEFT', loop=1)

            else:
                if head_angle == 35:
                    cls.robot._motion.grab(switch=True)
                    return True
                else:
                    cls.robot.curr_head4box.rotate(-1)

        else:
            cls.mode = Mode.FIND_BOX

        return False

    @classmethod
    def drop_box(cls) -> bool:
        cls.robot._motion.walk(dir='FORWARD', loop=2, grab=True)
        cls.robot._motion.grab(switch=False)
        cls.robot.color = LineColor.YELLOW
        time.sleep(0.5)
        return True
    
    @classmethod
    def find_line(cls) -> bool:
        if not cls.robot.line_info['V']:
            cls.robot._motion.turn(dir=cls.robot.direction.name, loop=2)
        else:
            cls.robot._motion.walk('FORWARD', loop=2, grab=True)
            return True
        return False

    @classmethod
    def turn_to_area(cls) -> bool:
        pass
    
    @classmethod
    def go_to_area(cls) -> bool:
        pass

    @classmethod
    def find_corner(cls) -> bool:
        pass
    
    @classmethod
    def go_to_corner(cls) -> bool:
        pass

    @classmethod
    def out_room(cls) -> bool:
        if cls.robot.line_info["V"]:
            if 300 < cls.robot.line_info["V_X"][0] < 340:
                cls.robot._motion.walk(dir='FORWARD', loop=2)
                return True
            elif cls.robot.line_info["V_X"][0] <= 300:
                cls.robot._motion.walk(dir='LEFT', loop=1)
            else:
                cls.robot._motion.walk(dir='RIGHT', loop=1)
        else:
            cls.robot._motion.turn(dir=cls.robot.direction.name, loop=1)
        time.sleep(0.5)
    
    @classmethod
    def run(cls) -> bool:
        pass
        

class GreenRoomMission(RoomMission):

    box_pos: BoxPos
    fast_turn : Direction
    

    @classmethod
    def set_robot(cls, robot:Robot) -> None :
        super().set_robot(robot=robot)
        cls.robot.curr_head4find_corner = deque([60, 35])

    @classmethod
    def find_box(cls) -> bool:

        head_angle = cls.robot.curr_head4box[0]
        cls.robot._motion.set_head("DOWN", angle=head_angle)
        time.sleep(0.2)
        cls.robot.set_line_and_edge_info()
        box_info = cls.robot._image_processor.get_milk_info(color=cls.alphabet_color)

        if box_info:
            return True
        else:
            if head_angle == 35:
                cls.robot._motion.turn(dir=cls.robot.direction.name, loop=8)
                cls.update_box_pos(box_info=box_info)
            cls.robot.curr_head4box.rotate(-1)
            return False

    @classmethod
    def update_box_pos(cls, box_info: tuple):
        cls.box_pos = BoxPos.LEFT if cls.robot.direction == Direction.LEFT else BoxPos.RIGHT

    @classmethod
    def turn_to_area(cls) -> bool:

        found_area: bool = cls.robot.line_info["H"] and cls.robot.line_info["len(H)"] >= 300

        if found_area :
            cls.robot._motion.move_arm(dir='HIGH')
            return True

        cls.robot._motion.turn(dir=cls.fast_turn.name, grab=True, loop=1)
        return False

    @classmethod
    def go_to_area(cls) -> bool:
        in_area: bool = cls.robot.line_info['ALL_Y'][1] > 460
        if in_area:
            return True
        cls.robot._motion.walk(dir="FORWARD", loop=1, grab=True)
        return False


    @classmethod
    def find_corner(cls) -> bool:
        head_angle = cls.robot.curr_head4find_corner[0]
        cls.robot._motion.set_head("DOWN", angle=head_angle)
        time.sleep(0.2)
        cls.robot.set_line_and_edge_info()
        
        corner = cls.robot._image_processor.get_yellow_line_corner(visualization=False)
        corner = corner if corner_filtering(corner=corner, line_info=cls.robot.line_info) else None
        if corner :
            return True
        else:
            if head_angle == 35:
                if cls.box_pos == BoxPos.RIGHT:
                    cls.robot._motion.turn(dir=Direction.LEFT.name, loop=2)
                else:
                    cls.robot._motion.turn(dir=Direction.RIGHT.name, loop=2)
            cls.robot.curr_head4find_corner.rotate(-1)
        return False

    @classmethod
    def go_to_corner(cls) -> bool:
        head_angle = cls.robot.curr_head4find_corner[0]
        cls.robot._motion.set_head("DOWN", angle=head_angle)
        time.sleep(0.2)
        cls.robot.set_line_and_edge_info()
        width = False if head_angle == 35 else True
        corner = cls.robot._image_processor.get_yellow_line_corner(visualization=False)
        corner = corner if corner_filtering(corner=corner, line_info=cls.robot.line_info) else None
        if corner :
            (dx, dy) = get_distance_from_baseline(pos=corner)
            if dy > 10:  # 기준선 보다 위에 있다면
                if -50 <= dx <= 50:
                    cls.robot._motion.walk(dir='FORWARD', loop=1, width=width)
                elif dx <= -70:
                    cls.robot._motion.turn(dir='RIGHT', loop=1)
                elif -70 < dx <= -50:  # 오른쪽
                    cls.robot._motion.walk(dir='RIGHT', loop=1)
                elif 70 > dx >= 50:  # 왼쪽
                    cls.robot._motion.walk(dir='LEFT', loop=1)
                elif dx >= 70:
                    cls.robot._motion.turn(dir='LEFT', loop=1)
            else:
                if head_angle == 35:
                    #cls.robot._motion.walk(dir='FORWARD', loop=1, width=width)
                    return True
                else:
                    cls.robot.curr_head4find_corner.rotate(-1)
        else:
            cls.mode = Mode.FIND_CONRER
        return False

    @classmethod
    def out_to_area(cls):
        if cls.robot.direction.name == cls.box_pos.name:
            if cls.robot.line_info['ALL_Y'][0] > 400 or not cls.robot.line_info['ALL']:
                cls.robot._motion.walk(dir='FORWARD', loop =2)
                cls.robot._motion.turn(dir = 'LEFT', sliding=True, wide = True, loop = 3) # 90
                return True
            else:
                cls.robot._motion.walk(dir='FORWARD', loop =1)
        else:
            if cls.robot.line_info['ALL_Y'][1] < 320 :
                cls.robot._motion.turn(dir = 'RIGHT', sliding=True, wide = True, loop = 3) # 90
                return True
            else:
                cls.robot._motion.walk(dir='BACKWARD', loop =1)
        return False
     
    @classmethod
    def go_to_line(cls):
        if cls.robot.line_info['H']:
            if cls.robot.line_info['ALL_Y'] < 470:
                if 80 < cls.robot.line_info["DEGREE"] < 100:
                    if 290 < np.mean(cls.robot.line_info["V_X"]) < 350:
                        cls.robot._motion.walk('FORWARD', 1)
                    else:
                        if np.mean(cls.robot.line_info["V_X"]) <= 290:
                            cls.robot._motion.walk('LEFT', 1)
                        elif np.mean(cls.robot.line_info["V_X"]) >= 350:
                            cls.robot._motion.walk('RIGHT', 1)
                elif 0 < cls.robot.line_info["DEGREE"] <= 80:
                    cls.robot._motion.turn('LEFT', 1)
                elif cls.robot.line_info["DEGREE"] == 0:
                    print('색깔 masking 확인하거나 sleep 확인')
                else:
                    cls.robot._motion.turn('RIGHT', 1)
            else:
                cls.robot._motion.walk('FORWARD', 2)
                cls.robot._motion.set_head(dir='DOWN', angle= 10)
                time.sleep(1)
                return True
        else:
            if cls.robot.direction.name == cls.box_pos.name:
                cls.robot._motion.turn(dir = 'LEFT')
            else:
                cls.robot._motion.turn(dir = 'RIGHT')
        return False

    @classmethod
    def run(cls, mode = 'default'):
        mode = cls.mode
        print(mode.name)
        if mode == Mode.START:
            cls.mode = Mode.DETECT_ALPHABET

        elif mode == Mode.DETECT_ALPHABET:
            if cls.detect_alphabet():
                cls.mode = Mode.FIND_BOX
                cls.box_pos = BoxPos.RIGHT if cls.robot.direction == Direction.LEFT else BoxPos.LEFT

        elif mode == Mode.FIND_BOX:
            if cls.find_box():
                
                cls.mode = Mode.TRACK_BOX
                if cls.robot.direction == Direction.LEFT :
                    cls.fast_turn = Direction.LEFT if cls.box_pos == BoxPos.RIGHT else Direction.RIGHT
                else:
                    cls.fast_turn = Direction.RIGHT if cls.box_pos == BoxPos.LEFT else Direction.LEFT

        elif mode == Mode.TRACK_BOX:
            if cls.track_box():
                cls.mode = Mode.TURN_TO_AREA
                cls.robot._motion.turn(dir=cls.fast_turn.name, grab=True, wide=True, sliding=True, loop=2)

        elif mode == Mode.TURN_TO_AREA:
            if cls.turn_to_area():
                cls.mode = Mode.GO_TO_AREA

        elif mode == Mode.GO_TO_AREA:
            if cls.go_to_area():
                cls.mode = Mode.DROP_BOX

        elif mode == Mode.DROP_BOX:
            if cls.drop_box():
                if mode == 'default':
                    cls.mode = Mode.FIND_CONRER
                    cls.robot.color = LineColor.YELLOW
                    cls.robot._motion.turn(dir=cls.fast_turn.name, loop=5, wide=True, sliding=True)
                    cls.robot.curr_head4find_corner = deque([60, 45, 35])
                else:
                    cls.robot._motion.set_head(dir='DOWN', angle = 45)
                    time.sleep(0.5)
                    if cls.robot.direction.name == cls.box_pos.name:
                        cls.robot._motion.turn(dir='RIGHT', sliding=True, wide=True, loop =3) # 90
                    else:
                        cls.robot._motion.walk(dir='BACKWARD', loop = 3) # H_Y < 50 일 때까지 

        elif mode == Mode.FIND_CONRER:
            if mode == 'default':
                if cls.find_corner():
                    cls.mode = Mode.GO_TO_CORNER
            else:
                if cls.out_to_area():
                    cls.robot._motion.set_head(dir='DOWN', angle = 60)
                    time.sleep(0.5)
                    cls.robot.color = LineColor.YELLOW
                    cls.mode = Mode.GO_TO_CORNER

        elif mode == Mode.GO_TO_CORNER:
            if mode == 'default':
                if cls.go_to_corner():
                    cls.mode = cls.mode = Mode.OUT_ROOM
                    loop: int
                    loop = 4 if cls.fast_turn == Direction.RIGHT else 2
                    cls.robot._motion.turn(dir=cls.robot.direction.name, loop=loop)
            else:
                if cls.go_to_line():
                    cls.mode = cls.mode = Mode.OUT_ROOM
                    
        elif mode == Mode.OUT_ROOM:
            if mode == 'default':
                if cls.out_room():
                    cls.mode = Mode.END
            else:
                cls.mode = Mode.END

        elif mode == Mode.END:
            return True
        
        return False

class BlackRoomMission(RoomMission):


    @classmethod
    def find_box(cls) -> bool:

        head_angle = cls.robot.curr_head4box[0]
        cls.robot._motion.set_head("DOWN", angle=head_angle)
        time.sleep(0.2)
        cls.robot.set_line_and_edge_info()
        box_info = cls.robot._image_processor.get_milk_info(color=cls.alphabet_color)

        if box_info:
            return True
        else:
            if head_angle == 35:
                cls.robot._motion.turn(dir=cls.robot.direction.name, loop=2)
            cls.robot.curr_head4box.rotate(-1)
            return False

    @classmethod
    def turn_to_area(cls) -> bool:
        cls.robot._motion.turn(dir=cls.robot.direction.name, loop=4)
        return True

    @classmethod
    def find_corner(cls) -> bool:
        head_angle = cls.robot.curr_head4find_corner[0]
        cls.robot._motion.set_head("DOWN", angle=head_angle)
        time.sleep(0.2)
        cls.robot.set_line_and_edge_info()
        corner = cls.robot._image_processor.get_yellow_line_corner(visualization=False)
        corner = corner if corner_filtering(corner=corner, line_info=cls.robot.line_info) else None
        if corner:
            return True
        else:
            if head_angle == 35:
                cls.robot._motion.turn(dir=cls.robot.direction.name, loop=2)
            cls.robot.curr_head4find_corner.rotate(-1)


    @classmethod
    def go_to_corner(cls) -> bool :
        head_angle = cls.robot.curr_head4find_corner[0]
        cls.robot._motion.set_head("DOWN", angle=head_angle)
        cls.robot.set_line_and_edge_info()
        time.sleep(0.3)
        width = False if head_angle == 35 else True
        corner = cls.robot._image_processor.get_yellow_line_corner(visualization=False)
        if corner:
            (dx, dy) = get_distance_from_baseline(pos=corner)
            if dy > 10:  # 기준선 보다 위에 있다면
                if -50 <= dx <= 50:
                    cls.robot._motion.walk(dir='FORWARD', loop=1, width=width)
                elif dx <= -70:
                    cls.robot._motion.turn(dir='RIGHT', loop=1)
                elif -70 < dx <= -50:  # 오른쪽
                    cls.robot._motion.walk(dir='RIGHT', loop=1)
                elif 70 > dx >= 50:  # 왼쪽
                    cls.robot._motion.walk(dir='LEFT', loop=1)
                elif dx >= 70:
                    cls.robot._motion.turn(dir='LEFT', loop=1)
            else:
                if head_angle == 35:
                    cls.robot._motion.walk(dir='FORWARD', loop=1, width=width)
                    return True
                else:
                    cls.robot.curr_head4find_corner.rotate(-1)
        else:
            cls.mode = Mode.FIND_CONRER
        return False

    @classmethod
    def find_yellow_line(cls) -> bool:
        cls.robot._motion.set_head("DOWN", angle=60)
        cls.robot.set_line_and_edge_info()
        if cls.robot.line_info["ALL_Y"][1]:
            return True
        cls.robot._motion.turn(dir=cls.robot.direction.name, grab=True, wide=True, sliding=True, loop=1)
        time.sleep(0.5)
        return False

    @classmethod
    def go_out_area(cls) -> bool:
        cls.robot._motion.walk(dir="FORWARD", grab=True, loop=1)
        if cls.robot._image_processor.is_out_of_black():
            return True
        else:
            return False


    
    @classmethod
    def run(cls):
        mode = cls.mode
        print(mode.name)
        
        if mode == Mode.START:
            cls.mode = Mode.DETECT_ALPHABET
            
        elif mode == Mode.DETECT_ALPHABET:
            if cls.detect_alphabet():
                cls.robot.black_room.append(cls.alphabet)
                cls.mode = Mode.TURN_TO_AREA

        elif mode == Mode.TURN_TO_AREA:
            if cls.turn_to_area():
                cls.mode = Mode.FIND_BOX
                
        elif mode == Mode.FIND_BOX:
            if cls.find_box():
                cls.mode = Mode.TRACK_BOX

        elif mode == Mode.TRACK_BOX:
            if cls.track_box():
                cls.mode = Mode.FIND_YELLOW_LINE
                cls.robot.color = LineColor.YELLOW
                cls.robot._motion.turn(dir=cls.robot.direction.name, grab=True, wide=True, sliding=True, loop=5)
                
                cls.robot._motion.set_head("DOWN", angle=60)

        elif mode == Mode.FIND_YELLOW_LINE:
            if cls.find_yellow_line():
                cls.mode = Mode.GO_OUT_AREA
                cls.robot._motion.set_head("DOWN", angle=35)

        elif mode == Mode.GO_OUT_AREA:
            if cls.go_out_area():
                cls.mode = Mode.DROP_BOX

        elif mode == Mode.DROP_BOX:
            if cls.drop_box():
                cls.mode = Mode.FIND_CONRER
                cls.robot.curr_head4find_corner = deque([55, 45, 35])

        elif mode == Mode.FIND_CONRER:
            if cls.find_corner():
                cls.mode = Mode.GO_TO_CORNER
                
        elif mode == Mode.GO_TO_CORNER:
            if cls.go_to_corner():
                cls.mode = Mode.OUT_ROOM
                
        elif mode == Mode.OUT_ROOM:
            if cls.out_room():
                cls.mode = Mode.END
                
        elif mode == Mode.END:
            return True
        
        return False