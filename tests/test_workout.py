import unittest
import pandas as pd
import numpy as np
from jensbay_utilities.workout import WorkoutGenerator, create_workout_from_dataframe


class TestWorkoutGenerator(unittest.TestCase):
    
    def setUp(self):
        self.sample_df = pd.DataFrame({
            'exercise': ['Push-ups', 'Squats', 'Crunches', 'Pull-ups', 'Lunges', 'Plank'],
            'area': ['Upper', 'Legs', 'Abs', 'Upper', 'Legs', 'Abs'],
            'diffucility': [3, 4, 2, 5, 3, 4]
        })
        self.generator = WorkoutGenerator(self.sample_df)
    
    def test_init_valid_dataframe(self):
        generator = WorkoutGenerator(self.sample_df)
        self.assertIsInstance(generator, WorkoutGenerator)
        self.assertFalse(generator.debug)
    
    def test_init_missing_columns(self):
        invalid_df = pd.DataFrame({
            'exercise': ['Push-ups'],
            'wrong_column': ['Upper']
        })
        with self.assertRaises(ValueError):
            WorkoutGenerator(invalid_df)
    
    def test_init_empty_dataframe(self):
        empty_df = pd.DataFrame(columns=['exercise', 'area', 'diffucility'])
        with self.assertRaises(ValueError):
            WorkoutGenerator(empty_df)
    
    def test_get_exercises_valid_area(self):
        exercises = self.generator.get_exercises('Upper', difficulty=4.0, exercise_amount=2)
        self.assertEqual(len(exercises), 2)
        self.assertIsInstance(exercises, list)
    
    def test_get_exercises_invalid_area(self):
        with self.assertRaises(ValueError):
            self.generator.get_exercises('NonExistent', difficulty=4.0, exercise_amount=2)
    
    def test_get_exercises_insufficient_exercises(self):
        exercises = self.generator.get_exercises('Upper', difficulty=4.0, exercise_amount=10)
        self.assertEqual(len(exercises), 10)
        self.assertTrue(any(ex == "" for ex in exercises))
    
    def test_get_area_allocations(self):
        allocations = self.generator.get_area_allocations(6, more_abs=True)
        self.assertIsInstance(allocations, dict)
        self.assertEqual(sum(allocations.values()), 6)
    
    def test_get_area_allocations_abs_bonus(self):
        allocations = self.generator.get_area_allocations(9, more_abs=True)
        if 'Abs' in allocations:
            other_areas = [v for k, v in allocations.items() if k != 'Abs']
            self.assertGreaterEqual(allocations['Abs'], max(other_areas))
    
    def test_generate_workout_plan(self):
        workout = self.generator.generate_workout_plan([3, 4, 5], use_area_coverage=False)
        self.assertIsInstance(workout, pd.DataFrame)
        self.assertTrue('information' in workout.columns)
        self.assertTrue(3 in workout.columns)
        self.assertTrue(4 in workout.columns)
        self.assertTrue(5 in workout.columns)
    
    def test_get_area_summary(self):
        summary = self.generator.get_area_summary()
        self.assertIsInstance(summary, pd.DataFrame)
        self.assertTrue('Exercise_Count' in summary.columns)
        self.assertTrue('Mean_Difficulty' in summary.columns)
    
    def test_find_exercises_by_difficulty(self):
        filtered = self.generator.find_exercises_by_difficulty(3.0, 4.0)
        self.assertIsInstance(filtered, pd.DataFrame)
        self.assertTrue(all(filtered.diffucility >= 3.0))
        self.assertTrue(all(filtered.diffucility <= 4.0))
    
    def test_create_workout_from_dataframe(self):
        workout = create_workout_from_dataframe(self.sample_df, days=[3, 4])
        self.assertIsInstance(workout, pd.DataFrame)
        self.assertTrue(3 in workout.columns)
        self.assertTrue(4 in workout.columns)


if __name__ == '__main__':
    unittest.main()