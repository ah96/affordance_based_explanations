"""
Tests of the explanation pipeline.  They need numpy and no ROS.

    python3 -m pytest test

Each test is named after the statement of the paper or of the README that it
checks.  The scenarios in a corridor are built in the test, since the library
ontology holds no openable object.
"""

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from aff import (AffordanceOntology, CoreExplanationGenerator,  # noqa: E402
                 LIBRARY_SCENARIOS, RobotState, load_library)
from planner import GridMap, path_length, plan_path  # noqa: E402
from qsr import QSR, relatum_angle  # noqa: E402
import verbalize  # noqa: E402

PI = math.pi


def paper_qsr():
    """The modified single-cross calculus of the paper."""
    return QSR(binary_qsr_choice=2, ternary_qsr_choice=2, R=1.0)


# ----------------------------------------------------------------------
# Qualitative spatial reasoning (Section III, Fig. 4b)
# ----------------------------------------------------------------------

@pytest.mark.parametrize('angle, relation', [
    (PI / 2, 'front'), (-PI / 2, 'back'), (0.0, 'right'),
    (PI, 'left'), (-PI, 'left'),
    (PI / 4, 'front'), (3 * PI / 4, 'left'),
    (-PI / 4, 'right'), (-3 * PI / 4, 'back'),
])
def test_modified_single_cross_has_four_quadrants(angle, relation):
    assert paper_qsr().getBinaryQsrValue(angle) == relation


@pytest.mark.parametrize('yaw, obj, relation', [
    (0.0, (1.0, 0.0), 'front'), (0.0, (0.0, 1.0), 'left'),
    (0.0, (0.0, -1.0), 'right'), (0.0, (-1.0, 0.0), 'back'),
    (PI / 2, (0.0, 1.0), 'front'), (PI / 2, (1.0, 0.0), 'right'),
    (PI, (-1.0, 0.0), 'front'), (-PI / 2, (1.0, 0.0), 'left'),
])
def test_relation_follows_the_heading_of_the_robot(yaw, obj, relation):
    angle = relatum_angle(0.0, 0.0, yaw, obj[0], obj[1])
    assert paper_qsr().getBinaryQsrValue(angle) == relation


def test_every_angle_has_a_relation_in_every_calculus():
    for choice in range(4):
        qsr = QSR(choice, choice, 1.0)
        for step in range(-180, 181):
            angle = math.radians(step)
            assert qsr.getBinaryQsrValue(angle) in qsr.binary_qsr_dict
            assert qsr.getTernaryQsrValue(0.5, angle, 1.0) in qsr.ternary_qsr_dict
    qsr = QSR(2, 4, 1.0)
    for step in range(-180, 181):
        for distance in (0.5, 2.0):
            value = qsr.getTernaryQsrValue(distance, math.radians(step), 1.0)
            assert value in qsr.ternary_qsr_dict


# ----------------------------------------------------------------------
# Planner
# ----------------------------------------------------------------------

def test_planner_finds_the_straight_path_on_an_empty_grid():
    grid = GridMap(0.05, 100, 40, 0.0, 0.0)
    path = plan_path(grid, (0.5, 1.0), (4.5, 1.0), robot_radius=0.3)
    assert path_length(path) == pytest.approx(4.0, abs=0.05)


def test_planner_reports_no_path_when_the_corridor_is_closed():
    grid = GridMap(0.05, 100, 40, 0.0, 0.0)
    grid.add_rectangle(2.5, 1.0, 0.2, 2.0)
    assert plan_path(grid, (0.5, 1.0), (4.5, 1.0), robot_radius=0.3) is None


# ----------------------------------------------------------------------
# Core explanation by replanning (Algorithm 1, Section IV)
# ----------------------------------------------------------------------

def corridor():
    """A corridor of 6 m by 1 m along x, closed by walls."""
    ontology = AffordanceOntology()
    ontology.add_object('wall_south', 'wall', 3.0, -0.05, 6.2, 0.1)
    ontology.add_object('wall_north', 'wall', 3.0, 1.05, 6.2, 0.1)
    ontology.add_object('wall_west', 'wall', -0.05, 0.5, 0.1, 1.2)
    ontology.add_object('wall_east', 'wall', 6.05, 0.5, 0.1, 1.2)
    grid = GridMap(0.05, 130, 30, -0.2, -0.2)
    return ontology, grid


