######
#
# Adapted from: https://github.com/warrenm/AHEasing
#
# View animated examples here: https://easings.net
#
#####
# //
# //  easing.c
# //
# //  Copyright (c) 2011, Auerhaus Development, LLC
# //
# //  This program is free software. It comes without any warranty, to
# //  the extent permitted by applicable law. You can redistribute it
# //  and/or modify it under the terms of the Do What The Fuck You Want
# //  To Public License, Version 2, as published by Sam Hocevar. See
# //  http://sam.zoy.org/wtfpl/COPYING for more details.
# //
##
##
# The MIT License (MIT)
#
# Copyright (c) 2021 Kevin Matocha (kmatch98, ksmatocha@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#
# Easing functions for animation motion
#
# Input value (p) should be between 0.0 (start point) and 1.0 (ending point).
# Output values begin at 0.0 and end at 1.0 but have a specific transfer displacment function
# to give the desired motion response.
#
# Note:  Some functions return values < 0.0 or > 1.0 due "springiness".

import math

# Modeled after the line y = x
def LinearInterpolation(p):
    return p


# Modeled after the parabola y = x^2
def QuadraticEaseIn(p):
    return p * p


# Modeled after the parabola y = -x^2 + 2x
def QuadraticEaseOut(p):
    return -(p * (p - 2))


# Modeled after the piecewise quadratic
# y = (1/2)((2x)^2)             ; [0, 0.5)
# y = -(1/2)((2x-1)*(2x-3) - 1) ; [0.5, 1]
def QuadraticEaseInOut(p):
    if p < 0.5:
        return 2 * p * p
    return (-2 * p * p) + (4 * p) - 1


# Modeled after the cubic y = x^3
def CubicEaseIn(p):
    return p * p * p


# Modeled after the cubic y = (x - 1)^3 + 1
def CubicEaseOut(p):
    f = p - 1
    return f * f * f + 1


# Modeled after the piecewise cubic
# y = (1/2)((2x)^3)       ; [0, 0.5)
# y = (1/2)((2x-2)^3 + 2) ; [0.5, 1]
def CubicEaseInOut(p):
    if p < 0.5:
        return 4 * p * p * p
    f = (2 * p) - 2
    return 0.5 * f * f * f + 1


# Modeled after the quartic x^4
def QuarticEaseIn(p):
    return p * p * p * p


# Modeled after the quartic y = 1 - (x - 1)^4
def QuarticEaseOut(p):
    f = p - 1
    return f * f * f * (1 - p) + 1


# Modeled after the piecewise quartic
# y = (1/2)((2x)^4)        ; [0, 0.5)
# y = -(1/2)((2x-2)^4 - 2) ; [0.5, 1]
def QuarticEaseInOut(p):
    if p < 0.5:
        return 8 * p * p * p * p
    f = p - 1
    return -8 * f * f * f * f + 1


# Modeled after the quintic y = x^5
def QuinticEaseIn(p):
    return p * p * p * p * p


# Modeled after the quintic y = (x - 1)^5 + 1
def QuinticEaseOut(p):
    f = p - 1
    return f * f * f * f * f + 1


# Modeled after the piecewise quintic
# y = (1/2)((2x)^5)       ; [0, 0.5)
# y = (1/2)((2x-2)^5 + 2) ; [0.5, 1]
def QuinticEaseInOut(p):
    if p < 0.5:
        return 16 * p * p * p * p * p
    f = (2 * p) - 2
    return 0.5 * f * f * f * f * f + 1


# Modeled after quarter-cycle of sine wave
def SineEaseIn(p):
    return math.sin((p - 1) * math.pi / 2) + 1


# Modeled after quarter-cycle of sine wave (different phase)
def SineEaseOut(p):
    return math.sin(p * math.pi / 2)


# Modeled after half sine wave
def SineEaseInOut(p):
    return 0.5 * (1 - math.cos(p * math.pi))


# Modeled after shifted quadrant IV of unit circle
def CircularEaseIn(p):
    return 1 - math.sqrt(1 - (p * p))


# Modeled after shifted quadrant II of unit circle
def CircularEaseOut(p):
    return math.sqrt((2 - p) * p)


