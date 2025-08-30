## File: jensbay_utilities/workput.py
import pandas as pd
import numpy as np
import random
from typing import List, Dict, Tuple, Optional, Union


class WorkoutGenerator:
    """
    Comprehensive workout generator that creates exercise routines from structured exercise data.
    
    ~~~
    • Validates and processes workout dataframes with exercise, area, and difficulty columns
    • Generates balanced workout routines based on specified parameters
    • Provides flexible allocation strategies for different muscle groups
    • Supports customizable difficulty targeting and exercise selection
    ~~~
    
    Returns type: generator (WorkoutGenerator) - initialized instance with methods for routine generation
    """
    
    def __init__(self, dataframe: pd.DataFrame, debug: bool = False):
        """
        Initialize the workout generator with exercise data.
        
        Args:
            dataframe (pd.DataFrame): Exercise dataframe with required columns:
                - 'exercise': Exercise name (str)
                - 'area': Muscle group/area (str) 
                - 'diffucility': Difficulty level (numeric)
            debug (bool): Enable debug output for troubleshooting
        
        Raises:
            ValueError: If required columns are missing from dataframe
        """
        self.df = dataframe.copy()
        self.debug = debug
        self._validate_dataframe()
        
    def _validate_dataframe(self) -> None:
        """
        Validates that the dataframe contains all required columns.
        
        ~~~
        • Checks for presence of 'exercise', 'area', 'diffucility' columns
        • Raises descriptive errors for missing columns
        ~~~
        
        Returns type: None (NoneType) - validates dataframe structure with no return value
        """
        required_columns = ['exercise', 'area', 'diffucility']
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        
        if missing_columns:
            raise ValueError(f"Dataframe missing required columns: {missing_columns}")
            
        if self.df.empty:
            raise ValueError("Dataframe cannot be empty")
    
    def get_exercises(self, area: str, difficulty: float = 4.0, 
                     exercise_amount: int = 2, tolerance: float = 0.5) -> List[str]:
        """
        Get exercises for a specific area matching target difficulty.
        
        ~~~
        • Filters exercises by muscle group area
        • Randomly selects unique exercises matching difficulty target
        • Uses iterative approach with tolerance for difficulty matching
        • Returns empty strings if unable to find suitable exercises
        ~~~
        
        Args:
            area (str): Target muscle group area
            difficulty (float): Target difficulty level
            exercise_amount (int): Number of exercises to select
            tolerance (float): Allowable deviation from target difficulty
            
        Returns type: exercises (List[str]) - exercise names matching criteria or empty strings if not found
        """
        if area not in self.df.area.unique():
            available_areas = list(self.df.area.unique())
            raise ValueError(f"Area '{area}' not found. Available areas: {available_areas}")
        
        local_df = self.df[self.df.area == area]
        
        if len(local_df) < exercise_amount:
            print(f"Warning: Only {len(local_df)} exercises available for area '{area}', requested {exercise_amount}")
            return local_df.exercise.tolist() + [""] * (exercise_amount - len(local_df))
        
        for attempt in range(1000):
            exercises = random.choices(local_df.exercise.tolist(), k=exercise_amount)
            
            unique_exercises = list(set(exercises))
            if len(unique_exercises) < exercise_amount:
                continue
            
            mean_difficulty = local_df[local_df.exercise.isin(exercises)].diffucility.mean()
            
            if abs(mean_difficulty - difficulty) <= tolerance:
                return exercises
        
        if self.debug:
            print(f"Could not find {exercise_amount} exercises for area '{area}' "
                  f"with difficulty {difficulty} ± {tolerance} after 1000 attempts")
        
        return [""] * exercise_amount
    
    def get_random_exercises_with_area_coverage(self, difficulty: float = 4.0, 
                                              exercise_amount: int = 11, tolerance: float = 0.5) -> List[str]:
        """
        Get random exercises ensuring at least 1 per area and targeting overall difficulty.
        
        ~~~
        • Ensures at least one exercise per available muscle group area
        • Randomly fills remaining slots from all exercises
        • Targets overall mean difficulty across all selected exercises
        • Returns mix of exercises covering all areas
        ~~~
        
        Args:
            difficulty (float): Target overall difficulty level
            exercise_amount (int): Total number of exercises to select
            tolerance (float): Allowable deviation from target difficulty
            
        Returns type: unique_exercises (List[str]) - exercise names ensuring coverage across all muscle areas
        """
        areas = self.df.area.unique().tolist()
        
        if exercise_amount < len(areas):
            raise ValueError(f"exercise_amount ({exercise_amount}) must be >= number of areas ({len(areas)})")
        
        for attempt in range(1000):
            selected_exercises = []
            
            # First, ensure at least 1 exercise per area
            for area in areas:
                area_exercises = self.df[self.df.area == area].exercise.tolist()
                if area_exercises:
                    selected_exercises.append(random.choice(area_exercises))
            
            # Fill remaining slots randomly from all exercises
            remaining_slots = exercise_amount - len(selected_exercises)
            if remaining_slots > 0:
                all_exercises = self.df.exercise.tolist()
                additional_exercises = random.choices(all_exercises, k=remaining_slots)
                selected_exercises.extend(additional_exercises)
            
            # Ensure all exercises are unique
            unique_exercises = list(set(selected_exercises))
            if len(unique_exercises) < exercise_amount:
                continue
            
            # Calculate mean difficulty
            mean_difficulty = self.df[self.df.exercise.isin(unique_exercises)].diffucility.mean()
            
            if abs(mean_difficulty - difficulty) <= tolerance:
                return unique_exercises[:exercise_amount]
        
        if self.debug:
            print(f"Could not find {exercise_amount} exercises with area coverage "
                  f"and difficulty {difficulty} ± {tolerance} after 1000 attempts")
        
        # Fallback: return at least one per area plus random fills
        fallback_exercises = []
        for area in areas:
            area_exercises = self.df[self.df.area == area].exercise.tolist()
            if area_exercises:
                fallback_exercises.append(random.choice(area_exercises))
        
        remaining = exercise_amount - len(fallback_exercises)
        if remaining > 0:
            all_exercises = self.df.exercise.tolist()
            fallback_exercises.extend(random.choices(all_exercises, k=remaining))
        
        return list(set(fallback_exercises))[:exercise_amount]
    
    def get_area_allocations(self, total_exercises: int, more_abs: bool = True) -> Dict[str, int]:
        """
        Calculate exercise allocation across different muscle group areas.
        
        ~~~
        • Distributes total exercises across available muscle group areas
        • Provides extra allocation for abs when more_abs is True
        • Handles remainder distribution for uneven divisions
        • Returns dictionary mapping areas to exercise counts
        ~~~
        
        Args:
            total_exercises (int): Total number of exercises to allocate
            more_abs (bool): Whether to give abs an extra exercise
            
        Returns type: Dict[str, int] mapping area names to exercise counts
        """
        areas = self.df.area.unique().tolist()
        allocation = {}
        
        if more_abs and 'Abs' in areas:
            remaining_exercises = total_exercises - 1
            base_per_area = remaining_exercises // len(areas)
            remainder = remaining_exercises % len(areas)
            
            for i, area in enumerate(areas):
                if area == 'Abs':
                    allocation[area] = base_per_area + 1 + (1 if i < remainder else 0)
                else:
                    allocation[area] = base_per_area + (1 if i < remainder else 0)
        else:
            base_per_area = total_exercises // len(areas)
            remainder = total_exercises % len(areas)
            
            for i, area in enumerate(areas):
                allocation[area] = base_per_area + (1 if i < remainder else 0)
        
        if self.debug:
            print(f"Area allocations: {allocation}")
            print(f"Total allocated: {sum(allocation.values())}")
        
        return allocation
    
    def generate_workout_plan(self, days: List[int], custom_allocations: Optional[Dict[str, int]] = None, 
                             use_area_coverage: bool = True) -> pd.DataFrame:
        """
        Generate a comprehensive workout plan for multiple days.
        
        ~~~
        • Creates workout routines for specified difficulty days
        • Uses area coverage method or traditional area allocations
        • Calculates mean difficulty for each workout day
        • Returns structured dataframe with exercises organized by day
        ~~~
        
        Args:
            days (List[int]): List of difficulty levels for each workout day
            custom_allocations (Optional[Dict[str, int]]): Custom exercise allocation per area
            use_area_coverage (bool): If True, ensures at least 1 exercise per area with random fill
            
        Returns type: pd.DataFrame with workout plan organized by days and areas
        """
        workout_df = pd.DataFrame()
        
        for day_difficulty in days:
            if use_area_coverage and not custom_allocations:
                # Use new method that ensures area coverage with random selection
                total_exercises = sum([3 if area == 'Abs' else 2 for area in self.df.area.unique()])
                day_exercises = self.get_random_exercises_with_area_coverage(
                    difficulty=day_difficulty, 
                    exercise_amount=total_exercises
                )
                
                # Create information rows based on actual exercise areas
                information_rows = ['mean']
                for exercise in day_exercises:
                    exercise_area = self.df[self.df.exercise == exercise].area.iloc[0] if len(self.df[self.df.exercise == exercise]) > 0 else 'Unknown'
                    information_rows.append(exercise_area)
                    
            else:
                # Use traditional area-based allocation method
                day_exercises = []
                
                if custom_allocations:
                    allocations = custom_allocations
                else:
                    total_exercises = sum([3 if area == 'Abs' else 2 for area in self.df.area.unique()])
                    allocations = self.get_area_allocations(total_exercises, more_abs=True)
                
                for area, count in allocations.items():
                    exercises = self.get_exercises(area, day_difficulty, count)
                    day_exercises.extend(exercises)
                
                information_rows = ['mean'] + [area for area, count in allocations.items() for _ in range(count)]
            
            mean_difficulty = self._calculate_mean_difficulty(day_exercises)
            workout_data = [mean_difficulty] + day_exercises
            
            workout_df[day_difficulty] = workout_data
        
        workout_df['information'] = information_rows
        
        return workout_df[['information'] + days]
    
    def _calculate_mean_difficulty(self, exercises: List[str]) -> float:
        """
        Calculate mean difficulty for a list of exercises.
        
        ~~~
        • Filters out empty exercise entries
        • Computes average difficulty from dataframe lookup
        • Returns 0.0 if no valid exercises provided
        ~~~
        
        Args:
            exercises (List[str]): List of exercise names
            
        Returns type: float representing mean difficulty level
        """
        valid_exercises = [ex for ex in exercises if ex and ex != ""]
        if not valid_exercises:
            return 0.0
        
        exercise_difficulties = self.df[self.df.exercise.isin(valid_exercises)].diffucility
        return exercise_difficulties.mean() if not exercise_difficulties.empty else 0.0
    
    def get_area_summary(self) -> pd.DataFrame:
        """
        Get summary statistics for each exercise area.
        
        ~~~
        • Groups exercises by muscle area
        • Calculates count, mean difficulty, and difficulty range
        • Provides overview of available exercises per area
        ~~~
        
        Returns type: pd.DataFrame with area statistics and exercise counts
        """
        summary = self.df.groupby('area').agg({
            'exercise': 'count',
            'diffucility': ['mean', 'min', 'max']
        }).round(2)
        
        summary.columns = ['Exercise_Count', 'Mean_Difficulty', 'Min_Difficulty', 'Max_Difficulty']
        summary = summary.reset_index()
        
        return summary
    
    def find_exercises_by_difficulty(self, min_difficulty: float, max_difficulty: float) -> pd.DataFrame:
        """
        Find all exercises within a specific difficulty range.
        
        ~~~
        • Filters exercises by difficulty bounds
        • Returns subset of dataframe matching criteria
        • Useful for targeting specific intensity levels
        ~~~
        
        Args:
            min_difficulty (float): Minimum difficulty threshold
            max_difficulty (float): Maximum difficulty threshold
            
        Returns type: pd.DataFrame filtered by difficulty range
        """
        return self.df[(self.df.diffucility >= min_difficulty) & (self.df.diffucility <= max_difficulty)]


