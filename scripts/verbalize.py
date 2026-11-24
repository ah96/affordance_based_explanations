#!/usr/bin/env python3
"""
Textual affordance-based explanations and the Verbalization Space.

Implements two parts of "Affordance-Based Explanations of Robot Navigation"
(Halilovic and Krivic, ICRA 2025).

Textual explanations (Section IV-B)
    ``verbalize_explanation`` turns a core explanation into a descriptive,
    suggestive or counterfactual sentence in the first person.  This is
    ``Verbalize(core_explanation, QSR)`` of Algorithm 1.  The QSR gives the
    spatial relation of each object to the robot ("in front of me").

Verbalization Space (Section IV-C, Table I)
    ``verbalize_plan`` verbalizes a task plan under four parameters.

    Abstraction (A)   how places and objects are referred to
        A1  coordinates             A2  angles/distances
        A3  right/left              A4  semantic annotations
    Locality (L)      which part of the plan is verbalized
        L1  complete plan           L2  range of actions
        L3  action or object
    Specificity (S)   how much detail an action gets
        S1  general picture         S2  summary
        S3  detailed narrative
    Explanation (E)   how failure and deviation actions are verbalized
        E1  no verbalization as an affordance-based explanation
        E2  descriptive             E3  suggestive
        E4  counterfactual

Verbalization space experiment (Section VI-B)
    ``compute_word_count_stats`` verbalizes the ten library plans under the
    combinations of A, S and E and returns the average number of words per
    plan.  ``figure_tables`` reduces them to the three tables of Fig. 8.

Usage
-----
    python3 verbalize.py        # prints the tables of the experiment
"""

# ---------------------------------------------------------------------------
# The ten plans of the library domain used in the experiment (Section VI-B).
# An action is a string of tokens separated by spaces:
#   goto_waypoint <robot> <from> <to>
#   pass_through  <robot> <object>
#   pass_between  <robot> <object> <object>
#   open          <robot> <object>
#   fetch         <robot> <item> <place>
#   ask_for_help  <robot> <human>
#   failure       <robot> <failed action> <object> <place> <reason>
#   deviation     <robot> <object>
# ---------------------------------------------------------------------------

