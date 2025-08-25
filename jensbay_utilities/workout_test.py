import pandas as pd

df = pd.read_clipboard()

df.rename(columns = {'Navn': 'exercise', 'Område': 'area', 'Sværhedsgrad':'diffucility'}, inplace = True)

df.sort_values(by=['area'], inplace=True)

import numpy as np
import random

def get_exercises(working_dataframe = df, area = 'Legs', diffuculty = 4, exercise_amount = 11):
    # now we need to check that area is in the dataframe columns
    if 'area' not in working_dataframe.columns:
        raise ValueError("The dataframe does not contain an 'area' column.")
    if 'exercise' not in working_dataframe.columns:
        raise ValueError("The dataframe does not contain an 'exercise' column.")
    if 'diffucility' not in working_dataframe.columns:
        raise ValueError("The dataframe does not contain a 'diffucility' column.")
    # Now lets ensure that we check that the area exists in the dataframe
    if area not in working_dataframe.area.unique():
        raise ValueError(f"Area '{area}' does not exist in the dataframe.", working_dataframe.area.unique())
    
    # local_df = working_dataframe[working_dataframe.area == area]

    for i in range(1000):
        exercises = get_exercise_list(exercise_amount, working_dataframe)

        unique = set(exercises)

        if len(unique) < exercise_amount:
            continue
        else:
            mean = working_dataframe[working_dataframe.exercise.isin(exercises)].diffucility.mean()
        
        if diffuculty - 0.5 < mean < diffuculty + 0.5:
            return exercises
    print(f"Could not find exercises for area {area} with difficulty {diffuculty} after 1000 tries.")    

    # now we ne need to make an empty list of the length exercise_amount
    output = ["" for i in range(exercise_amount)]
    return output

DEBUG = True  # Assuming DEBUG is defined somewhere; added for context

def get_allocations(working_dataframe, exercise_amount, more_abs=True):
        # Get the regions as the count of unique areas in the dataframe
    regions = working_dataframe.area.unique().tolist()
    non_abs = regions.copy()
    non_abs.remove('Abs')
    random.shuffle(non_abs)

    # Initialize allocation dictionary
    allocation = {}

    if more_abs:
        if DEBUG:
            print("HI from more abs")
        exercise_amount -= 1  # Deduct 1 for Abs
        region_exercise = exercise_amount / len(regions)

        if DEBUG:
            print(f"region_exercise: {region_exercise}")

        # Check if region_exercise is a whole number
        if not region_exercise.is_integer():
            if DEBUG:
                print(f"region_exercise: {region_exercise}, int(region_exercise): {int(region_exercise)}",
                      "length of regions:", len(regions), region_exercise - int(region_exercise))

            # Calculate how many regions get an extra exercise
            remainder = exercise_amount % len(regions)
            base_exercises = exercise_amount // len(regions)

            # Assign exercises to regions
            for i, region in enumerate(regions):
                if region == 'Abs':
                    allocation[region] = base_exercises + 1
                else:
                    if i < remainder:
                        allocation[region] = base_exercises + 1
                    else:
                        allocation[region] = base_exercises
        else:
            if DEBUG:
                print(f"region_exercise is a whole number: {region_exercise}")
            for region in regions:
                if region == 'Abs':
                    allocation[region] = int(region_exercise) + 1
                else:
                    allocation[region] = int(region_exercise)
    else:
        # Handle the case where more_abs is False
        region_exercise = exercise_amount / len(regions)
        for region in regions:
            allocation[region] = int(region_exercise)

    return allocation
