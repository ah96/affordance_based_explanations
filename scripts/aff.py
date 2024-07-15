import numpy as np
import matplotlib.pyplot as plt

class AffordanceSpace:
    def __init__(self, dimensions):
        self.dimensions = dimensions

    def compute_affordance(self, obj, capabilities):
        affordance_vector = []
        for dimension in self.dimensions:
            affordance_vector.append(dimension.compute(obj, capabilities))
        return np.array(affordance_vector)

class Dimension:
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def compute(self, obj, capabilities):
        return self.func(obj, capabilities)

class Object:
    def __init__(self, properties):
        self.properties = properties

    def get_property(self, name):
        return self.properties.get(name, None)

class Agent:
    def __init__(self, capabilities, activity_space):
        self.capabilities = capabilities
        self.activity_space = activity_space

    def perceive(self, environment):
        perceived_objects = []
        for obj in environment.objects:
            affordance_vector = self.compute_affordance(obj)
            perceived_objects.append((obj, affordance_vector))
        return perceived_objects

    def compute_affordance(self, obj):
        return environment.affordance_space.compute_affordance(obj, self.capabilities)

    def select_action(self, affordance_vector):
        if self.activity_space.is_action_feasible("pick up", affordance_vector):
            return "pick up"
        return "no feasible action"

    def explain_action(self, action, affordance_vector, obj):
        explanation = ExplanationGenerator.generate_explanation(action, affordance_vector, obj, self.activity_space)
        return explanation

class Environment:
    def __init__(self, objects, affordance_space, activity_space):
        self.objects = objects
        self.affordance_space = affordance_space
        self.activity_space = activity_space

class ExplanationGenerator:
    @staticmethod
    def generate_explanation(action, affordance_vector, obj, activity_space):
        explanation = f"The action '{action}' was selected because:\n"
        for i, value in enumerate(affordance_vector):
            dimension_name = obj.environment.affordance_space.dimensions[i].name
            explanation += f"- The {dimension_name} of the object is {value}.\n"
        if activity_space:
            explanation += activity_space.explain_feasibility(action, affordance_vector)
        return explanation

class ActivitySpace:
    def __init__(self, constraints):
        self.constraints = constraints

    def is_action_feasible(self, action, affordance_vector):
        return all(self.constraints.get(action, lambda x: True)(affordance_vector))

    def explain_feasibility(self, action, affordance_vector):
        if self.is_action_feasible(action, affordance_vector):
            return f"The action '{action}' is feasible within the activity space constraints.\n"
        else:
            return f"The action '{action}' is not feasible within the activity space constraints.\n"

# Example Usage and Use Cases
if __name__ == "__main__":
    # Define dimensions of affordance space
    size_dimension = Dimension("size", lambda obj, cap: obj.get_property("size") / cap.get("grip_size", 1))
    weight_dimension = Dimension("weight", lambda obj, cap: obj.get_property("weight") / cap.get("strength", 1))
    stability_dimension = Dimension("stability", lambda obj, cap: obj.get_property("stability"))
    
    # Create affordance space
    affordance_space = AffordanceSpace([size_dimension, weight_dimension, stability_dimension])
    
    # Define activity space constraints
    activity_constraints = {
        "pick up": lambda affordance_vector: affordance_vector[0] < 2 and affordance_vector[1] < 1
    }
    
    # Create activity space
    activity_space = ActivitySpace(activity_constraints)

    # Define objects in the environment
    cup = Object({"size": 5, "weight": 1, "stability": 0.8})
    cup.environment = Environment([cup], affordance_space, activity_space)  # Add environment reference for explanation
    plate = Object({"size": 8, "weight": 2, "stability": 0.9})
    plate.environment = Environment([plate], affordance_space, activity_space)  # Add environment reference for explanation
    
    # Define environment
    environment = Environment([cup, plate], affordance_space, activity_space)

    # Define agent capabilities
    robot_capabilities = {"grip_size": 6, "strength": 10}

    # Create agent
    robot = Agent(robot_capabilities, activity_space)

    # Agent perceives the environment
    perceived_objects = robot.perceive(environment)

    # Generate explanations for each object
    for obj, affordance_vector in perceived_objects:
        action = robot.select_action(affordance_vector)
        explanation = robot.explain_action(action, affordance_vector, obj)
        print(f"Object: {obj.properties}")
        print(f"Affordance Vector: {affordance_vector}")
        print(f"Selected Action: {action}")
        print(f"Explanation: {explanation}")
        print()

    # Plotting affordance space
    def plot_affordance_space(objects, affordance_space):
        fig, ax = plt.subplots()
        for obj in objects:
            affordance_vector = affordance_space.compute_affordance(obj, robot_capabilities)
            ax.plot(affordance_vector[0], affordance_vector[1], 'o', label=f'Object: {obj.properties}')
            for i, txt in enumerate(affordance_vector):
                ax.annotate(f'{obj.get_property("size")}, {obj.get_property("weight")}', (affordance_vector[0], affordance_vector[1]))
        ax.set_xlabel('Size/Grip Size')
        ax.set_ylabel('Weight/Strength')
        ax.set_title('Affordance Space')
        plt.legend()
        plt.show()

    plot_affordance_space([cup, plate], affordance_space)
    