_RAW_PLANS = [
    [
        "goto_waypoint tiago social_room corridor",
        "failure tiago passing door_3 doorway closed",
        "open tiago door_3",
        "pass_through tiago door_3",
        "goto_waypoint tiago corridor common_zone",
        "goto_waypoint tiago common_zone book_zone",
        "goto_waypoint tiago book_zone bookshelf_2",
        "deviation tiago human_1",
        "fetch tiago book bookshelf_2",
        "failure tiago fetching book bookshelf_2 too_high",
        "ask_for_help tiago human_5",
        "goto_waypoint tiago bookshelf_2 common_zone",
        "goto_waypoint tiago common_zone corridor",
        "goto_waypoint tiago corridor social_room",
    ],
    [
        "goto_waypoint tiago reading_zone common_zone",
        "deviation tiago human_13",
        "goto_waypoint tiago common_zone book_zone",
        "goto_waypoint tiago book_zone bookshelf_14",
        "pass_between tiago bookshelf_8 bookshelf_12",
        "pass_between tiago bookshelf_9 bookshelf_13",
        "fetch tiago book bookshelf_14",
        "goto_waypoint tiago book_zone bookshelf_14",
        "pass_between tiago bookshelf_9 bookshelf_13",
        "pass_between tiago bookshelf_8 bookshelf_12",
        "goto_waypoint tiago book_zone common_zone",
        "deviation tiago human_15",
        "goto_waypoint tiago common_zone book_zone",
    ],
    [
        "goto_waypoint tiago computer_room corridor",
        "pass_through tiago door_2",
        "goto_waypoint tiago corridor common_zone",
        "goto_waypoint tiago common_zone book_zone",
        "goto_waypoint tiago book_zone bookshelf_5",
        "deviation tiago human_2",
        "fetch tiago book bookshelf_5",
        "failure tiago fetching book bookshelf_5 too_high",
        "ask_for_help tiago human_7",
        "goto_waypoint tiago bookshelf_2 common_zone",
        "goto_waypoint tiago common_zone corridor",
        "goto_waypoint tiago corridor computer_room",
        "failure tiago passing door_2 doorway closed",
        "open tiago door_2",
    ],
    [
        "goto_waypoint tiago reading_zone common_zone",
        "deviation tiago human_19",
        "goto_waypoint tiago common_zone book_zone",
        "goto_waypoint tiago book_zone bookshelf_8",
        "pass_between tiago bookshelf_6 bookshelf_11",
        "pass_between tiago bookshelf_5 bookshelf_7",
        "fetch tiago book bookshelf_8",
        "goto_waypoint tiago book_zone bookshelf_8",
        "pass_between tiago bookshelf_5 bookshelf_7",
        "pass_between tiago bookshelf_6 bookshelf_11",
        "goto_waypoint tiago book_zone common_zone",
        "deviation tiago human_4",
        "goto_waypoint tiago common_zone book_zone",
    ],
    [
        "goto_waypoint tiago social_room corridor",
        "pass_through tiago door_3",
        "goto_waypoint tiago corridor common_zone",
        "goto_waypoint tiago common_zone book_zone",
        "goto_waypoint tiago book_zone bookshelf_5",
        "deviation tiago human_5",
        "fetch tiago book bookshelf_5",
        "failure tiago fetching book bookshelf_5 too_high",
        "ask_for_help tiago human_6",
        "goto_waypoint tiago bookshelf_5 common_zone",
        "goto_waypoint tiago common_zone corridor",
        "goto_waypoint tiago corridor social_room",
        "failure tiago passing door_3 doorway closed",
        "open tiago door_3",
    ],
    [
        "goto_waypoint tiago computer_room corridor",
        "failure tiago passing door_2 doorway closed",
        "open tiago door_2",
        "pass_through tiago door_2",
        "goto_waypoint tiago corridor common_zone",
        "goto_waypoint tiago common_zone book_zone",
        "goto_waypoint tiago book_zone bookshelf_9",
        "deviation tiago human_9",
        "fetch tiago book bookshelf_9",
        "failure tiago fetching book bookshelf_9 too_low",
        "ask_for_help tiago human_9",
        "goto_waypoint tiago bookshelf_9 common_zone",
        "goto_waypoint tiago common_zone corridor",
        "goto_waypoint tiago corridor computer_room",
    ],
    [
        "goto_waypoint tiago information_desk_zone corridor",
        "deviation tiago human_9",
        "deviation tiago human_8",
        "goto_waypoint tiago common_zone book_zone",
        "goto_waypoint tiago book_zone bookshelf_9",
        "pass_between tiago bookshelf_6 bookshelf_11",
        "pass_between tiago bookshelf_7 bookshelf_10",
        "fetch tiago book bookshelf_9",
        "failure tiago fetching book bookshelf_9 too_high",
        "ask_for_help tiago human_3",
        "goto_waypoint tiago bookshelf_9 book_zone",
        "goto_waypoint tiago book_zone common_zone",
        "goto_waypoint tiago common_zone reading_zone",
        "failure tiago returning book information_desk_zone wrong_zone",
        "goto_waypoint tiago reading_zone common_zone",
        "goto_waypoint tiago common_zone information_desk_zone",
    ],
    [
        "goto_waypoint tiago social_room corridor",
        "pass_through tiago door_3",
        "goto_waypoint tiago corridor common_zone",
        "failure tiago goto_waypoint common_zone common_zone chair_2",
        "ask_for_help tiago human_9",
        "goto_waypoint tiago common_zone information_desk_zone",
        "deviation tiago human_8",
        "fetch tiago book information_desk",
        "goto_waypoint tiago information_desk_zone common_zone",
        "goto_waypoint tiago common_zone corridor",
        "goto_waypoint tiago corridor social_room",
        "pass_through tiago door_3",
        "deviation tiago human_4",
    ],
    [
        "goto_waypoint tiago reading_zone common_zone",
        "deviation tiago human_8",
        "deviation tiago human_1",
        "goto_waypoint tiago common_zone corridor",
        "failure tiago passing door_3 doorway closed",
        "open tiago door_3",
        "pass_through tiago door_3",
        "fetch tiago book information_desk",
        "failure tiago fetching coffee coffee_table too_high",
        "ask_for_help tiago human_9",
        "goto_waypoint tiago social_room corridor",
        "goto_waypoint tiago corridor common_zone",
        "deviation tiago human_1",
        "goto_waypoint tiago common_zone reading_zone",
    ],
    [
        "goto_waypoint tiago information_desk_zone common_zone",
        "deviation tiago human_4",
        "deviation tiago human_5",
        "goto_waypoint tiago common_zone corridor",
        "failure tiago passing door_3 doorway closed",
        "open tiago door_3",
        "pass_through tiago door_3",
        "fetch tiago book information_desk",
        "failure tiago fetching coffee coffee_table too_far",
        "ask_for_help tiago human_9",
        "goto_waypoint tiago social_room corridor",
        "goto_waypoint tiago corridor common_zone",
        "goto_waypoint tiago common_zone information_desk_zone",
    ],
]

