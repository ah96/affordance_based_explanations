#!/usr/bin/env python3

plans = [["goto_waypoint tiago social_room corridor","failure tiago passing door_3 doorway closed","open tiago door_3","pass_through tiago door_3","goto_waypoint tiago corridor common_zone","goto_waypoint tiago common_zone book_zone","goto_waypoint tiago book_zone bookshelf_2","deviation tiago human_1","fetch tiago book bookshelf_2","failure tiago fetching book bookshelf_2 too_high","ask_for_help tiago human_5","goto_waypoint tiago bookshelf_2 common_zone","goto_waypoint tiago common_zone corridor","goto_waypoint tiago corridor social_room"],
["goto_waypoint tiago reading_zone common_zone","deviation tiago human_13","goto_waypoint tiago common_zone book_zone","goto_waypoint tiago book_zone bookshelf_14","pass_between tiago bookshelf_8 bookshelf_12","pass_between tiago bookshelf_9 bookshelf_13","fetch tiago book bookshelf_14","goto_waypoint tiago book_zone bookshelf_14","pass_between tiago bookshelf_9 bookshelf_13","pass_between tiago bookshelf_8 bookshelf_12","goto_waypoint tiago book_zone common_zone","deviation tiago human_15","goto_waypoint tiago common_zone book_zone"],
["goto_waypoint tiago computer_room corridor","pass_through tiago door_2","goto_waypoint tiago corridor common_zone","goto_waypoint tiago common_zone book_zone","goto_waypoint tiago book_zone bookshelf_5","deviation tiago human_2","fetch tiago book bookshelf_5","failure tiago fetching book bookshelf_5 too_high","ask_for_help tiago human_7","goto_waypoint tiago bookshelf_2 common_zone","goto_waypoint tiago common_zone corridor","goto_waypoint tiago corridor computer_room","failure tiago passing door_2 doorway closed","open tiago door_2"],
["goto_waypoint tiago reading_zone common_zone","deviation tiago human_19","goto_waypoint tiago common_zone book_zone","goto_waypoint tiago book_zone bookshelf_8","pass_between tiago bookshelf_6 bookshelf_11","pass_between tiago bookshelf_5 bookshelf_7","fetch tiago book bookshelf_8","goto_waypoint tiago book_zone bookshelf_8","pass_between tiago bookshelf_5 bookshelf_7","pass_between tiago bookshelf_6 bookshelf_11","goto_waypoint tiago book_zone common_zone","deviation tiago human_4","goto_waypoint tiago common_zone book_zone"],
["goto_waypoint tiago social_room corridor","pass_through tiago door_3","goto_waypoint tiago corridor common_zone","goto_waypoint tiago common_zone book_zone","goto_waypoint tiago book_zone bookshelf_5","deviation tiago human_5","fetch tiago book bookshelf_5","failure tiago fetching book bookshelf_5 too_high","ask_for_help tiago human_6","goto_waypoint tiago bookshelf_5 common_zone","goto_waypoint tiago common_zone corridor","goto_waypoint tiago corridor social_room","failure tiago passing door_3 doorway closed","open tiago door_3"],
["goto_waypoint tiago computer_room corridor","failure tiago passing door_2 doorway closed","open tiago door_2","pass_through tiago door_2","goto_waypoint tiago corridor common_zone","goto_waypoint tiago common_zone book_zone","goto_waypoint tiago book_zone bookshelf_9","deviation tiago human_9","fetch tiago book bookshelf_9","failure tiago fetching book bookshelf_9 too_low","ask_for_help tiago human_9","goto_waypoint tiago bookshelf_9 common_zone","goto_waypoint tiago common_zone corridor","goto_waypoint tiago corridor computer_room"],
["goto_waypoint tiago information_desk_zone corridor","deviation tiago human_9","deviation tiago human_8","goto_waypoint tiago common_zone book_zone","goto_waypoint tiago book_zone bookshelf_9","pass_between tiago bookshelf_6 bookshelf_11","pass_between tiago bookshelf_7 bookshelf_10","fetch tiago book bookshelf_9","failure tiago fetching book bookshelf_9 too_high","ask_for_help tiago human_3","goto_waypoint tiago bookshelf_9 book_zone","goto_waypoint tiago book_zone common_zone","goto_waypoint tiago common_zone reading_zone","failure tiago returning book information_desk_zone wrong_zone","goto_waypoint tiago reading_zone common_zone","goto_waypoint tiago common_zone information_desk_zone"],
["goto_waypoint tiago social_room corridor","pass_through tiago door_3","goto_waypoint tiago corridor common_zone","failure tiago goto_waypoint common_zone common_zone chair_2","ask_for_help tiago human_9","goto_waypoint tiago common_zone information_desk_zone","deviation tiago human_8","fetch tiago book information_desk","goto_waypoint tiago information_desk_zone common_zone","goto_waypoint tiago common_zone corridor","goto_waypoint tiago corridor social_room","pass_through tiago door_3","deviation tiago human_4"],
["goto_waypoint tiago reading_zone common_zone","deviation tiago human_8","deviation tiago human_1","goto_waypoint tiago common_zone corridor","failure tiago passing door_3 doorway closed","open tiago door_3","pass_through tiago door_3","fetch tiago book information_desk","failure tiago fetching coffee coffee_table too_high","ask_for_help tiago human_9","goto_waypoint tiago social_room corridor","goto_waypoint tiago corridor common_zone","deviation tiago human_1","goto_waypoint tiago common_zone reading_zone"],
["goto_waypoint tiago information_desk_zone common_zone","deviation tiago human_4","deviation tiago human_5","goto_waypoint tiago common_zone corridor","failure tiago passing door_3 doorway closed","open tiago door_3","pass_through tiago door_3","fetch tiago book information_desk","failure tiago fetching coffee coffee_table too_far","ask_for_help tiago human_9","goto_waypoint tiago social_room corridor","goto_waypoint tiago corridor common_zone","goto_waypoint tiago common_zone information_desk_zone"]]


