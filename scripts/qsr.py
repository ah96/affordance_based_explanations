#!/usr/bin/env python3
"""
Qualitative Spatial Reasoning (QSR) for affordance-based explanations.

Implements the modified single-cross calculus of Section III of
"Affordance-Based Explanations of Robot Navigation" (Halilovic and Krivic,
ICRA 2025).  The single-cross calculus of Freksa (1992) is simplified into
four quadrants around the robot (the relatum): left, right, front and back.
An object (the referent) gets the label of the quadrant it lies in, which
gives explanations such as "Please move the chair in front of me."

Calculi
-------
The ``QSR`` class holds several calculi, selected by an integer.

  binary_qsr_choice
    0 : left / right
    1 : front / back
    2 : left / right / front / back      (the calculus of the paper)
    3 : left/front, right/front, left/back, right/back

  ternary_qsr_choice
    0 to 3 : as above
    4 : calculus 2 with a close (c) or distant (d) prefix: cf, df, cl, ...

Angles
------
The two families use different angle conventions, both in radians in the
range from -pi to pi.

  Binary calculi take the angle in a frame whose x axis points to the right
  of the robot and whose y axis points ahead of it:
      0 = right,  +pi/2 = front,  +-pi = left,  -pi/2 = back.

  Ternary calculi take the bearing from the heading of the robot:
      0 = front,  +pi/2 = left,  +-pi = back,  -pi/2 = right.

``relatum_angle`` converts a robot pose and an object position in the map
frame into the angle of the binary calculi.
"""

import math

PI = math.pi


def relatum_angle(robot_x, robot_y, robot_yaw, obj_x, obj_y):
    """
    Return the angle of an object in the frame of the binary calculi.

    The frame has its origin at the robot, its y axis along the heading of
    the robot and its x axis to the right of the robot.  The result lies in
    the range from -pi (included) to pi (excluded).
    """
    bearing = math.atan2(obj_y - robot_y, obj_x - robot_x) - robot_yaw
    angle = bearing + PI / 2.0
    return (angle + PI) % (2.0 * PI) - PI