PLANS = [[action.split() for action in plan] for plan in _RAW_PLANS]

# ---------------------------------------------------------------------------
# Parameters of the Verbalization Space (Table I)
# ---------------------------------------------------------------------------

ABSTRACTION_LEVELS = [
    'coordinates',           # A1
    'angles/distances',      # A2
    'right/left',            # A3
    'semantic annotations',  # A4
]

LOCALITY_LEVELS = [
    'complete plan',     # L1
    'range of actions',  # L2
    'action or object',  # L3
]

SPECIFICITY_LEVELS = [
    'general picture',     # S1
    'summary',             # S2
    'detailed narrative',  # S3
]

EXPLANATION_LEVELS = [
    'no verb',         # E1
    'descriptive',     # E2
    'suggestive',      # E3
    'counterfactual',  # E4
    # Combinations of the three types.  They are not levels of Table I.
    'descriptive/suggestive',
    'suggestive/counterfactual',
    'counterfactual/descriptive',
    'descriptive/suggestive/counterfactual',
]

#: The four levels E1 to E4 of Table I, which Fig. 8 shows.
TABLE_EXPLANATION_LEVELS = EXPLANATION_LEVELS[:4]

# ---------------------------------------------------------------------------
# References to places and objects below the semantic level (A1 to A3).
# The experiment counts words, so one fixed reference stands for every place:
# a coordinate triple has the same number of words whatever its values are.
# The detailed narrative uses the long form, the summary the short form.
# ---------------------------------------------------------------------------

_REFERENCES = {
    'coordinates': ("zone with coordinates x = 0.0, y = 0.0, z = 0.0",
                    "x = 0.0, y = 0.0, z = 0.0"),
    'angles/distances': ("place x meters away", "place x"),
    'right/left': ("place on its left", "on its left"),
}


def _reference(abstraction, specificity):
    """Return the reference to a place or object for the levels A1 to A3."""
    long_form, short_form = _REFERENCES[abstraction]
    return long_form if specificity == 'detailed narrative' else short_form


# ---------------------------------------------------------------------------
# Verbalization of one plan action
# ---------------------------------------------------------------------------

def _verbalize_goto(robot, wp1, wp2, abstraction, specificity):
    if specificity == 'general picture':
        return f"{robot} is navigating"
    if abstraction == 'semantic annotations':
        return f"{robot} is navigating from {wp1} to {wp2}"
    ref = _reference(abstraction, specificity)
    return f"{robot} is navigating from {ref} to {ref}"


def _verbalize_pass_through(robot, obj, abstraction, specificity):
    if specificity == 'general picture':
        return f"{robot} is passing through"
    if abstraction != 'semantic annotations':
        obj = _reference(abstraction, specificity)
    # The space at the end is kept from the script of the experiment.  Its
    # word count splits at single spaces, so the space counts as one word.
    return f"{robot} is passing through {obj} "


def _verbalize_pass_between(robot, obj1, obj2, abstraction, specificity):
    if specificity == 'general picture':
        return f"{robot} is passing between"
    if abstraction == 'semantic annotations':
        return f"{robot} is passing between {obj1} and {obj2}"
    ref = _reference(abstraction, specificity)
    return f"{robot} is passing between {ref} and {ref}"


