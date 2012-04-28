import numpy as np
import cv2

MAIN_WINDOW = 'hello'
RECT_WINDOW = 'rect'
CELL_SIZE = 32
GRID_SIZE = 16 * CELL_SIZE

class PatternCreator(object):
    def __init__(self, frame, homography):
        self.img = cv2.warpPerspective(frame, homography, (GRID_SIZE, GRID_SIZE))
        cv2.namedWindow(RECT_WINDOW)
        cv2.imshow(RECT_WINDOW, self.img)

    def pattern(self, num_channels, num_steps):
        pattern = np.empty((num_channels, num_steps), np.bool)
        for channel in range(num_channels):
            for step in range(num_steps):
                cell = self.get_cell(channel, step)
                average_color = np.average(np.average(cell, axis=0), axis=0)
                pattern[channel][step] = self.is_note_set(average_color)
        return pattern

    def cell_start_end(self, id):
        start = id * CELL_SIZE + CELL_SIZE / 4
        end = start + CELL_SIZE / 2
        return start, end

    def get_cell(self, channel, step):
        channel_start, channel_end = self.cell_start_end(channel)
        step_start, step_end = self.cell_start_end(step)
        return self.img[
          channel_start : channel_end,
          step_start : step_end,
          :]

    def is_note_set(self, color):
        return color[0] > 160 or color[2] > 160

def global_on_mouse(event, x, y, unknown, lego_player):
    lego_player.on_mouse(event, x, y)

class LegoPlayer(object):
    def __init__(self):
        self.homography = None
        self.roi = np.empty((4, 2))
        self.roi_index = -1

        cv2.namedWindow(MAIN_WINDOW)
        cv2.setMouseCallback(MAIN_WINDOW, global_on_mouse, self)
        self.capture = cv2.VideoCapture(0)

    def on_mouse(self, event, x, y):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.has_roi():
                self.roi_index = -1
            self.roi_index += 1
            self.roi[self.roi_index] = [x, y]
            if self.has_roi():
                self.compute_homography()

    def has_roi(self):
        return self.roi_index == 3

    def compute_homography(self):
        src_points = self.roi
        dst_points = np.zeros_like(src_points)
        dst_points[1][0] = GRID_SIZE
        dst_points[2] = [GRID_SIZE, GRID_SIZE]
        dst_points[3][1] = GRID_SIZE
        self.homography = cv2.findHomography(src_points, dst_points)[0]

    def print_pattern(self, pattern):
        for channel in pattern:
            for step in channel:
                if step:
                    print '*',
                else:
                    print ' ',
            print
        print

    def loop(self):
        while True:
            success, img = self.capture.read()
            if success:
                cv2.imshow(MAIN_WINDOW, img)
                if self.homography is not None:
                    pattern_creator = PatternCreator(img, self.homography)
                    pattern = pattern_creator.pattern(4, 16)
                    self.print_pattern(pattern)
            cv2.waitKey(10)

if __name__ == '__main__':
    lego_player = LegoPlayer()
    lego_player.loop()
