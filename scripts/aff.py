#!/usr/bin/env python3
"""
Affordance-based ontology and core explanation generation.

Implements Algorithm 1 of "Affordance-Based Explanations of Robot Navigation"
(Halilovic and Krivic, ICRA 2025) up to the core explanation:

    objects = ScanNeighborhood(robot, map)
    affordances = ontology[objects]
    core_explanation = Replanning(objects, affordances, map)

AffordanceOntology
    The knowledge base of Section III.  Besides the spatial and semantic
    attributes of an object (position, size, name) it holds the affordances
    of the object: movability and openability.

CoreExplanationGenerator
    Replanning in a perturbed environment (Section IV).  A perturbation alters
    the affordance states of the objects near the robot: a movable object is
    moved away, an openable object is opened.  The path is replanned for each
    perturbation.  A linear regressor is fitted to the perturbations and the
    lengths of their paths, and its coefficients are the attributions of the
    object-affordance pairs.  The pairs with the highest absolute attribution
    that lie along the original path of the robot are the causes of the
    failure or deviation.

Usage
-----
    python3 aff.py          # two scenarios in the library environment

    ontology = AffordanceOntology('ontologies/library/ontology.csv')
    grid = GridMap.from_map_info('ontologies/library/map_info.csv')
    generator = CoreExplanationGenerator(ontology, grid)
    core = generator.generate(robot_pose=(x, y, yaw), goal=(gx, gy),
                              state=RobotState.DEVIATION)
    for pair in core.causes:
        print(pair, pair.attribution)
"""

import csv
import itertools
import math
import os
from enum import Enum

import numpy as np

from planner import GridMap, path_length, plan_path

#: The affordances of the ontology, in the order of its CSV columns.
AFFORDANCES = ('movability', 'openability')


class RobotState(Enum):
    """Navigation states.  Algorithm 1 explains FAILURE and DEVIATION."""

    NORMAL = 'normal'
    FAILURE = 'failure'      # the planner found no path to the goal
    DEVIATION = 'deviation'  # the robot left its initial path


class AffordancePair:
    """
    The 2-tuple <object, affordance> of Section IV.

    Attributes
    ----------
    obj_label : str
        Identifier of the object in the ontology, for example ``chair_1``.
    affordance : str
        ``movability`` or ``openability``.
    attribution : float
        Coefficient of the linear regressor for this pair, in metres of path
        length.  It is negative if fulfilling the affordance (moving the
        object away, opening it) shortens the path or makes the goal reachable.
    on_original_path : bool
        True if the object lies along the original path of the robot.
    """

    def __init__(self, obj_label, affordance):
        self.obj_label = obj_label
        self.affordance = affordance
        self.attribution = 0.0
        self.on_original_path = False

    def __repr__(self):
        return f"<{self.obj_label}, {self.affordance}>"


class CoreExplanation:
    """
    Result of the replanning step, the input of the Visualizer and Verbalizer.

    Attributes
    ----------
    state : RobotState
        FAILURE or DEVIATION.
    robot_pose : tuple(float, float, float)
        x, y in metres and yaw in radians, in the map frame.
    goal : tuple(float, float)
    pairs : list of AffordancePair
        Every pair in the neighbourhood of the robot, sorted by descending
        absolute attribution.
    causes : list of AffordancePair
        The pairs identified as causes of the failure or deviation.
    original_path : list of (x, y) or None
        The path the robot followed before the failure or deviation.
    current_path : list of (x, y) or None
        The path in the current environment.  None for a planning failure.

    An explanation without causes is empty and evaluates to False, which is
    the test ``core_explanation != {}`` of Algorithm 1.
    """

    def __init__(self, state, robot_pose, goal):
        self.state = state
        self.robot_pose = robot_pose
        self.goal = goal
        self.pairs = []
        self.causes = []
        self.original_path = None
        self.current_path = None

    def __bool__(self):
        return bool(self.causes)