def _verbalize_open(robot, obj, abstraction, specificity):
    if specificity == 'general picture':
        return f"{robot} is opening"
    if abstraction != 'semantic annotations':
        obj = _reference(abstraction, specificity)
    # The space at the end is kept, see _verbalize_pass_through.
    return f"{robot} is opening {obj} "


def _verbalize_fetch(robot, obj, place, abstraction, specificity):
    if specificity == 'general picture':
        return f"{robot} is fetching"
    if abstraction == 'semantic annotations':
        return f"{robot} is fetching {obj} from {place}"
    ref = _reference(abstraction, specificity)
    return f"{robot} is fetching {ref} from {ref}"


def _verbalize_ask_for_help(robot, obj, abstraction, specificity):
    if specificity == 'general picture':
        return f"{robot} is asking for help"
    if abstraction == 'semantic annotations':
        return f"{robot} is asking for help {obj}"
    ref = _reference(abstraction, specificity)
    return f"{robot} is asking for help {ref}"


def _failure_phrases(robot, failed_action, obj, place, reason,
                     abstraction, specificity):
    """
    Return the four verbalizations of a failure action.

    The tuple holds the plain statement of level E1 and the descriptive,
    suggestive and counterfactual explanations of the levels E2 to E4.
    """
    start = f"{robot} has experienced a failure while {failed_action}"
    help_me = f"dear human, please help me {failed_action}"

    if abstraction == 'semantic annotations':
        if specificity == 'detailed narrative':
            plain = f"{start} {obj} at {place}"
            description = f"{start} {obj} at {place} which is {reason}"
            suggestion = f"{help_me} {obj} at {place}"
            counterfactual = (f"if {obj} at {place} was not {reason}, "
                              f"I would be able to {failed_action} {obj} from {place}")
        else:
            plain = start if specificity == 'general picture' else f"{start} {obj}"
            description = f"{start} {obj} which is {reason}"
            suggestion = f"{help_me} {obj} which is {reason}"
            counterfactual = (f"if {obj} was not {reason}, "
                              f"I would be able to {failed_action} {obj}")
        return plain, description, suggestion, counterfactual

    if specificity == 'general picture':
        plain = start
        description = f"{start} which is {reason}"
        suggestion = help_me
        counterfactual = (f"if object was not {reason}, "
                          f"I would be able to {failed_action}")
        return plain, description, suggestion, counterfactual

    ref = _reference(abstraction, specificity)
    if specificity == 'summary':
        plain = f"{start} {ref}"
        description = f"{start} {ref} which is {reason}"
        suggestion = f"{help_me} {ref}"
        counterfactual = (f"if object {ref} was not {reason}, "
                          f"I would be able to {failed_action} {ref}")
    else:  # detailed narrative
        plain = f"{start} object {ref}"
        if abstraction == 'coordinates':
            # Level A1 names the place of the object a second time.
            description = f"{start} object {ref} which is {ref} {reason}"
        else:
            description = f"{start} object {ref} which is {reason}"
        suggestion = f"{help_me} object {ref}"
        counterfactual = (f"if object {ref} was not {reason}, "
                          f"I would be able to {failed_action} object {ref}")
    return plain, description, suggestion, counterfactual


def _deviation_phrases(robot, obj, abstraction, specificity):
    """
    Return the four verbalizations of a deviation action, as _failure_phrases.

    The object that causes a deviation is movable, which the explanations of
    the levels E2 to E4 state.
    """
    start = f"{robot} has experienced a deviation while navigating"
    smoothly = "I would be able to continue navigating more smoothly"
    please = "can you please move, so I can continue navigating more smoothly"

    if specificity == 'general picture':
        return (start, start, f"dear object, {please}",
                f"if object was not there, {smoothly}")

    if abstraction != 'semantic annotations':
        obj = _reference(abstraction, specificity)
    plain = f"{start} because of {obj}"
    if specificity == 'summary':
        description = f"{start} because of movable {obj}"
        suggestion = f"dear movable {obj}, {please}"
        counterfactual = f"if movable {obj} was not there, {smoothly}"
    else:  # detailed narrative
        description = (f"{start} because of movable {obj} "
                       f"which is in front of it")
        suggestion = f"dear movable {obj} in front of me, {please}"
        counterfactual = f"if movable {obj} was not in front of me, {smoothly}"
    return plain, description, suggestion, counterfactual