def failure_scenario():
    """
    The failure example of Section IV-B: the robot is to fetch a book, and a
    chair and a closed cabinet in front of it block the path.  A second chair
    and a trash bin stand behind the robot, off the path.
    """
    ontology, grid = corridor()
    ontology.add_object('chair_1', 'chair', 2.5, 0.5, 0.4, 0.4, movability=1)
    ontology.add_object('cabinet', 'cabinet', 3.5, 0.5, 0.5, 1.0, openability=1)
    ontology.add_object('chair_2', 'chair', 0.3, 0.8, 0.3, 0.3, movability=1)
    ontology.add_object('trash_bin', 'trash bin', 0.3, 0.2, 0.3, 0.3, movability=1)
    generator = CoreExplanationGenerator(ontology, grid, robot_radius=0.25)
    core = generator.generate((1.2, 0.5, 0.0), (5.0, 0.5), RobotState.FAILURE)
    return ontology, core


def test_failure_causes_are_the_chair_and_the_closed_cabinet():
    _, core = failure_scenario()
    assert core.current_path is None
    assert core.original_path is not None
    assert {(p.obj_label, p.affordance) for p in core.causes} == {
        ('chair_1', 'movability'), ('cabinet', 'openability')}


def test_objects_off_the_path_get_no_attribution():
    _, core = failure_scenario()
    by_label = {p.obj_label: p for p in core.pairs}
    assert by_label['chair_1'].attribution < -1.0
    assert by_label['cabinet'].attribution < -1.0
    assert abs(by_label['chair_2'].attribution) < 1e-6
    assert abs(by_label['trash_bin'].attribution) < 1e-6


def test_failure_scenario_gives_the_three_textual_explanations():
    ontology, core = failure_scenario()
    sentences = {
        kind: verbalize.verbalize_explanation(
            core, ontology, paper_qsr(), kind, task='fetch a book')
        for kind in ('descriptive', 'suggestive', 'counterfactual')
    }
    assert sentences['descriptive'] == (
        "I failed to fetch a book because the chair and the closed cabinet, "
        "both in front of me, blocked my path.")
    assert sentences['suggestive'] == (
        "Dear human, please move the chair and open the cabinet, "
        "both in front of me, so I can fetch a book.")
    assert sentences['counterfactual'] == (
        "If the chair in front of me was not there and the cabinet in front "
        "of me was open, I would not fail to fetch a book.")


def test_normal_state_and_empty_neighborhood_give_no_explanation():
    ontology, grid = corridor()
    generator = CoreExplanationGenerator(ontology, grid, robot_radius=0.25)
    assert not generator.generate((1.2, 0.5, 0.0), (5.0, 0.5), RobotState.NORMAL)
    # No object near the robot has an affordance.
    assert not generator.generate((1.2, 0.5, 0.0), (5.0, 0.5), RobotState.FAILURE)


def test_an_opened_object_is_no_longer_a_cause():
    ontology, _ = failure_scenario()
    _, grid = corridor()
    ontology.set_fulfilled('cabinet', 'openability')
    generator = CoreExplanationGenerator(ontology, grid, robot_radius=0.25)
    core = generator.generate((1.2, 0.5, 0.0), (5.0, 0.5), RobotState.FAILURE)
    assert [p.obj_label for p in core.causes] == ['chair_1']


# ----------------------------------------------------------------------
# Textual explanations (Section IV-B)
# ----------------------------------------------------------------------

def test_deviation_sentences_of_the_paper():
    """The deviation example: a human and a chair, both right of the robot."""
    causes = [('human', 'movability', 'right'), ('chair', 'movability', 'right')]
    assert verbalize.explanation_sentence('deviation', causes, 'suggestive') == (
        "Dear human, please move yourself and move the chair right of me so I "
        "can decrease my deviation and proceed to navigate more smoothly.")
    assert verbalize.explanation_sentence('deviation', causes, 'counterfactual') == (
        "If the human and the chair, right of me, were not there, "
        "I would not deviate from my path.")
    causes.reverse()
    assert verbalize.explanation_sentence('deviation', causes, 'descriptive') == (
        "I deviated from my initial path because the chair and the human, "
        "both right of me, blocked it.")


def test_failure_sentences_of_the_paper():
    causes = [('chair', 'movability', 'front'), ('cabinet', 'openability', 'front')]
    assert verbalize.explanation_sentence(
        'failure', causes, 'suggestive', task='fetch a book') == (
        "Dear human, please move the chair and open the cabinet, "
        "both in front of me, so I can fetch a book.")
    assert verbalize.explanation_sentence(
        'failure', causes, 'counterfactual', task='fetch the book') == (
        "If the chair in front of me was not there and the cabinet in front "
        "of me was open, I would not fail to fetch the book.")


def test_objects_in_different_directions_get_their_own_relation():
    causes = [('chair', 'movability', 'front'), ('human', 'movability', 'left')]
    assert verbalize.explanation_sentence('deviation', causes, 'descriptive') == (
        "I deviated from my initial path because the chair in front of me "
        "and the human left of me blocked it.")


