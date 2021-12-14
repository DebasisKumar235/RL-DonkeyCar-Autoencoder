import os

import cv2
import gym
import numpy as np
import pygame
from pygame.locals import *  # noqa: F403

UP = (1, 0)
LEFT = (0, 1)
RIGHT = (0, -1)
DOWN = (-1, 0)

MAX_TURN = 1
MAX_THROTTLE = 0.5
# Smoothing constants
STEP_THROTTLE = 0.8
STEP_TURN = 0.8


def control(x, theta, control_throttle, control_steering):
    """
    Smooth control.
    :param x: (float)
    :param theta: (float)
    :param control_throttle: (float)
    :param control_steering: (float)
    :return: (float, float)
    """
    target_throttle = x * MAX_THROTTLE
    target_steering = MAX_TURN * theta
    if target_throttle > control_throttle:
        control_throttle = min(target_throttle, control_throttle + STEP_THROTTLE)
    elif target_throttle < control_throttle:
        control_throttle = max(target_throttle, control_throttle - STEP_THROTTLE)
    else:
        control_throttle = target_throttle

    if target_steering > control_steering:
        control_steering = min(target_steering, control_steering + STEP_TURN)
    elif target_steering < control_steering:
        control_steering = max(target_steering, control_steering - STEP_TURN)
    else:
        control_steering = target_steering
    return control_throttle, control_steering


# pytype: disable=name-error
moveBindingsGame = {K_UP: UP, K_LEFT: LEFT, K_RIGHT: RIGHT, K_DOWN: DOWN}  # noqa: F405
# pytype: enable=name-error
WHITE = (230, 230, 230)
pygame.font.init()
FONT = pygame.font.SysFont("Open Sans", 25)

pygame.init()
window = pygame.display.set_mode((400, 400), RESIZABLE)

frame_skip = 2
total_frames = 5000
render = True
output_folder = "logs/carracing-v0"

# Create folder if needed
os.makedirs(output_folder, exist_ok=True)

control_throttle, control_steering = 0, 0

env = gym.make("CarRacing-v0")
obs = env.reset()
for frame_num in range(total_frames):
    # action = env.action_space.sample()
    # # do not break too much
    # # steer, gas, brake
    # action[2] = max(action[2], 0.1)
    control_break = 0
    x, theta = 0, 0
    # Record pressed keys
    keys = pygame.key.get_pressed()
    for keycode in moveBindingsGame.keys():
        if keys[keycode]:
            x_tmp, th_tmp = moveBindingsGame[keycode]
            x += x_tmp
            theta += th_tmp
    if keys[K_b]:
        control_break = 0.1

    # Smooth control for teleoperation
    control_throttle, control_steering = control(x, theta, control_throttle, control_steering)

    window.fill((0, 0, 0))
    pygame.display.flip()
    # Limit FPS
    # pygame.time.Clock().tick(1 / TELEOP_RATE)
    for event in pygame.event.get():
        if (event.type == QUIT or event.type == KEYDOWN) and event.key in [  # pytype: disable=name-error
            K_ESCAPE,  # pytype: disable=name-error
            K_q,  # pytype: disable=name-error
        ]:
            env.close()
            exit()

    window.fill((0, 0, 0))
    text = str("Control ready")
    text = FONT.render(text, True, WHITE)
    window.blit(text, (100, 100))
    pygame.display.flip()

    # steer, gas, brake
    action = np.array([-control_steering, control_throttle, 0.0])

    for _ in range(frame_skip):
        obs, _, done, _ = env.step(action)
        if done:
            break
    if render:
        env.render()
    path = os.path.join(output_folder, f"{frame_num}.jpg")
    cv2.imwrite(path, obs)
    if done:
        obs = env.reset()
        control_throttle, control_steering = 0, 0