def _select_explanation(plain, description, suggestion, counterfactual,
                        explanation):
    """Return the verbalization of a failure or deviation for the level E."""
    if explanation == 'no verb':
        return plain
    phrases = {'descriptive': description, 'suggestive': suggestion,
               'counterfactual': counterfactual}
    return '. '.join(phrases[part] for part in explanation.split('/'))


def verbalize_action(tokens, abstraction, specificity, explanation):
    """
    Verbalize one plan action.

    Parameters
    ----------
    tokens : list of str
        The action, for example ``['open', 'tiago', 'door_3']``.
    abstraction, specificity, explanation : str
        One of ``ABSTRACTION_LEVELS``, ``SPECIFICITY_LEVELS`` and
        ``EXPLANATION_LEVELS``.

    Returns
    -------
    str
        The verbalization, or ``''`` for an action name that is not known.
    """
    if len(tokens) < 2:
        return ''
    action, robot = tokens[0], tokens[1]
    args = tokens[2:] + ['?'] * 4  # missing arguments are verbalized as '?'

    if action == 'goto_waypoint':
        return _verbalize_goto(robot, args[0], args[1], abstraction, specificity)
    if action == 'pass_through':
        return _verbalize_pass_through(robot, args[0], abstraction, specificity)
    if action == 'pass_between':
        return _verbalize_pass_between(robot, args[0], args[1],
                                       abstraction, specificity)
    if action == 'open':
        return _verbalize_open(robot, args[0], abstraction, specificity)
    if action == 'fetch':
        return _verbalize_fetch(robot, args[0], args[1], abstraction, specificity)
    if action == 'ask_for_help':
        return _verbalize_ask_for_help(robot, args[0], abstraction, specificity)
    if action == 'failure':
        phrases = _failure_phrases(robot, args[0], args[1], args[2], args[3],
                                   abstraction, specificity)
        return _select_explanation(*phrases, explanation)
    if action == 'deviation':
        phrases = _deviation_phrases(robot, args[0], abstraction, specificity)
        return _select_explanation(*phrases, explanation)
    return ''


def verbalize_plan(plan, abstraction, locality, specificity, explanation,
                   locality_range=None, locality_action=None,
                   locality_object=None):
    """
    Verbalize a plan under the four parameters of the Verbalization Space.

    Parameters
    ----------
    plan : list of list of str
        The actions of the plan as token lists.
    abstraction, locality, specificity, explanation : str
        One level of each parameter.
    locality_range : tuple(int, int) or None
        For ``'range of actions'`` (L2): the slice of the plan to verbalize.
    locality_action : str or None
        For ``'action or object'`` (L3): the action name to verbalize.
    locality_object : str or None
        For ``'action or object'`` (L3): verbalize the actions that have this
        object as a parameter.

    Returns
    -------
    list of str
        One sentence per verbalized action.
    """
    if locality == 'range of actions':
        if locality_range is None:
            raise ValueError("locality 'range of actions' needs locality_range")
        actions = plan[locality_range[0]:locality_range[1]]
    elif locality == 'action or object':
        if locality_action is None and locality_object is None:
            raise ValueError("locality 'action or object' needs "
                             "locality_action or locality_object")
        actions = [
            tokens for tokens in plan
            if tokens[0] == locality_action or locality_object in tokens[2:]
        ]
    else:
        actions = plan

    sentences = [verbalize_action(tokens, abstraction, specificity, explanation)
                 for tokens in actions]
    return [sentence for sentence in sentences if sentence]


# ---------------------------------------------------------------------------
# Textual affordance-based explanations (Section IV-B)
# ---------------------------------------------------------------------------

#: The qualitative spatial relations of the modified single-cross calculus,
#: as the robot says them.
DIRECTION_PHRASES = {
    'front': 'in front of me',
    'back': 'behind me',
    'left': 'left of me',
    'right': 'right of me',
}

#: Name of a person in the ontology.  A person is asked to "move yourself".
HUMAN = 'human'


