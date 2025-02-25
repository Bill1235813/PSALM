import os
import cv2
import numpy as np
import argparse
import re

black_color = (0, 0, 0)
white_color = (160, 160, 160)
line_thickness = 2
res_factor = 100

robot = cv2.imread("robot.png")
robot = cv2.resize(robot, (int(0.9 * res_factor), int(0.9 * res_factor)), interpolation=cv2.INTER_LINEAR)


def draw_init(row, col, robot_loc, write_img_to):
    img = np.full((res_factor * row, res_factor * col, 3), 255, dtype=np.uint8)

    for r in range(row + 1):
        img = cv2.line(img, (0, r * res_factor), (col * res_factor, r * res_factor), black_color, line_thickness)

    for c in range(col + 1):
        img = cv2.line(img, (c * res_factor, 0), (c * res_factor, row * res_factor), black_color, line_thickness)

    img[
        int((robot_loc[0] + 0.05) * res_factor): int((robot_loc[0] + 0.05) * res_factor) + int(0.9 * res_factor),
        int((robot_loc[1] + 0.05) * res_factor): int((robot_loc[1] + 0.05) * res_factor) + int(0.9 * res_factor),
        :
    ] = robot

    cv2.imwrite(write_img_to, img)


def draw_goal(row, col, final_loc_dict, write_img_to):
    img = np.full((res_factor * row, res_factor * col, 3), 255, dtype=np.uint8)

    for r in range(row + 1):
        img = cv2.line(img, (0, r * res_factor), (col * res_factor, r * res_factor), black_color, line_thickness)

    for c in range(col + 1):
        img = cv2.line(img, (c * res_factor, 0), (c * res_factor, row * res_factor), black_color, line_thickness)

    moveup = 18
    font = cv2.FONT_HERSHEY_COMPLEX
    for r in range(row):
        for c in range(col):
            if (r, c) in final_loc_dict:
                cv2.putText(img, str(final_loc_dict[(r, c)]), (c * res_factor + moveup, (r + 1) * res_factor - moveup), font, 3, (0, 0, 0), 3, cv2.LINE_AA)
            else:
                cv2.putText(img, str(0), (c * res_factor + moveup, (r + 1) * res_factor - moveup), font, 3, (0, 0, 0), 3, cv2.LINE_AA)

    cv2.imwrite(write_img_to, img)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("--row", type=int, required=True)
    # parser.add_argument("--col", type=int, required=True)
    # parser.add_argument("--robot_loc", type=int, nargs="+", required=True)
    # parser.add_argument("--", type=int, nargs="+", required=True)
    # parser.add_argument("--problem_id", type=int, required=True)
    args = parser.parse_args()

    if not (os.path.exists("images") and os.path.isdir('images')):
        os.mkdir("images")

    problem_count = 16
    for p_file in range(1, problem_count + 1):
        nl_desp = open("p{:02d}.nl".format(p_file)).read()
        grid = re.findall(re.compile(r"The robot is on a grid with (\d) rows and (\d) columns"), nl_desp)
        assert len(grid) == 1
        row = int(grid[0][0])
        col = int(grid[0][1])
        robot_locs = re.findall(re.compile(r"\nThe robot is at pos-(\d)-(\d)"), nl_desp)
        assert len(robot_locs) == 1
        robot_loc = [(int(a), int(b)) for a, b in robot_locs][0]
        final_heights = re.findall(re.compile(r"the height at pos-(\d)-(\d) is (\d)"), nl_desp)
        final_loc_dict = {(int(a), int(b)): int(h) for a, b, h in final_heights}

        draw_init(row, col, robot_loc, f"images/init_state_{p_file}.png")
        draw_goal(row, col, final_loc_dict, f"images/goal_state_{p_file}.png")

# cv2.imshow("Image", img)
