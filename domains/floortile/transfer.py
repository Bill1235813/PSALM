import os
import cv2
import numpy as np
import argparse

black_color = (0, 0, 0)
white_color = (160, 160, 160)
line_thickness = 2
res_factor = 100

black_pen = cv2.imread("black_pen.png")
black_pen = cv2.resize(black_pen, (int(0.9 * res_factor), int(0.9 * res_factor)), interpolation=cv2.INTER_LINEAR)
white_pen = cv2.imread("white_pen.png")
white_pen = cv2.resize(white_pen, (int(0.9 * res_factor), int(0.9 * res_factor)), interpolation=cv2.INTER_LINEAR)


def draw_init(row, col, black_loc, white_loc, write_img_to):
    img = np.full((res_factor * row, res_factor * col, 3), 255, dtype=np.uint8)

    for r in range(row + 1):
        img = cv2.line(img, (0, r * res_factor), (col * res_factor, r * res_factor), black_color, line_thickness)

    for c in range(col + 1):
        img = cv2.line(img, (c * res_factor, 0), (c * res_factor, row * res_factor), black_color, line_thickness)

    img[int((black_loc[0] + 0.05) * res_factor): int((black_loc[0] + 0.05) * res_factor) + int(0.9 * res_factor),
    int((black_loc[1] - 0.95) * res_factor): int((black_loc[1] - 0.95) * res_factor) + int(0.9 * res_factor),
    :] = black_pen

    img[int((white_loc[0] + 0.05) * res_factor): int((white_loc[0] + 0.05) * res_factor) + int(0.9 * res_factor),
    int((white_loc[1] - 0.95) * res_factor): int((white_loc[1] - 0.95) * res_factor) + int(0.9 * res_factor),
    :] = white_pen

    cv2.imwrite(write_img_to, cv2.flip(img, 0))


def draw_goal(row, col, upper_right_color, other_color, write_img_to):
    img = np.full((res_factor * row, res_factor * col, 3), 255, dtype=np.uint8)

    for r in range(row + 1):
        img = cv2.line(img, (0, r * res_factor), (col * res_factor, r * res_factor), black_color, line_thickness)

    for c in range(col + 1):
        img = cv2.line(img, (c * res_factor, 0), (c * res_factor, row * res_factor), black_color, line_thickness)

    for r in range(row, 1, -1):
        for c in range(col, 0, -1):
            par = (row + col - r - c) % 2
            if par == 0:
                cv2.rectangle(img, ((c - 1) * res_factor, (r - 1) * res_factor), (c * res_factor, r * res_factor),
                              upper_right_color, -1)
            else:
                cv2.rectangle(img, ((c - 1) * res_factor, (r - 1) * res_factor), (c * res_factor, r * res_factor),
                              other_color, -1)

    cv2.imwrite(write_img_to, cv2.flip(img, 0))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--row", type=int, required=True)
    parser.add_argument("--col", type=int, required=True)
    parser.add_argument("--upper_right_color", type=str, required=True)
    parser.add_argument("--black_loc", type=int, nargs="+", required=True)
    parser.add_argument("--white_loc", type=int, nargs="+", required=True)
    parser.add_argument("--problem_id", type=int, required=True)
    args = parser.parse_args()

    if args.upper_right_color == "black":
        upper_right_color = black_color
        other_color = white_color
    else:
        upper_right_color = white_color
        other_color = black_color

    if not (os.path.exists("images") and os.path.isdir('images')):
        os.mkdir("images")
    draw_init(args.row, args.col, tuple(args.black_loc), tuple(args.white_loc), f"images/init_state_{args.problem_id}.png")
    draw_goal(args.row, args.col, upper_right_color, other_color, f"images/goal_state_{args.problem_id}.png")

# cv2.imshow("Image", img)
