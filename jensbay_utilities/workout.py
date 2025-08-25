import pandas as pd

df = pd.read_clipboard()

df.rename(columns = {'Navn': 'exercise', 'Område': 'area', 'Sværhedsgrad':'diffucility'}, inplace = True)

df.sort_values(by=['area'], inplace=True)

def get_exercises(working_dataframe = df, area = 'Legs', diffuculty = 4, exercise_amount = 2):
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
    
    local_df = working_dataframe[working_dataframe.area == area]

    for i in range(1000):
        exercises = random.choices(local_df.exercise.tolist(), k = exercise_amount)

        unique = set(exercises)

        if len(unique) < exercise_amount:
            continue

        mean = local_df[local_df.exercise.isin(exercises)].diffucility.mean()
        
        if diffuculty - 0.5 < mean < diffuculty + 0.5:
            return exercises
    print(f"Could not find exercises for area {area} with difficulty {diffuculty} after 1000 tries.")    

    # now we ne need to make an empty list of the length exercise_amount
    output = ["" for i in range(exercise_amount)]
    return output


days = [3, 4, 5]

exercise_df = pd.DataFrame(columns=days)
# now we need to make information column, the row is 'diffuculty' so that we can insert the mean diffucilty
information = ['mean', 'Abs', 'Abs', 'Abs', 'Back', 'Back', 'Cardio','Cardio','Legs','Legs', 'Upper','Upper']
exercise_df['information'] = information
for day in days:
    exercises = []
    for area in df.area.unique():
        if area == 'Abs': 
            exercises.extend(get_exercises(df, area, diffuculty=day, exercise_amount=3))
        else:
            exercises.extend(get_exercises(df, area, diffuculty=day, exercise_amount=2))
    # Now we need 
    mean = df[df.exercise.isin(exercises)].diffucility.mean()
    exercises = [mean] + exercises 
    exercise_df[day] = exercises
    
    
# now we want a dataframe with the days as the columns and the exercise as the rows

exercise_df[['information', 3,4,5]]