def create_workout_from_dataframe(df: pd.DataFrame, days: List[int] = [3, 4, 5], 
                                 debug: bool = False, use_area_coverage: bool = True) -> pd.DataFrame:
    """
    Convenience function to create workout plan from dataframe.
    
    ~~~
    • Creates WorkoutGenerator instance from provided dataframe
    • Generates workout plan for specified difficulty days
    • Returns formatted workout dataframe ready for use
    ~~~
    
    Args:
        df (pd.DataFrame): Exercise dataframe with 'exercise', 'area', 'diffucility' columns
        days (List[int]): List of difficulty levels for workout days
        debug (bool): Enable debug output
        use_area_coverage (bool): If True, ensures at least 1 exercise per area with random selection
        
    Returns type: workout (pd.DataFrame) - complete workout plan organized by days and areas with difficulty targets
    
    Expected DataFrame Structure:
        - 'exercise': Name of the exercise (string)
        - 'area': Muscle group area (string, e.g., 'Legs', 'Arms', 'Abs', 'Back')
        - 'diffucility': Difficulty level (numeric, typically 1-5 or 1-10)
        
    Example Usage:
        >>> import pandas as pd
        >>> from jensbay_utilities import workput
        >>> 
        >>> # Your dataframe should look like:
        >>> df = pd.DataFrame({
        ...     'exercise': ['Push-ups', 'Squats', 'Crunches'],
        ...     'area': ['Upper', 'Legs', 'Abs'],
        ...     'diffucility': [3, 4, 2]
        ... })
        >>> 
        >>> # New method (default): ensures area coverage with random selection
        >>> workout_plan = workput.create_workout_from_dataframe(df, days=[3, 4, 5])
        >>> 
        >>> # Old method: uses area-specific allocations
        >>> workout_plan = workput.create_workout_from_dataframe(df, days=[3, 4, 5], use_area_coverage=False)
        >>> print(workout_plan)
    """
    generator = WorkoutGenerator(df, debug=debug)
    return generator.generate_workout_plan(days, use_area_coverage=use_area_coverage)