class AffordanceOntology:
    """
    Affordance-based ontology of the environment.

    Parameters
    ----------
    csv_path : str or None
        Path to an ontology CSV file (``ontologies/library/ontology.csv``).
        Without a file the ontology starts empty and is filled with
        ``add_object``.

    The position of an object is the centre of its footprint and its size is
    given in metres.  Affordances are binary.  An affordance is fulfilled when
    its action has been carried out: a movable object was moved away, an
    openable object is open.  Every affordance starts as not fulfilled.
    """

    def __init__(self, csv_path=None):
        #: Maps the object identifier to its attributes.
        self.objects = {}
        if csv_path is not None:
            self._load(csv_path)

    def _load(self, csv_path):
        with open(csv_path, newline='') as f:
            for row in csv.DictReader(f):
                label = row['gazebo_label'].strip()
                if not label:
                    continue
                self.add_object(
                    label, row['label'].strip(),
                    float(row['c_map_x']), float(row['c_map_y']),
                    float(row['d_map_x']), float(row['d_map_y']),
                    movability=int(row['movability']),
                    openability=int(row['openability']),
                )

    def add_object(self, obj_label, name, x, y, size_x, size_y,
                   movability=0, openability=0):
        """
        Add an object or replace the one with the same identifier.

        The robot calls this to keep its ontology up to date, for example
        when a human enters its surroundings.
        """
        self.objects[obj_label] = {
            'name': name,
            'x': float(x), 'y': float(y),
            'w': float(size_x), 'h': float(size_y),
            'movability': int(bool(movability)),
            'openability': int(bool(openability)),
            'fulfilled': set(),
        }

    def set_fulfilled(self, obj_label, affordance, fulfilled=True):
        """Record the affordance state of an object, for example an open door."""
        states = self.objects[obj_label]['fulfilled']
        if fulfilled:
            states.add(affordance)
        else:
            states.discard(affordance)

    def get_affordances(self, obj_label):
        """Return the affordances of an object, an empty list if it has none."""
        obj = self.objects.get(obj_label)
        if obj is None:
            return []
        return [aff for aff in AFFORDANCES if obj[aff]]

    def distance(self, obj_label, x, y):
        """Return the distance in metres from the point (x, y) to the footprint."""
        obj = self.objects[obj_label]
        dx = max(abs(x - obj['x']) - obj['w'] / 2.0, 0.0)
        dy = max(abs(y - obj['y']) - obj['h'] / 2.0, 0.0)
        return math.hypot(dx, dy)

    def scan_neighborhood(self, robot_x, robot_y, radius):
        """
        ``ScanNeighborhood`` of Algorithm 1.

        Returns the identifiers of the objects whose footprint is within
        ``radius`` metres of the robot, nearest first.
        """
        nearby = []
        for label in self.objects:
            dist = self.distance(label, robot_x, robot_y)
            if dist <= radius:
                nearby.append((dist, label))
        return [label for _, label in sorted(nearby)]

    def rasterize(self, grid, removed=()):
        """
        Return a copy of ``grid`` with the object footprints marked occupied.

        Objects whose identifier is in ``removed`` are left out, and so are
        objects with a fulfilled affordance in the ontology.
        """
        result = grid.copy()
        for label, obj in self.objects.items():
            if label in removed or obj['fulfilled']:
                continue
            result.add_rectangle(obj['x'], obj['y'], obj['w'], obj['h'])
        return result