def _join(items):
    """Join words as "a", "a and b" or "a, b and c"."""
    if len(items) <= 2:
        return ' and '.join(items)
    return ', '.join(items[:-1]) + ' and ' + items[-1]


def _located(nouns, directions):
    """
    Attach the spatial relations to a list of noun phrases.

    Objects in the same direction share one relation: "the chair and the
    closed cabinet, both in front of me,".  Otherwise each object gets its
    own: "the chair in front of me and the human left of me".
    """
    known = [d for d in directions if d is not None]
    if len(nouns) >= 2 and len(known) == len(nouns) and len(set(known)) == 1:
        quantifier = 'both' if len(nouns) == 2 else 'all'
        return f"{_join(nouns)}, {quantifier} {DIRECTION_PHRASES[known[0]]},"
    return _join([
        f"{noun} {DIRECTION_PHRASES[direction]}" if direction else noun
        for noun, direction in zip(nouns, directions)
    ])


def _descriptive(state, causes, task):
    nouns = [
        f"the closed {name}" if affordance == 'openability' else f"the {name}"
        for name, affordance, _ in causes
    ]
    subject = _located(nouns, [direction for _, _, direction in causes])
    if state == 'failure':
        return f"I failed to {task} because {subject} blocked my path."
    return f"I deviated from my initial path because {subject} blocked it."


def _suggestive(state, causes, task):
    # A person is addressed directly and gets no spatial relation.
    to_person = ['move yourself' for name, _, _ in causes if name == HUMAN]
    objects = [cause for cause in causes if cause[0] != HUMAN]
    actions = [
        f"open the {name}" if affordance == 'openability' else f"move the {name}"
        for name, affordance, _ in objects
    ]
    directions = [direction for _, _, direction in objects]
    known = [d for d in directions if d is not None]
    if len(actions) >= 2 and len(known) == len(actions) and len(set(known)) == 1:
        quantifier = 'both' if len(actions) == 2 else 'all'
        request = (f"{_join(to_person + actions)}, "
                   f"{quantifier} {DIRECTION_PHRASES[known[0]]},")
    else:
        request = _join(to_person + [
            f"{action} {DIRECTION_PHRASES[direction]}" if direction else action
            for action, direction in zip(actions, directions)
        ])
    if state == 'failure':
        return f"Dear human, please {request} so I can {task}."
    return (f"Dear human, please {request} so I can decrease my deviation "
            f"and proceed to navigate more smoothly.")


def _counterfactual(state, causes, task):
    clauses = []
    for affordance, singular, plural in (
            ('movability', 'was not there', 'were not there'),
            ('openability', 'was open', 'were open')):
        group = [cause for cause in causes if cause[1] == affordance]
        if not group:
            continue
        nouns = [f"the {name}" for name, _, _ in group]
        directions = [direction for _, _, direction in group]
        known = [d for d in directions if d is not None]
        if len(group) == 1:
            clauses.append(f"{_located(nouns, directions)} {singular}")
        elif len(known) == len(group) and len(set(known)) == 1:
            clauses.append(f"{_join(nouns)}, {DIRECTION_PHRASES[known[0]]}, "
                           f"{plural}")
        else:
            clauses.append(f"{_located(nouns, directions)} {plural}")
    condition = ' and '.join(clauses)
    if state == 'failure':
        return f"If {condition}, I would not fail to {task}."
    return f"If {condition}, I would not deviate from my path."


def explanation_sentence(state, causes, explanation, task=None):
    """
    Return a textual affordance-based explanation.

    Parameters
    ----------
    state : str
        ``'failure'`` or ``'deviation'``.
    causes : list of (name, affordance, direction)
        The causes of the core explanation: the name of the object ("chair"),
        its affordance (``'movability'`` or ``'openability'``) and its spatial
        relation to the robot (``'front'``, ``'back'``, ``'left'``,
        ``'right'`` or None).
    explanation : str
        ``'descriptive'``, ``'suggestive'`` or ``'counterfactual'``.
    task : str or None
        What the robot failed to do, for example ``'fetch a book'``.

    Returns
    -------
    str
        The sentence, or ``''`` if there is no cause to explain.
    """
    if not causes:
        return ''
    task = task or 'reach my goal'
    generators = {'descriptive': _descriptive, 'suggestive': _suggestive,
                  'counterfactual': _counterfactual}
    return generators[explanation](state, causes, task)