def split_strings(list_of_lists):
    """
    Split every string in each sublist into words.

    Args:
    list_of_lists (list of list of str): A list containing 10 sublists, where each sublist contains strings.

    Returns:
    list of list of list of str: A list containing 10 sublists, where each sublist contains lists of words.
    """
    # Initialize an empty list to hold the result
    split_words = []

    # Iterate over each sublist in the list of lists
    for sublist in list_of_lists:
        # Initialize an empty list to hold the split words for the current sublist
        sublist_split_words = []
        #print("sublist = ", sublist)
        # Iterate over each string in the current sublist
        for string in sublist:
            # Split the string into words and add to the sublist_split_words
            words = string.split(' ')
            sublist_split_words.append(words)

        # Add the split words for the current sublist to the main list
        split_words.append(sublist_split_words)

    return split_words

# Call the function with the example list
plans = split_strings(plans)

# Print the result
#for plan in plans:
#    print(plan)

# possible actions: goto_waypoint, pass_through, pass_between, open, fetch, ask_for_help, failure, deviation 

abstraction_levels = ["coordinates","angles/distances","right/left","semantic annotations"]
specificity_levels = ["general picture","summary","detailed narrative"]
explanation_levels = ["no verb","descriptive","suggestive","counterfactual","descriptive/suggestive","suggestive/counterfactual","counterfactual/descriptive","descriptive/suggestive/counterfactual"]

abstraction_level = abstraction_levels[2]
specificity_level = specificity_levels[2]
explanation_level = explanation_levels[3]

space_dummy = " "
navigating_dummy = "navigating"
is_dummy = "is"
navigating_from_dummy = "navigating from"
to_dummy = "to"
and_dummy = "and"
from_dummy = "from"

coord_dummy = "zone with coordinates x = 0.0, y = 0.0, z = 0.0"
coord_dummy_2 = "x = 0.0, y = 0.0, z = 0.0"

distance_dummy = "place x meters away"
distance_dummy_2 = "place x"

direction_dummy = "place on its left"
direction_dummy_2 = "on its left"

pass_through_dummy = "passing through"
pass_between_dummy = "passing between"
open_dummy = "opening"
fetch_dummy = "fetching"
ask_for_help_dummy = 'asking for help'