class CoreExplanationGenerator:
    """
    Replanning in a perturbed environment with linear attribution.

    Parameters
    ----------
    ontology : AffordanceOntology
    grid : GridMap
        Grid of the environment without the objects of the ontology.  It
        defines the geometry of the map and can hold further static obstacles.
    neighborhood_radius : float
        Radius in metres of the neighbourhood that is scanned for objects.
    robot_radius : float
        Radius in metres of the circular robot footprint used for planning.
    max_perturbations : int
        With n pairs there are 2^n perturbations.  All of them are planned if
        they are at most ``max_perturbations``.  Otherwise this many are drawn
        at random.
    cause_threshold : float
        A pair along the original path is a cause if its absolute attribution
        is at least this fraction of the highest one.
    failure_cost : float or None
        Path length in metres assigned to a perturbation without a path.
        None uses the perimeter of the map, which is longer than a path in
        the library environment.
    seed : int
        Seed of the random perturbations, so that results are reproducible.
    """

    def __init__(self, ontology, grid, neighborhood_radius=3.0,
                 robot_radius=0.3, max_perturbations=256,
                 cause_threshold=0.5, failure_cost=None, seed=0):
        self.ontology = ontology
        self.grid = grid
        self.neighborhood_radius = neighborhood_radius
        self.robot_radius = robot_radius
        self.max_perturbations = max_perturbations
        self.cause_threshold = cause_threshold
        if failure_cost is None:
            failure_cost = 2.0 * (grid.width + grid.height) * grid.resolution
        self.failure_cost = failure_cost
        self.seed = seed

    # ------------------------------------------------------------------
    # Algorithm 1
    # ------------------------------------------------------------------

    def generate(self, robot_pose, goal, state, original_path=None):
        """
        Generate the core explanation for a failure or deviation.

        Parameters
        ----------
        robot_pose : tuple(float, float, float)
            x, y in metres and yaw in radians, in the map frame.
        goal : tuple(float, float)
            Goal position in metres.
        state : RobotState
            Only FAILURE and DEVIATION are explained.
        original_path : list of (x, y) or None
            The path the robot followed before the failure or deviation.  If
            it is not given, the path in the environment with every affordance
            of the neighbourhood fulfilled is used.

        Returns
        -------
        CoreExplanation
            Empty (False) if the state needs no explanation, if no object near
            the robot has an affordance, or if no pair is a cause.
        """
        core = CoreExplanation(state, tuple(robot_pose), tuple(goal))
        if state not in (RobotState.FAILURE, RobotState.DEVIATION):
            return core

        start = (robot_pose[0], robot_pose[1])
        objects = self.ontology.scan_neighborhood(
            start[0], start[1], self.neighborhood_radius)
        pairs = [
            AffordancePair(label, aff)
            for label in objects
            for aff in self.ontology.get_affordances(label)
            if aff not in self.ontology.objects[label]['fulfilled']
        ]
        if not pairs:
            return core

        perturbations = self._perturbations(len(pairs))
        paths = {}
        for row in perturbations:
            removed = {pairs[j].obj_label for j, bit in enumerate(row) if bit}
            env = self.ontology.rasterize(self.grid, removed)
            paths[row] = plan_path(env, start, goal, self.robot_radius)

        lengths = np.array([
            self.failure_cost if paths[row] is None else path_length(paths[row])
            for row in perturbations
        ])
        attributions = self._linear_regression(
            np.array(perturbations, dtype=float), lengths)
        for pair, value in zip(pairs, attributions):
            pair.attribution = float(value)

        nothing_fulfilled = (0,) * len(pairs)
        all_fulfilled = (1,) * len(pairs)
        core.current_path = paths[nothing_fulfilled]
        core.original_path = (original_path if original_path is not None
                              else paths[all_fulfilled])
        core.pairs = sorted(pairs, key=lambda p: -abs(p.attribution))
        core.causes = self._select_causes(core.pairs, core.original_path)
        return core

    # ------------------------------------------------------------------
    # Steps of the replanning
    # ------------------------------------------------------------------

    def _perturbations(self, n_pairs):
        """
        Return the perturbations as tuples of n_pairs bits.

        Bit j is 1 if the affordance of pair j is fulfilled in the perturbed
        environment.  The current environment (all 0) and the environment
        with every affordance fulfilled (all 1) are always included.
        """
        if 2 ** n_pairs <= self.max_perturbations:
            return list(itertools.product((0, 1), repeat=n_pairs))
        rng = np.random.default_rng(self.seed)
        rows = {(0,) * n_pairs, (1,) * n_pairs}
        while len(rows) < self.max_perturbations:
            rows.add(tuple(int(b) for b in rng.integers(0, 2, size=n_pairs)))
        return sorted(rows)

    @staticmethod
    def _linear_regression(perturbations, lengths):
        """
        Fit ``length = intercept + sum_j coefficient_j * bit_j`` by least squares.

        Returns the coefficients, one per pair.  This is the interpretable
        model of Section IV.
        """
        design = np.column_stack([perturbations, np.ones(len(perturbations))])
        solution, _, _, _ = np.linalg.lstsq(design, lengths, rcond=None)
        return solution[:-1]

    def _select_causes(self, pairs, original_path):
        """
        Return the pairs with the highest absolute attribution along the path.

        An object with two affordances contributes one pair, the one with the
        higher absolute attribution, since the explanation shows the
        affordance that influences the path planning.
        """
        if not original_path:
            return []
        for pair in pairs:
            pair.on_original_path = self._on_path(pair.obj_label, original_path)

        best = {}
        for pair in pairs:  # sorted by descending absolute attribution
            if pair.on_original_path and pair.obj_label not in best:
                best[pair.obj_label] = pair
        candidates = list(best.values())
        if not candidates:
            return []
        highest = abs(candidates[0].attribution)
        if highest < 1e-9:
            return []
        return [pair for pair in candidates
                if abs(pair.attribution) >= self.cause_threshold * highest]

    def _on_path(self, obj_label, path):
        """True if the robot footprint on the path touches the object footprint."""
        reach = self.robot_radius + self.grid.resolution
        return any(self.ontology.distance(obj_label, x, y) <= reach
                   for x, y in path)


