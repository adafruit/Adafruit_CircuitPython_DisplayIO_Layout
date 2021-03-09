# SPDX-FileCopyrightText: 2021 Kevin Matocha
#
# SPDX-License-Identifier: MIT

"""
`easing`
================================================================================

Various easing functions in support of the Widget library.

* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

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
def linear_interpolation(pos):
    """
    Easing function for animations: Linear Interpolation.
    """
    return pos


# Modeled after the parabola y = x^2
def quadratic_easein(pos):
    """
    Easing function for animations: Quadratic Ease In
    """
    return pos * pos


# Modeled after the parabola y = -x^2 + 2x
def quadratic_easeout(pos):
    """
    Easing function for animations: Quadratic Ease Out.
    """
    return -(pos * (pos - 2))


# Modeled after the piecewise quadratic
# y = (1/2)((2x)^2)             ; [0, 0.5)
# y = -(1/2)((2x-1)*(2x-3) - 1) ; [0.5, 1]
def quadratic_easeinout(pos):
    """
    Easing function for animations: Quadratic Ease In & Out
    """
    if pos < 0.5:
        return 2 * pos * pos
    return (-2 * pos * pos) + (4 * pos) - 1


# Modeled after the cubic y = x^3
def cubic_easein(pos):
    """
    Easing function for animations: Cubic Ease In
    """
    return pos * pos * pos


# Modeled after the cubic y = (x - 1)^3 + 1
def cubic_easeout(pos):
    """
    Easing function for animations: Cubic Ease Out
    """
    fos = pos - 1
    return fos * fos * fos + 1


# Modeled after the piecewise cubic
# y = (1/2)((2x)^3)       ; [0, 0.5)
# y = (1/2)((2x-2)^3 + 2) ; [0.5, 1]
def cubic_easeinout(pos):
    """
    Easing function for animations: Cubic Ease In & Out
    """
    if pos < 0.5:
        return 4 * pos * pos * pos
    fos = (2 * pos) - 2
    return 0.5 * fos * fos * fos + 1


# Modeled after the quartic x^4
def quartic_easein(pos):
    """
    Easing function for animations: Quartic Ease In
    """
    return pos * pos * pos * pos


# Modeled after the quartic y = 1 - (x - 1)^4
def quartic_easeout(pos):
    """
    Easing function for animations: Quartic Ease Out
    """
    fos = pos - 1
    return fos * fos * fos * (1 - pos) + 1


# Modeled after the piecewise quartic
# y = (1/2)((2x)^4)        ; [0, 0.5)
# y = -(1/2)((2x-2)^4 - 2) ; [0.5, 1]
def quartic_easeinout(pos):
    """
    Easing function for animations: Quartic Ease In & Out
    """
    if pos < 0.5:
        return 8 * pos * pos * pos * pos
    fos = pos - 1
    return -8 * fos * fos * fos * fos + 1


# Modeled after the quintic y = x^5
def quintic_easein(pos):
    """
    Easing function for animations: Quintic Ease In
    """
    return pos * pos * pos * pos * pos


# Modeled after the quintic y = (x - 1)^5 + 1
def quintic_easeout(pos):
    """
    Easing function for animations: Quintic Ease Out
    """
    fos = pos - 1
    return fos * fos * fos * fos * fos + 1


# Modeled after the piecewise quintic
# y = (1/2)((2x)^5)       ; [0, 0.5)
# y = (1/2)((2x-2)^5 + 2) ; [0.5, 1]
def quintic_easeinout(pos):
    """
    Easing function for animations: Quintic Ease In & Out
    """
    if pos < 0.5:
        return 16 * pos * pos * pos * pos * pos
    fos = (2 * pos) - 2
    return 0.5 * fos * fos * fos * fos * fos + 1


# Modeled after quarter-cycle of sine wave
def sine_easein(pos):
    """
    Easing function for animations: Sine Ease In
    """
    return math.sin((pos - 1) * math.pi / 2) + 1


# Modeled after quarter-cycle of sine wave (different phase)
def sine_easeout(pos):
    """
    Easing function for animations: Sine Ease Out
    """
    return math.sin(pos * math.pi / 2)


# Modeled after half sine wave
def sine_easeinout(pos):
    """
    Easing function for animations: Sine Ease In & Out
    """
    return 0.5 * (1 - math.cos(pos * math.pi))


# Modeled after shifted quadrant IV of unit circle
def circular_easein(pos):
    """
    Easing function for animations: Circular Ease In
    """
    return 1 - math.sqrt(1 - (pos * pos))


# Modeled after shifted quadrant II of unit circle
def circular_easeout(pos):
    """
    Easing function for animations: Circular Ease Out
    """
    return math.sqrt((2 - pos) * pos)


# Modeled after the piecewise circular function
# y = (1/2)(1 - sqrt(1 - 4x^2))           ; [0, 0.5)
# y = (1/2)(sqrt(-(2x - 3)*(2x - 1)) + 1) ; [0.5, 1]
def circular_easeinout(pos):
    """
    Easing function for animations: Circular Ease In & Out
    """
    if pos < 0.5:
        return 0.5 * (1 - math.sqrt(1 - 4 * (pos * pos)))
    return 0.5 * (math.sqrt(-((2 * pos) - 3) * ((2 * pos) - 1)) + 1)


# Modeled after the exponential function y = 2^(10(x - 1))
def exponential_easein(pos):
    """
    Easing function for animations: Exponential Ease In
    """
    if pos == 0:
        return pos
    return math.pow(2, 10 * (pos - 1))


# Modeled after the exponential function y = -2^(-10x) + 1
def exponential_easeout(pos):
    """
    Easing function for animations: Exponential Ease Out
    """
    if pos == 1:
        return pos
    return 1 - math.pow(2, -10 * pos)


# Modeled after the piecewise exponential
# y = (1/2)2^(10(2x - 1))         ; [0,0.5)
# y = -(1/2)*2^(-10(2x - 1))) + 1 ; [0.5,1]
def exponential_easeinout(pos):
    """
    Easing function for animations: Exponential Ease In & Out
    """
    if pos in (0.0, 1.0):
        return pos
    if pos < 0.5:
        return 0.5 * math.pow(2, (20 * pos) - 10)
    return (-0.5 * math.pow(2, (-20 * pos) + 10)) + 1


# Modeled after the damped sine wave y = sin(13pi/2*x)*pow(2, 10 * (x - 1))
def elastic_easein(pos):
    """
    Easing function for animations: Elastic Ease In
    """
    return math.sin(13 * pos * math.pi / 2) * math.pow(2, 10 * (pos - 1))


# Modeled after the damped sine wave y = sin(-13pi/2*(x + 1))*pow(2, -10x) + 1
def elastic_easeout(pos):
    """
    Easing function for animations: Elastic Ease Out
    """
    return math.sin(-13 * math.pi / 2 * (pos + 1)) * math.pow(2, -10 * pos) + 1


# Modeled after the piecewise exponentially-damped sine wave:
# y = (1/2)*sin(13pi/2*(2*x))*pow(2, 10 * ((2*x) - 1))      ; [0,0.5)
# y = (1/2)*(sin(-13pi/2*((2x-1)+1))*pow(2,-10(2*x-1)) + 2) ; [0.5, 1]
def elastic_easeinout(pos):
    """
    Easing function for animations: Elastic Ease In & Out
    """
    if pos < 0.5:
        return 0.5 * math.sin(13 * math.pi * pos) * math.pow(2, 10 * ((2 * pos) - 1))
    return 0.5 * (
        math.sin(-13 * math.pi / 2 * ((2 * pos - 1) + 1)) * pow(2, -10 * (2 * pos - 1))
        + 2
    )


# Modeled after the overshooting cubic y = x^3-x*sin(x*pi)
def back_easein(pos):
    """
    Easing function for animations: Back Ease In
    """
    return pos * pos * pos - pos * math.sin(pos * math.pi)


# Modeled after overshooting cubic y = 1-((1-x)^3-(1-x)*sin((1-x)*pi))
def back_easeout(pos):
    """
    Easing function for animations: Back Ease Out
    """
    fos = 1 - pos
    return 1 - (fos * fos * fos - fos * math.sin(fos * math.pi))


# Modeled after the piecewise overshooting cubic function:
# y = (1/2)*((2x)^3-(2x)*sin(2*x*pi))           ; [0, 0.5)
# y = (1/2)*(1-((1-x)^3-(1-x)*sin((1-x)*pi))+1) ; [0.5, 1]
def back_easeinout(pos):
    """
    Easing function for animations: Back Ease In & Out
    """
    if pos < 0.5:
        fos = 2 * pos
        return 0.5 * (fos * fos * fos - fos * math.sin(fos * math.pi))
    fos = 1 - (2 * pos - 1)
    return 0.5 * (1 - (fos * fos * fos - fos * math.sin(fos * math.pi))) + 0.5


def bounce_easein(pos):
    """
    Easing function for animations: Bounce Ease In
    """
    return 1 - bounce_easeout(1 - pos)


def bounce_easeout(pos):
    """
    Easing function for animations: Bounce Ease Out
    """
    if pos < 4 / 11.0:
        return (121 * pos * pos) / 16.0
    if pos < 8 / 11.0:
        return (363 / 40.0 * pos * pos) - (99 / 10.0 * pos) + (17 / 5.0)
    if pos < 9 / 10.0:
        return (4356 / 361.0 * pos * pos) - (35442 / 1805.0 * pos) + 16061 / 1805.0
    return (54 / 5.0 * pos * pos) - (513 / 25.0 * pos) + 268 / 25.0


def bounce_easeinout(pos):
    """
    Easing function for animations: Bounce Ease In & Out
    """
    if pos < 0.5:
        return 0.5 * bounce_easein(pos * 2)
    return 0.5 * bounce_easeout(pos * 2 - 1) + 0.5