def spatial_relations(core_explanation, ontology, qsr):
    """
    Return the causes of a core explanation as (name, affordance, direction).

    The direction is the qualitative spatial relation of the object to the
    robot, computed by the QSR calculus from the robot pose.
    """
    from qsr import relatum_angle

    robot_x, robot_y, robot_yaw = core_explanation.robot_pose
    causes = []
    for pair in core_explanation.causes:
        obj = ontology.objects[pair.obj_label]
        angle = relatum_angle(robot_x, robot_y, robot_yaw, obj['x'], obj['y'])
        direction = qsr.getBinaryQsrValue(angle) or None
        causes.append((obj['name'], pair.affordance, direction))
    return causes


def verbalize_explanation(core_explanation, ontology, qsr,
                          explanation='descriptive', task=None):
    """
    ``Verbalize(core_explanation, QSR)`` of Algorithm 1.

    Returns the textual explanation of the given type, or ``''`` for an empty
    core explanation.
    """
    causes = spatial_relations(core_explanation, ontology, qsr)
    return explanation_sentence(core_explanation.state.value, causes,
                                explanation, task)


# ---------------------------------------------------------------------------
# Verbalization space experiment (Section VI-B)
# ---------------------------------------------------------------------------

def count_words(sentence):
    """
    Count the words of a verbalized action as the experiment did.

    The sentence is split at single spaces.  A space at the end of a sentence
    therefore adds one to the count.
    """
    return len(sentence.split(' '))


def compute_word_count_stats(plans=PLANS):
    """
    Return the average number of words per plan for the combinations of A, S, E.

    The plans are verbalized as complete plans (locality L1).

    Returns
    -------
    dict
        Maps (abstraction, specificity, explanation) to the number of words
        of all verbalized plans divided by the number of plans.
    """
    stats = {}
    for abstraction in ABSTRACTION_LEVELS:
        for specificity in SPECIFICITY_LEVELS:
            for explanation in EXPLANATION_LEVELS:
                words = sum(
                    count_words(sentence)
                    for plan in plans
                    for sentence in verbalize_plan(
                        plan, abstraction, 'complete plan', specificity,
                        explanation)
                )
                stats[(abstraction, specificity, explanation)] = words / len(plans)
    return stats


def figure_tables(stats):
    """
    Reduce the statistics to the three tables of Fig. 8.

    Each table is the average over the levels of the third parameter.  Only
    the explanation levels E1 to E4 of Table I enter.

    Returns
    -------
    dict
        ``'abstraction/specificity'``, ``'abstraction/explanation'`` and
        ``'explanation/specificity'``, each a dict that maps a pair of levels
        to the average number of words.
    """
    def mean(values):
        values = list(values)
        return sum(values) / len(values)

    levels_e = TABLE_EXPLANATION_LEVELS
    return {
        'abstraction/specificity': {
            (a, s): mean(stats[(a, s, e)] for e in levels_e)
            for a in ABSTRACTION_LEVELS for s in SPECIFICITY_LEVELS
        },
        'abstraction/explanation': {
            (a, e): mean(stats[(a, s, e)] for s in SPECIFICITY_LEVELS)
            for a in ABSTRACTION_LEVELS for e in levels_e
        },
        'explanation/specificity': {
            (e, s): mean(stats[(a, s, e)] for a in ABSTRACTION_LEVELS)
            for e in levels_e for s in SPECIFICITY_LEVELS
        },
    }


def main():
    stats = compute_word_count_stats()

    print("Average number of words per plan")
    print(f"{'abstraction':<22}{'specificity':<20}{'explanation':<40}{'words':>7}")
    for (a, s, e), words in stats.items():
        print(f"{a:<22}{s:<20}{e:<40}{words:>7.1f}")

    for name, table in figure_tables(stats).items():
        print(f"\nFig. 8, {name} (average number of words)")
        for (first, second), words in table.items():
            print(f"  {first:<22}{second:<20}{words:>7.1f}")


if __name__ == '__main__':
    main()