# ----------------------------------------------------------------------
# Library environment
# ----------------------------------------------------------------------

def package_path(*parts):
    """
    Return the path of a data file of the package.

    The installed package keeps its data in the share directory.  When the
    scripts are run from a checkout, the data lie next to the scripts folder.
    """
    checkout = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    if os.path.isdir(os.path.join(checkout, 'ontologies')):
        return os.path.join(checkout, *parts)
    from ament_index_python.packages import get_package_share_directory
    return os.path.join(
        get_package_share_directory('affordance_based_explanations'), *parts)


def load_library():
    """Return the ontology and the empty grid of the library environment."""
    ontology = AffordanceOntology(
        package_path('ontologies', 'library', 'ontology.csv'))
    grid = GridMap.from_map_info(
        package_path('ontologies', 'library', 'map_info.csv'))
    return ontology, grid


#: Two situations in the library environment, used by the demos and the tests.
#: Deviation: chair_16 stands in the gap between bookshelf_10 and bookshelf_9,
#: so the robot goes around a bookshelf.  Failure: the goal is the place of
#: chair_1 between the wall and table_4, so no path exists.
LIBRARY_SCENARIOS = {
    'deviation': {
        'state': RobotState.DEVIATION,
        'robot_pose': (-6.45, 3.52, 0.0),
        'goal': (-5.0, 3.52),
        'task': 'reach the next aisle',
    },
    'failure': {
        'state': RobotState.FAILURE,
        'robot_pose': (-9.6, 1.9, -math.pi / 2.0),
        'goal': (-9.6, 0.67),
        'task': 'reach the reading place',
    },
}


def main():
    ontology, grid = load_library()
    generator = CoreExplanationGenerator(ontology, grid)
    for name, scenario in LIBRARY_SCENARIOS.items():
        core = generator.generate(scenario['robot_pose'], scenario['goal'],
                                  scenario['state'])
        print(f"=== {name} ===")
        for pair in core.pairs:
            mark = 'cause' if pair in core.causes else ''
            print(f"  {str(pair):28s} attribution = {pair.attribution:8.3f} m"
                  f"  {mark}")
        if not core:
            print("  no affordance-based explanation")


if __name__ == '__main__':
    main()
