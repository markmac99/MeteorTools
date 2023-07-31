# Copyright (C) 2018-2023 Mark McIntyre

# vector maths for comparing directions of meteors etc
import numpy as np
import math


def shortestDistance(a, b, c, d):
    # Lines are L=a+bt, M=c+ds
    e = a - c
    b2 = np.dot(b, b)
    d2 = np.dot(b, b)
    bd = np.dot(b, d)
    de = np.dot(d, e)
    be = np.dot(b, e)
    db = np.dot(d, b)

    A = -b2 * d2 + bd * bd
    s = (-b2 * de + be * db) / A
    t = (+d2 * be - de * db) / A
    D = e + b * t - d * s
    d = math.sqrt(np.dot(D, D))

    return s, t, d
