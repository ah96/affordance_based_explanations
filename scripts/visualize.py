#!/usr/bin/env python3
"""
Visual affordance-based explanations.

Implements the visual explanation of Section IV-A of "Affordance-Based
Explanations of Robot Navigation" (Halilovic and Krivic, ICRA 2025): a
bird's-eye view of the surroundings of the robot.  The objects that caused
the planning failure or the deviation are red.  The other objects are light
gray.  This is ``Visualize(core_explanation, map)`` of Algorithm 1.

The view does not depend on the path planner.  It needs the core explanation
and the ontology only.

Usage
-----
    python3 visualize.py        # writes visual_explanation.png

    visualizer = VisualExplanationGenerator(ontology)
    visualizer.generate(core_explanation, output_path='explanation.png')
"""

import math
import os

import matplotlib
matplotlib.use('Agg')  # draws to a file, so that no display is needed
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

#: Colors of the explanation, as (red, green, blue) from 0 to 1.
COLOR_CAUSE = (1.0, 0.0, 0.0)        # red: the object is a cause
COLOR_NEUTRAL = (0.85, 0.85, 0.85)   # light gray: the object has no influence
COLOR_ROBOT = (1.0, 1.0, 1.0)
COLOR_BACKGROUND = (0.4, 0.4, 0.4)


class VisualExplanationGenerator:
    """
    Draws the bird's-eye view of a core explanation.

    Parameters
    ----------
    ontology : AffordanceOntology
        Gives the position, the size and the identifier of each object.
    view_radius : float
        Half of the side of the square view around the robot, in metres.
        This is the size of the environment shown in the explanation.
    robot_radius : float
        Radius of the robot symbol in metres.
    dpi : int
        Resolution of the image.
    """

    def __init__(self, ontology, view_radius=3.0, robot_radius=0.3, dpi=100):
        self.ontology = ontology
        self.view_radius = view_radius
        self.robot_radius = robot_radius
        self.dpi = dpi

    def colors(self, core_explanation):
        """
        Return the color of every object in the view.

        Returns
        -------
        dict
            Maps the object identifier to ``COLOR_CAUSE`` or ``COLOR_NEUTRAL``.
        """
        robot_x, robot_y, _ = core_explanation.robot_pose
        causes = {pair.obj_label for pair in core_explanation.causes}
        result = {}
        for label, obj in self.ontology.objects.items():
            if (abs(obj['x'] - robot_x) - obj['w'] / 2.0 > self.view_radius
                    or abs(obj['y'] - robot_y) - obj['h'] / 2.0 > self.view_radius):
                continue
            result[label] = COLOR_CAUSE if label in causes else COLOR_NEUTRAL
        return result

    def generate(self, core_explanation, output_path=None, show_paths=True):
        """
        Draw the visual explanation.

        Parameters
        ----------
        core_explanation : CoreExplanation
        output_path : str or None
            If given, the image is saved there.
        show_paths : bool
            Draw the original path of the robot (dashed) and, for a deviation,
            its current path (solid).

        Returns
        -------
        matplotlib.figure.Figure
        """
        robot_x, robot_y, robot_yaw = core_explanation.robot_pose
        fig, ax = plt.subplots(figsize=(6, 6), dpi=self.dpi)
        ax.set_aspect('equal')
        ax.set_facecolor(COLOR_BACKGROUND)
        ax.set_xlim(robot_x - self.view_radius, robot_x + self.view_radius)
        ax.set_ylim(robot_y - self.view_radius, robot_y + self.view_radius)

        for label, color in self.colors(core_explanation).items():
            obj = self.ontology.objects[label]
            ax.add_patch(mpatches.Rectangle(
                (obj['x'] - obj['w'] / 2.0, obj['y'] - obj['h'] / 2.0),
                obj['w'], obj['h'],
                facecolor=color, edgecolor='black', linewidth=0.8, zorder=2))
            ax.text(obj['x'], obj['y'], label, fontsize=7, fontweight='bold',
                    ha='center', va='center', clip_on=True, zorder=3)

        if show_paths:
            for path, style in ((core_explanation.original_path, '--'),
                                (core_explanation.current_path, '-')):
                if path:
                    ax.plot([p[0] for p in path], [p[1] for p in path],
                            style, color='white', linewidth=1.2, zorder=4)

        ax.add_patch(mpatches.Circle(
            (robot_x, robot_y), self.robot_radius,
            facecolor=COLOR_ROBOT, edgecolor='black', linewidth=0.8, zorder=5))
        ax.annotate(
            '', zorder=6,
            xy=(robot_x + 2.5 * self.robot_radius * math.cos(robot_yaw),
                robot_y + 2.5 * self.robot_radius * math.sin(robot_yaw)),
            xytext=(robot_x + self.robot_radius * math.cos(robot_yaw),
                    robot_y + self.robot_radius * math.sin(robot_yaw)),
            arrowprops=dict(arrowstyle='->', color='white', lw=2))

        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        ax.legend(
            handles=[
                mpatches.Patch(facecolor=COLOR_CAUSE, edgecolor='black',
                               label='cause of the failure or deviation'),
                mpatches.Patch(facecolor=COLOR_NEUTRAL, edgecolor='black',
                               label='object without influence'),
                mpatches.Patch(facecolor=COLOR_ROBOT, edgecolor='black',
                               label='robot'),
            ],
            loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3,
            fontsize=7, frameon=False)
        fig.tight_layout()

        if output_path:
            fig.savefig(output_path, dpi=self.dpi)
        return fig


def main():
    from aff import CoreExplanationGenerator, LIBRARY_SCENARIOS, load_library

    ontology, grid = load_library()
    generator = CoreExplanationGenerator(ontology, grid)
    scenario = LIBRARY_SCENARIOS['deviation']
    core = generator.generate(scenario['robot_pose'], scenario['goal'],
                              scenario['state'])
    output_path = os.path.join(os.getcwd(), 'visual_explanation.png')
    VisualExplanationGenerator(ontology).generate(core, output_path)
    print(f"Causes: {core.causes}")
    print(f"Saved {output_path}")
    plt.close('all')


if __name__ == '__main__':
    main()
