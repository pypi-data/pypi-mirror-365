# === GRADIENT DEDCENT ALGORITHM ===
# https://github.com/hurtki/DataSince

import math
from typing import Callable


def gradient_descent_2d(
    nigzeret: Callable[[float], float],
    start: float,
    alpha: float,
    iter: int,
    time_log: int
) -> float:
    """
    This function realizes a gradient descent algorithm 
    """
    # assighning unreal previous to not quit from the start
    previous = start + 999999
    # starting trying from start point
    x = start

    # entering cycle for iter
    for i in range(iter):
        # counting nigzerert volume from the given function
        value = nigzeret(x)

        # checking if we need to log somethink
        if i % (iter // time_log) == 0:
            print(f"value: {value}, x: {x}")

        # assighning new x value
        x -= alpha * value
        previous = value

    return x


def gradient_descent_3d(
    nigzeret: Callable[[tuple[float, float]], tuple[float, float]],
    start: tuple[float, float],
    alpha: float,
    iter: int,
    time_log: float
) -> tuple[float, float]:
    
    x = start
    for i in range(iter):
        grad_w, grad_b = nigzeret(x)
        # логирование
        
        if (not time_log == 0) and i % (iter // time_log) == 0:
            print(f"Iteration {i}: w={x[0]}, b={x[1]}, grad_w={grad_w}, grad_b={grad_b}")
        x = (x[0] - alpha * grad_w, x[1] - alpha * grad_b)
    return x