class QSR(object):
    """
    Qualitative Spatial Reasoning calculator.

    Computes a qualitative directional label for an object given the bearing
    angle from the robot to that object.  The calculus can be binary
    (direction only) or ternary (direction + distance band).

    Parameters
    ----------
    binary_qsr_choice : int
        Selects the binary calculus variant (0 to 3), see the module docstring.
    ternary_qsr_choice : int
        Selects the ternary calculus variant (0 to 4), see the module docstring.
    R : float
        Distance threshold (metres) for the close / distant distinction
        in ternary calculus 4.
    """

    def __init__(self, binary_qsr_choice, ternary_qsr_choice, R):
        self.binary_qsr_choice = binary_qsr_choice
        self.ternary_qsr_choice = ternary_qsr_choice
        self.R = R
        self.PI = PI

        self.defineBinaryQsrCalculus()
        self.defineTernaryQsrCalculus()

    # ------------------------------------------------------------------
    # Binary calculus
    # ------------------------------------------------------------------

    def defineBinaryQsrCalculus(self):
        """Initialise the label → index mapping for the selected binary calculus."""
        if self.binary_qsr_choice == 0:
            # 1-D left / right split along the y-axis.
            self.binary_qsr_dict = {'left': 0, 'right': 1}

        elif self.binary_qsr_choice == 1:
            # 1-D front / back split along the x-axis.
            self.binary_qsr_dict = {'front': 0, 'back': 1}

        elif self.binary_qsr_choice == 2:
            # 4-direction split: the paper's modified single-cross calculus.
            # Quadrant boundaries are at ±π/4 and ±3π/4.
            self.binary_qsr_dict = {'left': 0, 'right': 1, 'front': 2, 'back': 3}

        elif self.binary_qsr_choice == 3:
            # Diagonal quadrants, useful when left/right and front/back
            # are equally important simultaneously.
            self.binary_qsr_dict = {
                'left/front':  0,
                'right/front': 1,
                'left/back':   2,
                'right/back':  3,
            }

        # Inverse dict used to convert index → label in NLP generation.
        self.binary_qsr_dict_inv = {v: k for k, v in self.binary_qsr_dict.items()}

    def getBinaryQsrValue(self, angle):
        """
        Map a bearing angle to a qualitative direction label.

        Parameters
        ----------
        angle : float
            Angle of the object in radians, in the frame of the binary
            calculi (0 = right, +pi/2 = front); see the module docstring.

        Returns
        -------
        str
            One of the labels defined by the selected binary calculus,
            e.g. ``"front"``, ``"left"``, ``"right"``, ``"back"``.
        """
        value = ''

        if self.binary_qsr_choice == 0:
            # Objects to the right of the robot's heading (−π/2 to +π/2).
            if -self.PI / 2 <= angle < self.PI / 2:
                value += 'right'
            elif self.PI / 2 <= angle <= self.PI or -self.PI <= angle < -self.PI / 2:
                value += 'left'

        elif self.binary_qsr_choice == 1:
            # Objects ahead of the robot (0 to +π).
            if 0 <= angle <= self.PI:
                value += 'front'
            elif -self.PI <= angle < 0:
                value += 'back'

        elif self.binary_qsr_choice == 2:
            # 4-direction split used in the paper.
            # The front sector is centred on +y (robot's heading).
            if 3 * self.PI / 4 <= angle <= self.PI or -self.PI <= angle < -3 * self.PI / 4:
                value += 'left'
            elif -self.PI / 4 <= angle < self.PI / 4:
                value += 'right'
            elif self.PI / 4 <= angle < 3 * self.PI / 4:
                value += 'front'
            elif -3 * self.PI / 4 <= angle < -self.PI / 4:
                value += 'back'

        elif self.binary_qsr_choice == 3:
            # Diagonal quadrants: each occupies a π/2 sector.
            if 0 <= angle < self.PI / 2:
                value += 'right/front'
            elif self.PI / 2 <= angle <= self.PI:
                value += 'left/front'
            elif -self.PI / 2 <= angle < 0:
                value += 'right/back'
            elif -self.PI <= angle < -self.PI / 2:
                value += 'left/back'

        return value

    # ------------------------------------------------------------------
    # Ternary calculus
    # ------------------------------------------------------------------

    def defineTernaryQsrCalculus(self):
        """Initialise the label → index mapping for the selected ternary calculus."""
        if self.ternary_qsr_choice == 0:
            self.ternary_qsr_dict = {'left': 0, 'right': 1}

        elif self.ternary_qsr_choice == 1:
            self.ternary_qsr_dict = {'front': 0, 'back': 1}

        elif self.ternary_qsr_choice == 2:
            # The four quadrants of binary choice 2.
            self.ternary_qsr_dict = {'left': 0, 'right': 1, 'front': 2, 'back': 3}

        elif self.ternary_qsr_choice == 3:
            self.ternary_qsr_dict = {
                'left/front':  0,
                'right/front': 1,
                'left/back':   2,
                'right/back':  3,
            }

        elif self.ternary_qsr_choice == 4:
            # Combines close (c) / distant (d) with 4 directions → 8 relations.
            # Labelled as: c/d prefix + direction suffix, e.g. 'cf', 'dl'.
            self.ternary_qsr_dict = {
                'cl': 0, 'dl': 1,
                'cr': 2, 'dr': 3,
                'cb': 4, 'db': 5,
                'cf': 6, 'df': 7,
            }

        self.ternary_qsr_dict_inv = {v: k for k, v in self.ternary_qsr_dict.items()}

    def getTernaryQsrValue(self, r, angle, R):
        """
        Map a distance + bearing to a ternary qualitative relation.

        Parameters
        ----------
        r : float
            Distance from robot to object in metres.
        angle : float
            Bearing of the object from the heading of the robot in radians
            (0 = front, +pi/2 = left); see the module docstring.
        R : float
            Close / distant threshold (metres); used only for choice 4.

        Returns
        -------
        str
            Qualitative relation label, e.g. ``"cf"`` (close, front) or
            ``"dl"`` (distant, left).
        """
        value = ''

        if self.ternary_qsr_choice == 0:
            if -self.PI <= angle < 0:
                value += 'right'
            else:
                value += 'left'

        elif self.ternary_qsr_choice == 1:
            if -self.PI / 2 <= angle < self.PI / 2:
                value += 'front'
            else:
                value += 'back'

        elif self.ternary_qsr_choice == 2:
            # The four quadrants, with the bearing measured from the heading.
            if -self.PI / 4 <= angle <= self.PI / 4:
                value += 'front'
            elif self.PI / 4 < angle < 3 * self.PI / 4:
                value += 'left'
            elif 3 * self.PI / 4 <= angle or angle <= -3 * self.PI / 4:
                value += 'back'
            elif -3 * self.PI / 4 < angle < -self.PI / 4:
                value += 'right'

        elif self.ternary_qsr_choice == 3:
            if 0 <= angle < self.PI / 2:
                value += 'left/front'
            elif self.PI / 2 <= angle <= self.PI:
                value += 'left/back'
            elif -self.PI / 2 <= angle < 0:
                value += 'right/front'
            elif -self.PI <= angle < -self.PI / 2:
                value += 'right/back'

        elif self.ternary_qsr_choice == 4:
            # Prepend 'c' (close) or 'd' (distant) based on metric distance.
            value += 'c' if r <= R else 'd'

            # Append the first letter of the direction, as in the dictionary.
            if -self.PI / 4 <= angle <= self.PI / 4:
                value += 'f'
            elif self.PI / 4 < angle < 3 * self.PI / 4:
                value += 'l'
            elif 3 * self.PI / 4 <= angle or angle <= -3 * self.PI / 4:
                value += 'b'
            elif -3 * self.PI / 4 < angle < -self.PI / 4:
                value += 'r'

        return value