for plan in plans:
    plan_verb = []
    for action_string in plan:
        action = action_string[0]
        #print('action = ', action)
        robot = action_string[1]
        #print('robot = ', robot)

        action_string_verb = ""

        if action == "goto_waypoint":
            wp1 = action_string[2]
            wp2 = action_string[3]

            if abstraction_level == "coordinates":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + navigating_from_dummy + space_dummy + coord_dummy + space_dummy + to_dummy + space_dummy + coord_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + navigating_from_dummy + space_dummy + coord_dummy_2 + space_dummy + to_dummy + space_dummy + coord_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + navigating_dummy

            elif abstraction_level == "angles/distances":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + navigating_from_dummy + space_dummy + distance_dummy + space_dummy + to_dummy + space_dummy + distance_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + navigating_from_dummy + space_dummy + distance_dummy_2 + space_dummy + to_dummy + space_dummy + distance_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + navigating_dummy

            elif abstraction_level == "right/left":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + navigating_from_dummy + space_dummy + direction_dummy + space_dummy + to_dummy + space_dummy + direction_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + navigating_from_dummy + space_dummy + direction_dummy_2 + space_dummy + to_dummy + space_dummy + direction_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + navigating_dummy
        
            elif abstraction_level == "semantic annotations":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + navigating_from_dummy + space_dummy + wp1 + space_dummy + to_dummy + space_dummy + wp2
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + navigating_from_dummy + space_dummy + wp1 + space_dummy + to_dummy + space_dummy + wp2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + navigating_dummy

        elif action == "pass_through":
            object = action_string[2]

            if abstraction_level == "coordinates":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_through_dummy + space_dummy + coord_dummy + space_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_through_dummy + space_dummy + coord_dummy_2 + space_dummy
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_through_dummy

            elif abstraction_level == "angles/distances":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_through_dummy + space_dummy + distance_dummy + space_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_through_dummy + space_dummy + distance_dummy_2 + space_dummy
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_through_dummy

            elif abstraction_level == "right/left":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_through_dummy + space_dummy + direction_dummy + space_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_through_dummy + space_dummy + direction_dummy_2 + space_dummy
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_through_dummy
        
            elif abstraction_level == "semantic annotations":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_through_dummy + space_dummy + object + space_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_through_dummy + space_dummy + object + space_dummy
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_through_dummy

        elif action == "pass_between":
            wp1 = action_string[2]
            wp2 = action_string[3]

            if abstraction_level == "coordinates":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_between_dummy + space_dummy + coord_dummy + space_dummy + and_dummy + space_dummy + coord_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_between_dummy + space_dummy + coord_dummy_2 + space_dummy + and_dummy + space_dummy + coord_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_between_dummy

            elif abstraction_level == "angles/distances":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_between_dummy + space_dummy + distance_dummy + space_dummy + and_dummy + space_dummy + distance_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_between_dummy + space_dummy + distance_dummy_2 + space_dummy + and_dummy + space_dummy + distance_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_between_dummy

            elif abstraction_level == "right/left":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_between_dummy + space_dummy + direction_dummy + space_dummy + and_dummy + space_dummy + direction_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_between_dummy+ space_dummy + direction_dummy_2 + space_dummy + and_dummy + space_dummy + direction_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_between_dummy
        
            elif abstraction_level == "semantic annotations":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_between_dummy + space_dummy + wp1 + space_dummy + and_dummy + space_dummy + wp2
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_between_dummy + space_dummy + wp1 + space_dummy + and_dummy + space_dummy + wp2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + pass_between_dummy

        elif action == "open":
            object = action_string[2]

            if abstraction_level == "coordinates":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + open_dummy + space_dummy + coord_dummy + space_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + open_dummy + space_dummy + coord_dummy_2 + space_dummy
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + open_dummy

            elif abstraction_level == "angles/distances":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + open_dummy + space_dummy + distance_dummy + space_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + open_dummy + space_dummy + distance_dummy_2 + space_dummy
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + open_dummy

            elif abstraction_level == "right/left":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + open_dummy + space_dummy + direction_dummy + space_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + open_dummy + space_dummy + direction_dummy_2 + space_dummy
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + open_dummy
        
            elif abstraction_level == "semantic annotations":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + open_dummy + space_dummy + object + space_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + open_dummy + space_dummy + object + space_dummy
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + open_dummy        

        elif action == "fetch":
            object = action_string[2]
            place = action_string[3]

            if abstraction_level == "coordinates":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + fetch_dummy + space_dummy + coord_dummy + space_dummy + from_dummy + space_dummy + coord_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + fetch_dummy + space_dummy + coord_dummy_2 + space_dummy + from_dummy + space_dummy + coord_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + fetch_dummy

            elif abstraction_level == "angles/distances":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + fetch_dummy + space_dummy + distance_dummy + space_dummy + from_dummy + space_dummy + distance_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + fetch_dummy + space_dummy + distance_dummy_2 + space_dummy + from_dummy + space_dummy + distance_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + fetch_dummy

            elif abstraction_level == "right/left":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + fetch_dummy + space_dummy + direction_dummy + space_dummy + from_dummy + space_dummy + direction_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + fetch_dummy + space_dummy + direction_dummy_2 + space_dummy + from_dummy + space_dummy + direction_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + fetch_dummy
        
            elif abstraction_level == "semantic annotations":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + fetch_dummy + space_dummy + object + space_dummy + from_dummy + space_dummy + place
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + fetch_dummy + space_dummy + object + space_dummy + from_dummy + space_dummy + place
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + fetch_dummy

        elif action == "ask_for_help":
            object = action_string[2]

            if abstraction_level == "coordinates":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy + space_dummy + coord_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy + space_dummy + coord_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy

            elif abstraction_level == "angles/distances":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy + space_dummy + distance_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy + space_dummy + distance_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy

            elif abstraction_level == "right/left":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy + space_dummy + direction_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy + space_dummy + direction_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy
        
            elif abstraction_level == "semantic annotations":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy + space_dummy + object
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy + space_dummy + object
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy

        elif action == "failure":
            reason_action = action_string[2]
            object_1 = action_string[3]
            object_2 = action_string[4]
            reason = action_string[5]

            if abstraction_level == "coordinates":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + "has failed" + space_dummy + "while" + space_dummy + reason_action + space_dummy + object_1 + space_dummy + "at" + space_dummy + object_2 + space_dummy + "which is" + space_dummy + reason
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy + space_dummy + coord_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy

            elif abstraction_level == "angles/distances":
                if specificity_level == "detailed narrative":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy + space_dummy + distance_dummy
                elif specificity_level == "summary":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy + space_dummy + distance_dummy_2
                elif specificity_level == "general picture":
                    action_string_verb = robot + space_dummy + is_dummy + space_dummy + ask_for_help_dummy

            elif abstraction_level == "right/left":
                if specificity_level == "detailed narrative":
                    description = robot + space_dummy + "has experienced a failure" + space_dummy + "while" + space_dummy + reason_action + space_dummy + "object" + space_dummy + direction_dummy + space_dummy + "which is" + space_dummy + reason
                    suggestion = "dear human, please help me" + space_dummy + reason_action + space_dummy + "object" + space_dummy + direction_dummy
                    counterfactual = "if" + space_dummy + "object" + space_dummy + direction_dummy + space_dummy + "was not" + space_dummy + reason + ',' + space_dummy + "I would be able to" + space_dummy + reason_action + space_dummy + "object" + space_dummy + direction_dummy
                    if explanation_level == "no verb":
                        action_string_verb = robot + space_dummy + "has experienced a failure" + space_dummy + "while" + space_dummy + reason_action + space_dummy + "object" + space_dummy + direction_dummy
                    elif explanation_level == "descriptive":
                        action_string_verb = description
                    elif explanation_level == "suggestive":
                        action_string_verb = suggestion
                    elif explanation_level == "counterfactual":
                        action_string_verb = counterfactual
                    elif explanation_level == "descriptive/suggestive":
                        action_string_verb = description + '. ' + suggestion
                    elif explanation_level == "suggestive/counterfactual":
                        action_string_verb = suggestion + '. ' + counterfactual
                    elif explanation_level == "counterfactual/descriptive":
                        action_string_verb = counterfactual + '. ' + description
                    elif explanation_level == "descriptive/suggestive/counterfactual":
                        action_string_verb = description + '. ' + suggestion + '. ' + counterfactual                    
                elif specificity_level == "summary":
                    pass
                elif specificity_level == "general picture":
                    pass
        
            elif abstraction_level == "semantic annotations":
                if specificity_level == "detailed narrative":
                    description = robot + space_dummy + "has experienced a failure" + space_dummy + "while" + space_dummy + reason_action + space_dummy + object_1 + space_dummy + "at" + space_dummy + object_2 + space_dummy + "which is" + space_dummy + reason
                    suggestion = "dear human, please help me" + space_dummy + reason_action + space_dummy + object_1 + space_dummy + "at" + space_dummy + object_2
                    counterfactual = "if" + space_dummy + object_1 + space_dummy + "at" + space_dummy + object_2 + space_dummy + "was not" + space_dummy + reason + ',' + space_dummy + "I would be able to" + space_dummy + reason_action + space_dummy + object_1 + space_dummy + from_dummy + space_dummy + object_2
                    if explanation_level == "no verb":
                        action_string_verb = robot + space_dummy + "has experienced a failure" + space_dummy + "while" + space_dummy + reason_action + space_dummy + object_1 + space_dummy + "at" + space_dummy + object_2
                    elif explanation_level == "descriptive":
                        action_string_verb = description
                    elif explanation_level == "suggestive":
                        action_string_verb = suggestion
                    elif explanation_level == "counterfactual":
                        action_string_verb = counterfactual
                    elif explanation_level == "descriptive/suggestive":
                        action_string_verb = description + '. ' + suggestion
                    elif explanation_level == "suggestive/counterfactual":
                        action_string_verb = suggestion + '. ' + counterfactual
                    elif explanation_level == "counterfactual/descriptive":
                        action_string_verb = counterfactual + '. ' + description
                    elif explanation_level == "descriptive/suggestive/counterfactual":
                        action_string_verb = description + '. ' + suggestion + '. ' + counterfactual
                
                elif specificity_level == "summary":
                    description = robot + space_dummy + "has experienced a failure" + space_dummy + "while" + space_dummy + reason_action + space_dummy + object_1 + space_dummy + "which is" + space_dummy + reason
                    suggestion = "dear human, please help me" + space_dummy + reason_action + space_dummy + object_1 + space_dummy + "which is" + space_dummy + reason
                    counterfactual = "if" + space_dummy + object_1 + space_dummy + "was not" + space_dummy + reason + ',' + space_dummy + "I would be able to" + space_dummy + reason_action + space_dummy + object_1
                    if explanation_level == "no verb":
                        action_string_verb = robot + space_dummy + "has experienced a failure" + space_dummy + "while" + space_dummy + reason_action + space_dummy + object_1
                    elif explanation_level == "descriptive":
                        action_string_verb = description
                    elif explanation_level == "suggestive":
                        action_string_verb = suggestion
                    elif explanation_level == "counterfactual":
                        action_string_verb = counterfactual
                    elif explanation_level == "descriptive/suggestive":
                        action_string_verb = description + '. ' + suggestion
                    elif explanation_level == "suggestive/counterfactual":
                        action_string_verb = suggestion + '. ' + counterfactual
                    elif explanation_level == "counterfactual/descriptive":
                        action_string_verb = counterfactual + '. ' + description
                    elif explanation_level == "descriptive/suggestive/counterfactual":
                        action_string_verb = description + '. ' + suggestion + '. ' + counterfactual
                
                elif specificity_level == "general picture":
                    description = robot + space_dummy + "has experienced a failure" + space_dummy + "while" + space_dummy + reason_action + space_dummy + object_1 + space_dummy + "which is" + space_dummy + reason
                    suggestion = "dear human, please help me" + space_dummy + reason_action + space_dummy + object_1 + space_dummy + "which is" + space_dummy + reason
                    counterfactual = "if" + space_dummy + object_1 + space_dummy + "was not" + space_dummy + reason + ',' + space_dummy + "I would be able to" + space_dummy + reason_action + space_dummy + object_1
                    if explanation_level == "no verb":
                        action_string_verb = robot + space_dummy + "has experienced a failure" + space_dummy + "while" + space_dummy + reason_action
                    elif explanation_level == "descriptive":
                        action_string_verb = description
                    elif explanation_level == "suggestive":
                        action_string_verb = suggestion
                    elif explanation_level == "counterfactual":
                        action_string_verb = counterfactual
                    elif explanation_level == "descriptive/suggestive":
                        action_string_verb = description + '. ' + suggestion
                    elif explanation_level == "suggestive/counterfactual":
                        action_string_verb = suggestion + '. ' + counterfactual
                    elif explanation_level == "counterfactual/descriptive":
                        action_string_verb = counterfactual + '. ' + description
                    elif explanation_level == "descriptive/suggestive/counterfactual":
                        action_string_verb = description + '. ' + suggestion + '. ' + counterfactual

        print(action_string_verb)