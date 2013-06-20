"""
UBC Eye Movement Data Analysis Toolkit

$$$Daria: contains auxiliary functions for math calculations performed within EMDAT

Author: Nicholas FitzGerald - nicholas.fitzgerald@gmail.com

Basic geometrical helper functions
"""
import os, sys, math, random


def euclidean_distance(point1, point2):
    (x1, y1) = point1
    (x2, y2) = point2

    x1 = float(x1)
    y1 = float(y1)
    x2 = float(x2)
    y2 = float(y2)

    return math.sqrt((x1-x2)**2 + (y1-y2)**2)


def vector_difference(point1, point2):
    (x1, y1) = point1
    (x2, y2) = point2

    distance = euclidean_distance(point1, point2)

    if distance == 0:
        return 0,0
    
    (dx, dy) = (x2-x1, y2-y1)

    signx = dx > 0
    signy = dy > 0

    if dx ==0 and dy!=0:
        return distance, 0
    elif dx!=0 and dy==0:
        theta = math.pi/2
    else:
        theta = math.atan(float(abs(dy))/abs(dx))

    if signx and signy:
        return distance, theta
    elif signx and not signy:
        return distance, -theta
    elif not signx and signy:
        return distance, math.pi - theta
    elif not signx and not signy:
        return distance, theta - math.pi

    raise Exception()

def vector2coords(mag, angle):
    return (mag*math.cos(angle), mag*math.sin(angle))
   
def random_angle():
    return random.uniform(-math.pi, math.pi)

def opp_direction(direction):
    return direction-math.pi

def random_vector_coords(mag):
    return vector2coords(mag,random_angle())

def vector_add(vec1, vec2):
    (x1, y1) = vec1
    (x2, y2) = vec2
    return (x1+x2, y1+y2)

def add_random_scatter(target, mag):
    return vector_add(target, random_vector_coords(mag))

def rads2degrees(angle):
    return angle*180/math.pi