# Modeled after the piecewise circular function
# y = (1/2)(1 - sqrt(1 - 4x^2))           ; [0, 0.5)
# y = (1/2)(sqrt(-(2x - 3)*(2x - 1)) + 1) ; [0.5, 1]
def CircularEaseInOut(p):
    if p < 0.5:
        return 0.5 * (1 - math.sqrt(1 - 4 * (p * p)))
    return 0.5 * (math.sqrt(-((2 * p) - 3) * ((2 * p) - 1)) + 1)


# Modeled after the exponential function y = 2^(10(x - 1))
def ExponentialEaseIn(p):
    if p == 0:
        return p
    return math.pow(2, 10 * (p - 1))


# Modeled after the exponential function y = -2^(-10x) + 1
def ExponentialEaseOut(p):
    if p == 1:
        return p
    return 1 - math.pow(2, -10 * p)


# Modeled after the piecewise exponential
# y = (1/2)2^(10(2x - 1))         ; [0,0.5)
# y = -(1/2)*2^(-10(2x - 1))) + 1 ; [0.5,1]
def ExponentialEaseInOut(p):
    if (p == 0.0) or (p == 1.0):
        return p
    if p < 0.5:
        return 0.5 * math.pow(2, (20 * p) - 10)
    return (-0.5 * math.pow(2, (-20 * p) + 10)) + 1


# Modeled after the damped sine wave y = sin(13pi/2*x)*pow(2, 10 * (x - 1))
def ElasticEaseIn(p):
    return math.sin(13 * p * math.pi / 2) * math.pow(2, 10 * (p - 1))


# Modeled after the damped sine wave y = sin(-13pi/2*(x + 1))*pow(2, -10x) + 1
def ElasticEaseOut(p):
    return math.sin(-13 * math.pi / 2 * (p + 1)) * math.pow(2, -10 * p) + 1


# Modeled after the piecewise exponentially-damped sine wave:
# y = (1/2)*sin(13pi/2*(2*x))*pow(2, 10 * ((2*x) - 1))      ; [0,0.5)
# y = (1/2)*(sin(-13pi/2*((2x-1)+1))*pow(2,-10(2*x-1)) + 2) ; [0.5, 1]
def ElasticEaseInOut(p):
    if p < 0.5:
        return 0.5 * math.sin(13 * math.pi * p) * math.pow(2, 10 * ((2 * p) - 1))
    return 0.5 * (
        math.sin(-13 * math.pi / 2 * ((2 * p - 1) + 1)) * pow(2, -10 * (2 * p - 1)) + 2
    )


# Modeled after the overshooting cubic y = x^3-x*sin(x*pi)
def BackEaseIn(p):
    return p * p * p - p * math.sin(p * math.pi)


# Modeled after overshooting cubic y = 1-((1-x)^3-(1-x)*sin((1-x)*pi))
def BackEaseOut(p):
    f = 1 - p
    return 1 - (f * f * f - f * math.sin(f * math.pi))


# Modeled after the piecewise overshooting cubic function:
# y = (1/2)*((2x)^3-(2x)*sin(2*x*pi))           ; [0, 0.5)
# y = (1/2)*(1-((1-x)^3-(1-x)*sin((1-x)*pi))+1) ; [0.5, 1]
def BackEaseInOut(p):
    if p < 0.5:
        f = 2 * p
        return 0.5 * (f * f * f - f * math.sin(f * math.pi))
    f = 1 - (2 * p - 1)
    return 0.5 * (1 - (f * f * f - f * math.sin(f * math.pi))) + 0.5


def BounceEaseIn(p):
    return 1 - BounceEaseOut(1 - p)


def BounceEaseOut(p):
    if p < 4 / 11.0:
        return (121 * p * p) / 16.0
    if p < 8 / 11.0:
        return (363 / 40.0 * p * p) - (99 / 10.0 * p) + (17 / 5.0)
    if p < 9 / 10.0:
        return (4356 / 361.0 * p * p) - (35442 / 1805.0 * p) + 16061 / 1805.0
    return (54 / 5.0 * p * p) - (513 / 25.0 * p) + 268 / 25.0


def BounceEaseInOut(p):
    if p < 0.5:
        return 0.5 * BounceEaseIn(p * 2)
    return 0.5 * BounceEaseOut(p * 2 - 1) + 0.5
