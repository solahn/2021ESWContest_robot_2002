import cv2
import os
import numpy as np

class HashDetector:
    def __init__(self, file_path) -> None:        
        self.directions_hash = []
        self.directions = []
        for direction in os.listdir(file_path):
            self.directions_hash.append(self.image_to_hash(cv2.imread(file_path + direction)))
            self.directions.append(direction.rsplit('.')[0])
        print(file_path + direction)
        print(self.directions)
            
    @staticmethod
    def image_to_hash(img : np.ndarray) -> list:        
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, (16, 16))
        avg = img.mean()
        bin = 1 * (img > avg)
        return bin
         
    @staticmethod
    def hamming_distance(src_hash : list, cmp_hash : list) -> int:
        src_hash = src_hash.reshape(1,-1)
        cmp_hash = cmp_hash.reshape(1,-1)
        # 같은 자리의 값이 서로 다른 것들의 합
        distance = (src_hash != cmp_hash).sum()
        return distance
    
    def detect_direction_hash(self, img : np.ndarray) -> str:
        img_hash = self.image_to_hash(img)
        hdist_list = []
        
        for hash in self.directions_hash:
            hdist_list.append(self.hamming_distance(img_hash, hash))
            
        result = hdist_list.index(min(hdist_list))
        
        return self.directions[result]


if __name__ == "__main__":
    from Sensor.ImageProcessor import ImageProcessor
    from imutils import auto_canny
    from Sensor.Target import Target
    imageProcessor = ImageProcessor(video_path='src/N.h264')
    hashDetector = HashDetector()
    while True:
        targets = []
        src = imageProcessor.get_image()
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        mask = auto_canny(mask)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True)*0.02, True)
            vertice = len(approx)

            if vertice == 4 and cv2.contourArea(cnt)> 2500:
                targets.append(Target(contour=cnt))
        if targets:
            targets.sort(key= lambda x: x.get_area)
            roi = targets[0].get_target_roi(src = src, pad=10, visualization=True)
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            cv2.imshow("roi thresh", mask)
            cv2.waitKey(1)
            print(hashDetector.detect_direction_hash(roi))