# ----------------------------------------------------------------------
# Library environment
# ----------------------------------------------------------------------

def test_library_ontology_has_forty_objects_and_thirteen_movable_chairs():
    ontology, grid = load_library()
    assert len(ontology.objects) == 40
    movable = [label for label in ontology.objects
               if ontology.get_affordances(label) == ['movability']]
    assert len(movable) == 13
    assert all(ontology.objects[label]['name'] == 'chair' for label in movable)
    assert (grid.width, grid.height, grid.resolution) == (210, 310, 0.05)


def test_library_deviation_is_caused_by_the_chair_between_the_bookshelves():
    ontology, grid = load_library()
    scenario = LIBRARY_SCENARIOS['deviation']
    core = CoreExplanationGenerator(ontology, grid).generate(
        scenario['robot_pose'], scenario['goal'], scenario['state'])
    assert [str(p) for p in core.causes] == ['<chair_16, movability>']
    assert path_length(core.current_path) > path_length(core.original_path) + 1.0
    assert verbalize.verbalize_explanation(
        core, ontology, paper_qsr(), 'counterfactual') == (
        "If the chair in front of me was not there, "
        "I would not deviate from my path.")


def test_library_failure_is_caused_by_the_chair_at_the_goal():
    ontology, grid = load_library()
    scenario = LIBRARY_SCENARIOS['failure']
    core = CoreExplanationGenerator(ontology, grid).generate(
        scenario['robot_pose'], scenario['goal'], scenario['state'])
    assert core.current_path is None
    assert [str(p) for p in core.causes] == ['<chair_1, movability>']
    assert verbalize.verbalize_explanation(
        core, ontology, paper_qsr(), 'suggestive', task=scenario['task']) == (
        "Dear human, please move the chair in front of me "
        "so I can reach the reading place.")


# ----------------------------------------------------------------------
# Verbalization space experiment (Section VI-B, Fig. 8)
# ----------------------------------------------------------------------

#: Averages printed by the script of the experiment, for a few combinations.
EXPERIMENT_AVERAGES = {
    ('coordinates', 'general picture', 'no verb'): 57.6,
    ('coordinates', 'summary', 'counterfactual'): 305.0,
    ('coordinates', 'detailed narrative', 'descriptive'): 379.5,
    ('angles/distances', 'detailed narrative', 'suggestive'): 179.6,
    ('right/left', 'summary', 'no verb'): 143.8,
    ('semantic annotations', 'summary', 'suggestive'): 109.2,
    ('semantic annotations', 'detailed narrative', 'counterfactual'): 125.0,
    ('semantic annotations', 'detailed narrative',
     'descriptive/suggestive/counterfactual'): 217.5,
}


def test_word_counts_equal_those_of_the_experiment():
    stats = verbalize.compute_word_count_stats()
    assert len(stats) == 4 * 3 * 8
    for key, words in EXPERIMENT_AVERAGES.items():
        assert stats[key] == pytest.approx(words, abs=1e-9)


def test_counterfactuals_have_the_most_words_of_the_explanation_levels():
    stats = verbalize.compute_word_count_stats()
    for a in verbalize.ABSTRACTION_LEVELS:
        for s in verbalize.SPECIFICITY_LEVELS:
            words = {e: stats[(a, s, e)]
                     for e in verbalize.TABLE_EXPLANATION_LEVELS}
            assert max(words, key=words.get) == 'counterfactual'


def test_more_abstraction_means_fewer_words_except_for_the_general_picture():
    table = verbalize.figure_tables(
        verbalize.compute_word_count_stats())['abstraction/specificity']
    first, last = verbalize.ABSTRACTION_LEVELS[0], verbalize.ABSTRACTION_LEVELS[-1]
    for s in ('summary', 'detailed narrative'):
        assert table[(first, s)] > table[(last, s)]
    general = [table[(a, 'general picture')] for a in verbalize.ABSTRACTION_LEVELS]
    assert max(general) - min(general) < 5.0


def test_locality_restricts_the_verbalized_actions():
    plan = verbalize.PLANS[0]
    args = ('semantic annotations', 'summary', 'descriptive')
    complete = verbalize.verbalize_plan(plan, args[0], 'complete plan', *args[1:])
    assert len(complete) == len(plan)
    part = verbalize.verbalize_plan(plan, args[0], 'range of actions', *args[1:],
                                    locality_range=(0, 3))
    assert part == complete[:3]
    doors = verbalize.verbalize_plan(plan, args[0], 'action or object', *args[1:],
                                     locality_object='door_3')
    assert len(doors) == 3
    opens = verbalize.verbalize_plan(plan, args[0], 'action or object', *args[1:],
                                     locality_action='open')
    assert opens == ['tiago is opening door_3 ']
