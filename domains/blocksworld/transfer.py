import os
import cv2
import numpy as np
import argparse
import re
import copy

line_thickness = 2
res_factor = 100

blocks_img = []
for i in range(1, 11):
    block = cv2.imread(f"B{i}.png")
    block = cv2.resize(block, (res_factor, res_factor), interpolation=cv2.INTER_LINEAR)
    hsv = cv2.cvtColor(block, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([0, 0, 0]))
    block[mask > 0] = (255, 255, 255)
    blocks_img.append(block)


def merge_list(l):
    new_dict = {}
    # a is on top of b.
    for item in l:
        find_match = False
        for start_id, pile in new_dict.items():
            if item[1] == pile[-1] and item[0] in new_dict:
                new_dict[start_id] = pile + new_dict[item[0]]
                del new_dict[item[0]]
                find_match = True
                break
            elif item[1] == pile[-1]:
                new_dict[start_id].append(item[0])
                find_match = True
                break
        if find_match:
            continue
        elif item[0] in new_dict:
            new_dict[item[1]] = [item[1]] + new_dict[item[0]]
            del new_dict[item[0]]
        else:
            new_dict[item[1]] = [item[1], item[0]]
    return new_dict


def draw_dict(block_dict, write_to_file):
    overlap = 28
    height = max([len(b) for b in block_dict.values()]) * (res_factor - overlap) + overlap
    width = res_factor * (len(block_dict) * 2 - 1)
    img = np.full((height, width, 3), 255, dtype=np.uint8)

    for pile_idx, (start_id, blocks) in enumerate(block_dict.items()):
        top = height
        previous_color = None
        for bid, b in enumerate(blocks):
            if bid > 0:
                add_img_color = copy.deepcopy(blocks_img[b - 1][res_factor // 2:])
                mask[:, :res_factor // 2] = 0
                add_img_color[mask[res_factor // 2:, :] > 0] = previous_color
                insert_block = np.concatenate((blocks_img[b - 1][:res_factor // 2], add_img_color), axis=0)
                hsv = cv2.cvtColor(block, cv2.COLOR_BGR2HSV)
                tmp_mask = cv2.inRange(hsv, np.array([230, 230, 230]), np.array([256, 256, 256]))
                insert_block[tmp_mask > 0] = tuple(insert_block[res_factor // 2, res_factor - 10, :])
            else:
                insert_block = blocks_img[b - 1]
            previous_color = tuple(insert_block[res_factor // 2, res_factor - 10, :])
            img[top - res_factor: top, res_factor * pile_idx * 2: res_factor * (pile_idx * 2 + 1), :] = insert_block
            top = top - res_factor + overlap

    cv2.imwrite(f"images/{write_to_file}.png", img)


if not (os.path.exists("images") and os.path.isdir('images')):
    os.mkdir("images")

problem_count = 16
for p_file in range(1, problem_count + 1):
    nl_desp = open("p{:02d}.nl".format(p_file)).read()
    bottom_blocks = re.findall(re.compile(r"\nb(\d+) is on the table."), nl_desp)
    top_blocks = re.findall(re.compile(r"\nb(\d+) is clear."), nl_desp)
    init_trans_list = re.findall(re.compile(r"\nb(\d+) is on top of b(\d+)."), nl_desp)
    goal_trans_list = re.findall(re.compile(r"\nb(\d+) should be on top of b(\d+)."), nl_desp)

    init_block_dict = merge_list([(int(a), int(b)) for a, b in init_trans_list])
    goal_block_dict = merge_list([(int(a), int(b)) for a, b in goal_trans_list])
    init_bottom_list = [int(b) for b in bottom_blocks]
    init_top_list = [int(b) for b in top_blocks]
    for i in init_bottom_list:
        if i not in init_block_dict:
            init_block_dict[i] = [i]
    print(init_bottom_list, init_top_list, init_block_dict, goal_block_dict)

    draw_dict(init_block_dict, f"init_state_{p_file}")
    draw_dict(goal_block_dict, f"goal_state_{p_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("--row", type=int, required=True)
    # parser.add_argument("--col", type=int, required=True)
    # parser.add_argument("--upper_right_color", type=str, required=True)
    # parser.add_argument("--black_loc", type=int, nargs="+", required=True)
    # parser.add_argument("--white_loc", type=int, nargs="+", required=True)
    # parser.add_argument("--problem_id", type=int, required=True)
    args = parser.parse_args()

    # if args.upper_right_color == "black":
    #     upper_right_color = black_color
    #     other_color = white_color
    # else:
    #     upper_right_color = white_color
    #     other_color = black_color

    # if not os.path.exists("images") and os.path.isdir('images'):
    #     os.mkdir("images")
    # draw_init(args.row, args.col, tuple(args.black_loc), tuple(args.white_loc), f"images/init_state_{args.problem_id}.png")
    # draw_goal(args.row, args.col, upper_right_color, other_color, f"images/goal_state_{args.problem_id}.png")

# cv2.imshow("Image", img)
