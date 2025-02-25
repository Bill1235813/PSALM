import os
import cv2
import numpy as np
import argparse
import re

black_color = (0, 0, 0)
blue_color = (255, 0, 0)
red_color = (0, 0, 255)
white_color = (255, 255, 255)
line_thickness = 2
res_factor = 200
textmoveup = 10

robot = cv2.imread("hoist.png")
robot = cv2.resize(robot, (int(0.8 * res_factor), int(0.8 * res_factor)), interpolation=cv2.INTER_LINEAR)

crate = cv2.imread("crate.png")
crate = cv2.resize(crate, (int(0.8 * res_factor), int(0.8 * res_factor)), interpolation=cv2.INTER_LINEAR)


def draw_init(row, col, connect_row, connect_col, hoist_loc_dict, crate_loc_dict, write_img_to):
    img = np.full((res_factor * (row + 3), res_factor * col, 3), 255, dtype=np.uint8)

    for r in range(row + 1):
        img = cv2.line(img, (0, r * res_factor), (col * res_factor, r * res_factor), black_color, line_thickness)

    for c in range(col + 1):
        img = cv2.line(img, (c * res_factor, 0), (c * res_factor, row * res_factor), black_color, line_thickness)

    font = cv2.FONT_HERSHEY_COMPLEX_SMALL

    for hoist_id, robot_loc in hoist_loc_dict.items():
        img[
            int((robot_loc[0] - 0.9) * res_factor): int((robot_loc[0] - 0.9) * res_factor) + int(0.8 * res_factor),
            int((robot_loc[1] - 0.9) * res_factor): int((robot_loc[1] - 0.9) * res_factor) + int(0.8 * res_factor),
            :
        ] = robot
        cv2.putText(img, "hoist " + str(hoist_id), ((robot_loc[1] - 1) * res_factor + textmoveup * 5, robot_loc[0] * res_factor - textmoveup), font, 1, (0, 0, 0), 1, cv2.LINE_AA)

    cv2.rectangle(img, ((connect_col - 1) * res_factor, connect_row * res_factor), (connect_col * res_factor, (connect_row + 1) * res_factor), red_color, -1)
    cv2.rectangle(img, (0, (connect_row + 1) * res_factor), (col * res_factor, (connect_row + 2) * res_factor), red_color, -1)
    cv2.putText(img, "Load Area",
                (int(col / 2 * res_factor) - 10 * textmoveup, int((row + 1.5) * res_factor)), font, 1.5,
                white_color, 2, cv2.LINE_AA)

    for crate_id, crate_loc in crate_loc_dict.items():
        cv2.rectangle(img, (crate_id * res_factor, (row + 2) * res_factor), ((crate_id + 1) * res_factor, (row + 3) * res_factor), black_color, 2)
        img[
            int((row + 2.1) * res_factor): int((row + 2.1) * res_factor) + int(0.8 * res_factor),
            int((crate_loc + 0.1) * res_factor): int((crate_loc + 0.1) * res_factor) + int(0.8 * res_factor),
            :
        ] = crate
        cv2.putText(img, "crate " + str(crate_id), (crate_loc * res_factor + textmoveup * 3, int((row + 2.5) * res_factor) + textmoveup), font, 1.5,
                    white_color, 2, cv2.LINE_AA)

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

    problem_count = 17
    for p_file in range(1, problem_count + 1):
        if not os.path.exists("p{:02d}.nl".format(p_file)):
            continue
        nl_desp = open("p{:02d}.nl".format(p_file)).read()
        area_count = re.findall(re.compile(r"You have (\d) depot storeareas"), nl_desp)
        assert len(area_count) == 1
        depot_count = int(area_count[0])
        if depot_count >= 4:
            assert depot_count % 2 == 0
            row = 2
            col = depot_count // 2
        else:
            row = 1
            col = depot_count

        connect_to_load = re.findall(re.compile(r"depot48-(\d)-(\d) and loadarea are connected"), nl_desp)
        assert len(connect_to_load) == 1
        connect_loc = connect_to_load[0]
        connect_row, connect_col = int(connect_loc[0]), int(connect_loc[1])
        hoist_locs = re.findall(re.compile(r"hoist(\d) is in depot48-(\d)-(\d)"), nl_desp)
        hoist_loc_dict = {}
        for hoist_id, h_row, h_col in hoist_locs:
            hoist_loc_dict[int(hoist_id)] = (int(h_row), int(h_col))
        crate_locs = re.findall(re.compile(r"crate(\d) is on container-0-(\d)"), nl_desp)
        crate_loc_dict = {}
        for crate_id, c_col in crate_locs:
            crate_loc_dict[int(crate_id)] = int(c_col)

        draw_init(row, col, connect_row, connect_col, hoist_loc_dict, crate_loc_dict, f"images/init_state_{p_file}.png")

# cv2.imshow("Image", img)
