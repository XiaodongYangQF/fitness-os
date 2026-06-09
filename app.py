from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import re
from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
FOOD_DB_PATH = DATA_DIR / "food_database.csv"
FOOD_LOG_PATH = DATA_DIR / "food_log.csv"
WORKOUT_LOG_PATH = DATA_DIR / "workout_log.csv"
BODY_LOG_PATH = DATA_DIR / "body_log.csv"
LATEST_PLAN_PATH = DATA_DIR / "latest_meal_plan.csv"
EXERCISE_LIBRARY_PATH = DATA_DIR / "exercise_library.csv"
LATEST_TRAINING_PLAN_PATH = DATA_DIR / "latest_training_plan.csv"
WORKOUT_DETAIL_LOG_PATH = DATA_DIR / "workout_detail_log.csv"

DAILY_TARGETS = {
    "kcal_min": 1800,
    "kcal_max": 2200,
    "protein_min": 120,
    "protein_max": 140,
    "fiber_min": 25,
    "fiber_max": 35,
}

MEAL_TARGETS = {
    "Breakfast": {"kcal": 520, "protein": 35, "fiber": 8},
    "Lunch": {"kcal": 650, "protein": 45, "fiber": 10},
    "Dinner": {"kcal": 520, "protein": 40, "fiber": 8},
    "Snack": {"kcal": 180, "protein": 10, "fiber": 4},
}

CALORIE_TOLERANCE = {
    "Breakfast": 0.18,
    "Lunch": 0.18,
    "Dinner": 0.18,
    "Snack": 0.25,
}

CATEGORY_DEFAULT_GRAMS = {
    "protein": 180,
    "carb": 140,
    "vegetable": 120,
    "fruit": 120,
    "dairy": 250,
    "supplement": 30,
    "seasoning": 5,
    "seed": 8,
}

CATEGORY_LIMITS = {
    "protein": (100, 300),
    "carb": (60, 260),
    "vegetable": (30, 250),
    "fruit": (50, 250),
    "dairy": (50, 500),
    "supplement": (10, 50),
    "seasoning": (0, 30),
    "oil": (0, 30),
    "seed": (0, 30),
    "other": (0, 500),
}

PAGE_OPTIONS = ["Meal Planner", "Diet Log", "Training Planner", "Workout Log", "Progress", "Settings"]

MEAL_DEFAULT_FOODS = {
    "Breakfast": ["Low Fat Milk", "Oats", "Banana", "Blueberries", "Whey Protein"],
    "Lunch": ["Cooked Mixed Brown Rice", "Beef Tripe", "Lettuce", "Celery", "Enoki Mushrooms"],
    "Dinner": ["Mackerel", "Beef Omasum", "Lettuce", "Celery", "Enoki Mushrooms"],
    "Snack": ["Apple", "Banana"],
}

BREAKFAST_STAPLES = {
    "Low Fat Milk",
    "Oats",
    "Banana",
    "Blueberries",
    "Strawberries",
    "Whey Protein",
}

DEFAULT_EXERCISE_LIBRARY = [
    {
        "exercise_name": "Lat Pulldown",
        "aliases": "Pull Downs",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Vertical Pull",
        "primary_muscle": "Back / Lats",
        "equipment": "Cable Pulldown Machine",
        "difficulty": "Beginner",
        "joint_stress": "Low",
        "default_sets": 3,
        "default_reps": "8-12",
        "default_weight": 35,
        "rest_sec": 75,
        "rpe_range": "6-8",
        "cues": "Keep chest tall. Pull elbows down. Do not shrug.",
        "avoid_if": "Shoulder pain",
        "recorded_sets": 12,
        "recorded_weight_min": 12,
        "recorded_weight_max": 44,
        "notes": "From uploaded 12-week training record.",
    },
    {
        "exercise_name": "Kettlebell Squat",
        "aliases": "KB Squat",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Squat",
        "primary_muscle": "Quads / Glutes",
        "equipment": "Kettlebell",
        "difficulty": "Beginner",
        "joint_stress": "Moderate knee",
        "default_sets": 3,
        "default_reps": "10-12",
        "default_weight": 14,
        "rest_sec": 75,
        "rpe_range": "6-8",
        "cues": "Brace core. Sit between hips. Keep knees tracking over toes.",
        "avoid_if": "Knee pain above 3/10",
        "recorded_sets": 16,
        "recorded_weight_min": 8,
        "recorded_weight_max": 20,
        "notes": "Frequent exercise in uploaded record.",
    },
    {
        "exercise_name": "Incline Dumbbell Bench Press",
        "aliases": "Incline DB Bench Press",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Horizontal Push",
        "primary_muscle": "Chest / Front Delts / Triceps",
        "equipment": "Dumbbells + Incline Bench",
        "difficulty": "Beginner-Intermediate",
        "joint_stress": "Low-moderate shoulder",
        "default_sets": 3,
        "default_reps": "8-12",
        "default_weight": 10,
        "rest_sec": 75,
        "rpe_range": "6-8",
        "cues": "Control the lowering phase. Keep shoulder blades stable.",
        "avoid_if": "Shoulder pain",
        "recorded_sets": 13,
        "recorded_weight_min": 5,
        "recorded_weight_max": 12.5,
        "notes": "Dumbbell weight per hand if recorded that way.",
    },
    {
        "exercise_name": "Dumbbell Incline Row",
        "aliases": "DB Incline Row",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Horizontal Pull",
        "primary_muscle": "Back / Rear Delts",
        "equipment": "Dumbbells + Incline Bench",
        "difficulty": "Beginner",
        "joint_stress": "Low",
        "default_sets": 3,
        "default_reps": "10-12",
        "default_weight": 10,
        "rest_sec": 75,
        "rpe_range": "6-8",
        "cues": "Pull elbows back. Pause briefly. Avoid swinging.",
        "avoid_if": "Lower-back discomfort if setup is poor",
        "recorded_sets": 12,
        "recorded_weight_min": 6,
        "recorded_weight_max": 12.5,
        "notes": "Good joint-friendly pull exercise.",
    },
    {
        "exercise_name": "Prone Machine Hamstring Curl",
        "aliases": "Prone Machine Hamstring Curl",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Knee Flexion",
        "primary_muscle": "Hamstrings",
        "equipment": "Hamstring Curl Machine",
        "difficulty": "Beginner",
        "joint_stress": "Low knee",
        "default_sets": 3,
        "default_reps": "10-15",
        "default_weight": 25,
        "rest_sec": 60,
        "rpe_range": "6-8",
        "cues": "Control both directions. Do not lift hips from the pad.",
        "avoid_if": "Hamstring strain",
        "recorded_sets": 14,
        "recorded_weight_min": 15,
        "recorded_weight_max": 35,
        "notes": "Very suitable for strength rebuild.",
    },
    {
        "exercise_name": "Leg Extension",
        "aliases": "Leg Extension",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Knee Extension",
        "primary_muscle": "Quads",
        "equipment": "Leg Extension Machine",
        "difficulty": "Beginner",
        "joint_stress": "Moderate knee",
        "default_sets": 2,
        "default_reps": "10-15",
        "default_weight": 20,
        "rest_sec": 60,
        "rpe_range": "6-7",
        "cues": "Use controlled reps. Avoid locking knees hard.",
        "avoid_if": "Knee pain above 3/10",
        "recorded_sets": 5,
        "recorded_weight_min": 10,
        "recorded_weight_max": 30,
        "notes": "Use carefully if knee feels sensitive.",
    },
    {
        "exercise_name": "T-Bar Row",
        "aliases": "T-Bar Row",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Horizontal Pull",
        "primary_muscle": "Back / Lats / Mid Traps",
        "equipment": "T-Bar Row Machine",
        "difficulty": "Beginner-Intermediate",
        "joint_stress": "Low-moderate lower back",
        "default_sets": 3,
        "default_reps": "8-12",
        "default_weight": 12.5,
        "rest_sec": 75,
        "rpe_range": "6-8",
        "cues": "Neutral spine. Pull toward lower chest. Control the eccentric.",
        "avoid_if": "Lower-back pain",
        "recorded_sets": 7,
        "recorded_weight_min": 0,
        "recorded_weight_max": 13.5,
        "notes": "Machine setup may make 0kg meaningful as base load.",
    },
    {
        "exercise_name": "Dumbbell Renegade Row",
        "aliases": "DB Renegade Row",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Core + Horizontal Pull",
        "primary_muscle": "Back / Core",
        "equipment": "Dumbbells",
        "difficulty": "Intermediate",
        "joint_stress": "Moderate wrist/shoulder",
        "default_sets": 3,
        "default_reps": "8-10",
        "default_weight": 6,
        "rest_sec": 75,
        "rpe_range": "6-8",
        "cues": "Keep hips steady. Use light weights. Avoid twisting.",
        "avoid_if": "Wrist or shoulder pain",
        "recorded_sets": 12,
        "recorded_weight_min": 5,
        "recorded_weight_max": 6,
        "notes": "Keep as optional because it is technically harder.",
    },
    {
        "exercise_name": "Sit-Up",
        "aliases": "Sit-Up",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Core",
        "pattern": "Trunk Flexion",
        "primary_muscle": "Abs",
        "equipment": "Mat",
        "difficulty": "Beginner",
        "joint_stress": "Low-moderate spine",
        "default_sets": 3,
        "default_reps": "10-15",
        "default_weight": 0,
        "rest_sec": 45,
        "rpe_range": "6-8",
        "cues": "Move with control. Stop if lower back feels uncomfortable.",
        "avoid_if": "Lower-back pain",
        "recorded_sets": 9,
        "recorded_weight_min": 0,
        "recorded_weight_max": 5,
        "notes": "Can be replaced by Dead Bug for a more back-friendly option.",
    },
    {
        "exercise_name": "Barbell Bicep Curl",
        "aliases": "Barbell Bicep Curl",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Arm Curl",
        "primary_muscle": "Biceps",
        "equipment": "Barbell / EZ Bar",
        "difficulty": "Beginner",
        "joint_stress": "Low elbow",
        "default_sets": 2,
        "default_reps": "10-12",
        "default_weight": 15,
        "rest_sec": 60,
        "rpe_range": "6-8",
        "cues": "Keep elbows stable. Avoid swinging.",
        "avoid_if": "Elbow pain",
        "recorded_sets": 9,
        "recorded_weight_min": 10,
        "recorded_weight_max": 25,
        "notes": "Accessory exercise.",
    },
    {
        "exercise_name": "Cable Triceps Extension",
        "aliases": "Cable Tricep Extention",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Arm Extension",
        "primary_muscle": "Triceps",
        "equipment": "Cable Machine",
        "difficulty": "Beginner",
        "joint_stress": "Low elbow",
        "default_sets": 2,
        "default_reps": "10-12",
        "default_weight": 15,
        "rest_sec": 60,
        "rpe_range": "6-8",
        "cues": "Keep elbows tucked. Finish with control.",
        "avoid_if": "Elbow pain",
        "recorded_sets": 6,
        "recorded_weight_min": 10,
        "recorded_weight_max": 20,
        "notes": "Corrected spelling from uploaded record.",
    },
    {
        "exercise_name": "Assisted Dip",
        "aliases": "Dip",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Vertical Push",
        "primary_muscle": "Chest / Triceps",
        "equipment": "Assisted Dip Machine / Dip Station",
        "difficulty": "Intermediate",
        "joint_stress": "Moderate shoulder",
        "default_sets": 2,
        "default_reps": "8-10",
        "default_weight": 25,
        "rest_sec": 75,
        "rpe_range": "6-8",
        "cues": "Do not go too deep. Keep shoulders comfortable.",
        "avoid_if": "Shoulder pain",
        "recorded_sets": 6,
        "recorded_weight_min": 0,
        "recorded_weight_max": 45,
        "notes": "If this was assisted dip, higher number may mean more assistance.",
    },
    {
        "exercise_name": "Leg Press",
        "aliases": "Lep Press",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Squat",
        "primary_muscle": "Quads / Glutes",
        "equipment": "Leg Press Machine",
        "difficulty": "Beginner",
        "joint_stress": "Low-moderate knee",
        "default_sets": 3,
        "default_reps": "10-12",
        "default_weight": 40,
        "rest_sec": 90,
        "rpe_range": "6-8",
        "cues": "Control depth. Knees track over toes. Do not lock out aggressively.",
        "avoid_if": "Knee pain above 3/10",
        "recorded_sets": 7,
        "recorded_weight_min": 0,
        "recorded_weight_max": 40,
        "notes": "Corrected typo from uploaded record.",
    },
    {
        "exercise_name": "Incline Dumbbell Reverse Fly",
        "aliases": "Incline DB Reverse Fly",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Rear Delt Isolation",
        "primary_muscle": "Rear Delts / Upper Back",
        "equipment": "Dumbbells + Incline Bench",
        "difficulty": "Beginner",
        "joint_stress": "Low shoulder",
        "default_sets": 2,
        "default_reps": "10-15",
        "default_weight": 5,
        "rest_sec": 60,
        "rpe_range": "6-8",
        "cues": "Use light weights. Lead with elbows. Do not shrug.",
        "avoid_if": "Shoulder pain",
        "recorded_sets": 8,
        "recorded_weight_min": 4,
        "recorded_weight_max": 5,
        "notes": "Good posture/accessory movement.",
    },
    {
        "exercise_name": "Hip Adductor Machine",
        "aliases": "Inner Thigh",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Hip Adduction",
        "primary_muscle": "Adductors",
        "equipment": "Adductor Machine",
        "difficulty": "Beginner",
        "joint_stress": "Low hip/knee",
        "default_sets": 2,
        "default_reps": "10-15",
        "default_weight": 20,
        "rest_sec": 60,
        "rpe_range": "6-7",
        "cues": "Slow and controlled. Avoid bouncing.",
        "avoid_if": "Groin discomfort",
        "recorded_sets": 2,
        "recorded_weight_min": 14,
        "recorded_weight_max": 23,
        "notes": "Accessory lower-body machine.",
    },
    {
        "exercise_name": "Hip Abductor Machine",
        "aliases": "Outer Thigh",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Hip Abduction",
        "primary_muscle": "Glute Medius / Outer Hip",
        "equipment": "Abductor Machine",
        "difficulty": "Beginner",
        "joint_stress": "Low hip/knee",
        "default_sets": 2,
        "default_reps": "10-15",
        "default_weight": 20,
        "rest_sec": 60,
        "rpe_range": "6-7",
        "cues": "Control the movement. Keep torso stable.",
        "avoid_if": "Hip discomfort",
        "recorded_sets": 0,
        "recorded_weight_min": 0,
        "recorded_weight_max": 0,
        "notes": "Listed in uploaded Exercise sheet.",
    },
    {
        "exercise_name": "Barbell Hip Thrust",
        "aliases": "Barbell Hip Thrust",
        "source": "User 12-week programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Hip Hinge / Glute Bridge",
        "primary_muscle": "Glutes / Hamstrings",
        "equipment": "Barbell + Bench",
        "difficulty": "Beginner-Intermediate",
        "joint_stress": "Low knee",
        "default_sets": 3,
        "default_reps": "10-12",
        "default_weight": 20,
        "rest_sec": 75,
        "rpe_range": "6-8",
        "cues": "Chin tucked. Drive through heels. Pause at top.",
        "avoid_if": "Lower-back discomfort",
        "recorded_sets": 2,
        "recorded_weight_min": 5,
        "recorded_weight_max": 5,
        "notes": "Good option for glutes with lower knee stress.",
    },
    {
        "exercise_name": "Dumbbell Shoulder Press",
        "aliases": "DB Shoulder Press / Incline DB Bench Press (HG)",
        "source": "User note + programme",
        "selected": True,
        "category": "Strength",
        "pattern": "Vertical Push",
        "primary_muscle": "Shoulders / Triceps",
        "equipment": "Dumbbells",
        "difficulty": "Beginner-Intermediate",
        "joint_stress": "Moderate shoulder",
        "default_sets": 3,
        "default_reps": "8-10",
        "default_weight": 8,
        "rest_sec": 75,
        "rpe_range": "6-8",
        "cues": "Press slightly forward. Keep ribs down. Stop if shoulder pinches.",
        "avoid_if": "Shoulder pain",
        "recorded_sets": 12,
        "recorded_weight_min": 4,
        "recorded_weight_max": 12.5,
        "notes": "Workbook note says incline DB bench press is the same as DB shoulder press; confirm later.",
    },
    {
        "exercise_name": "Incline Walk",
        "aliases": "Treadmill Incline Walk",
        "source": "Recommended",
        "selected": False,
        "category": "Cardio",
        "pattern": "Low-impact Cardio",
        "primary_muscle": "Cardiorespiratory / Legs",
        "equipment": "Treadmill",
        "difficulty": "Beginner",
        "joint_stress": "Low-moderate ankle/knee",
        "default_sets": 0,
        "default_reps": "35-45 min",
        "default_weight": 0,
        "rest_sec": 0,
        "rpe_range": "Zone 2",
        "cues": "Speed 5.5-6.2 km/h, incline 8-12%, HR 125-145.",
        "avoid_if": "Sharp knee/ankle pain",
        "recorded_sets": 0,
        "recorded_weight_min": 0,
        "recorded_weight_max": 0,
        "notes": "Recommended for fat loss and joint-friendly conditioning.",
    },
    {
        "exercise_name": "Elliptical Zone 2",
        "aliases": "Elliptical",
        "source": "Recommended",
        "selected": False,
        "category": "Cardio",
        "pattern": "Low-impact Cardio",
        "primary_muscle": "Cardiorespiratory / Legs",
        "equipment": "Elliptical",
        "difficulty": "Beginner",
        "joint_stress": "Low",
        "default_sets": 0,
        "default_reps": "30-45 min",
        "default_weight": 0,
        "rest_sec": 0,
        "rpe_range": "Zone 2",
        "cues": "Keep HR 125-140. Smooth rhythm. Avoid chasing calories.",
        "avoid_if": "Unusual joint pain",
        "recorded_sets": 0,
        "recorded_weight_min": 0,
        "recorded_weight_max": 0,
        "notes": "Recommended recovery cardio.",
    },
    {
        "exercise_name": "Bike Zone 2",
        "aliases": "Stationary Bike",
        "source": "Recommended",
        "selected": False,
        "category": "Cardio",
        "pattern": "Low-impact Cardio",
        "primary_muscle": "Cardiorespiratory / Legs",
        "equipment": "Bike",
        "difficulty": "Beginner",
        "joint_stress": "Low",
        "default_sets": 0,
        "default_reps": "30-45 min",
        "default_weight": 0,
        "rest_sec": 0,
        "rpe_range": "Zone 2",
        "cues": "Keep cadence smooth. HR 120-140.",
        "avoid_if": "Knee discomfort from bike setup",
        "recorded_sets": 0,
        "recorded_weight_min": 0,
        "recorded_weight_max": 0,
        "notes": "Alternative low-impact cardio.",
    },
    {
        "exercise_name": "Dead Bug",
        "aliases": "Dead Bug",
        "source": "Recommended",
        "selected": False,
        "category": "Core",
        "pattern": "Anti-extension",
        "primary_muscle": "Core",
        "equipment": "Mat",
        "difficulty": "Beginner",
        "joint_stress": "Low",
        "default_sets": 3,
        "default_reps": "8-10 each side",
        "default_weight": 0,
        "rest_sec": 45,
        "rpe_range": "6-7",
        "cues": "Keep lower back gently pressed down. Move slowly.",
        "avoid_if": "None; generally back-friendly",
        "recorded_sets": 0,
        "recorded_weight_min": 0,
        "recorded_weight_max": 0,
        "notes": "Recommended core replacement for sit-up when back is tired.",
    },
    {
        "exercise_name": "Pallof Press",
        "aliases": "Cable Pallof Press",
        "source": "Recommended",
        "selected": False,
        "category": "Core",
        "pattern": "Anti-rotation",
        "primary_muscle": "Core / Obliques",
        "equipment": "Cable Machine",
        "difficulty": "Beginner",
        "joint_stress": "Low",
        "default_sets": 3,
        "default_reps": "10 each side",
        "default_weight": 10,
        "rest_sec": 45,
        "rpe_range": "6-7",
        "cues": "Do not rotate. Brace core. Move slowly.",
        "avoid_if": "Shoulder discomfort",
        "recorded_sets": 0,
        "recorded_weight_min": 0,
        "recorded_weight_max": 0,
        "notes": "Recommended joint-friendly core exercise.",
    },
    {
        "exercise_name": "Face Pull",
        "aliases": "Cable Face Pull",
        "source": "Recommended",
        "selected": False,
        "category": "Strength",
        "pattern": "Upper Back / Shoulder Health",
        "primary_muscle": "Rear Delts / Rotator Cuff",
        "equipment": "Cable Machine",
        "difficulty": "Beginner",
        "joint_stress": "Low shoulder",
        "default_sets": 2,
        "default_reps": "12-15",
        "default_weight": 10,
        "rest_sec": 45,
        "rpe_range": "6-7",
        "cues": "Pull toward face. Keep elbows high. Use light load.",
        "avoid_if": "Shoulder pain",
        "recorded_sets": 0,
        "recorded_weight_min": 0,
        "recorded_weight_max": 0,
        "notes": "Recommended for posture and shoulder balance.",
    },
]

SESSION_TEMPLATES = {
    "Full Body A": [
        ("Warm-up", "Incline Walk"),
        ("Strength", "Leg Press"),
        ("Strength", "Lat Pulldown"),
        ("Strength", "Incline Dumbbell Bench Press"),
        ("Strength", "Dumbbell Incline Row"),
        ("Accessory", "Prone Machine Hamstring Curl"),
        ("Core", "Dead Bug"),
        ("Conditioning", "Elliptical Zone 2"),
    ],
    "Full Body B": [
        ("Warm-up", "Incline Walk"),
        ("Strength", "Kettlebell Squat"),
        ("Strength", "T-Bar Row"),
        ("Strength", "Dumbbell Shoulder Press"),
        ("Accessory", "Leg Extension"),
        ("Accessory", "Cable Triceps Extension"),
        ("Accessory", "Barbell Bicep Curl"),
        ("Accessory", "Incline Dumbbell Reverse Fly"),
    ],
    "Lower + Core": [
        ("Warm-up", "Incline Walk"),
        ("Strength", "Kettlebell Squat"),
        ("Strength", "Leg Press"),
        ("Accessory", "Prone Machine Hamstring Curl"),
        ("Accessory", "Barbell Hip Thrust"),
        ("Accessory", "Hip Adductor Machine"),
        ("Core", "Dead Bug"),
    ],
    "Upper + Conditioning": [
        ("Warm-up", "Elliptical Zone 2"),
        ("Strength", "Lat Pulldown"),
        ("Strength", "T-Bar Row"),
        ("Strength", "Incline Dumbbell Bench Press"),
        ("Strength", "Dumbbell Incline Row"),
        ("Accessory", "Face Pull"),
        ("Accessory", "Cable Triceps Extension"),
        ("Accessory", "Barbell Bicep Curl"),
    ],
    "Recovery Cardio": [
        ("Warm-up", "Incline Walk"),
        ("Cardio", "Elliptical Zone 2"),
        ("Cardio", "Bike Zone 2"),
        ("Core", "Dead Bug"),
    ],
}


def ensure_files() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    if not FOOD_DB_PATH.exists():
        pd.DataFrame(
            [
                ["Banana", "fruit", "g", 89, 1.1, 22.8, 0.3, 2.6],
                ["Blueberries", "fruit", "g", 57, 0.7, 14.5, 0.3, 2.4],
                ["Strawberries", "fruit", "g", 32, 0.7, 7.7, 0.3, 2.0],
                ["Apple", "fruit", "g", 52, 0.3, 14.0, 0.2, 2.4],
                ["Oats", "carb", "g", 389, 16.9, 66.3, 6.9, 10.6],
                ["Low Fat Milk", "dairy", "ml", 46, 3.4, 4.8, 1.5, 0],
                ["Whey Protein", "supplement", "g", 390, 78, 8, 6, 0],
                ["Cooked Mixed Brown Rice", "carb", "g", 125, 2.7, 26.0, 1.0, 1.8],
                ["Beef Tripe", "protein", "g", 78, 14.5, 0, 1.8, 0],
                ["Beef Omasum", "protein", "g", 72, 13.2, 0, 1.6, 0],
                ["Mackerel", "protein", "g", 205, 22, 0, 13, 0],
                ["Mussels", "protein", "g", 86, 12, 3.7, 2.2, 0],
                ["Prawns", "protein", "g", 99, 24, 0.2, 0.3, 0],
                ["Lettuce", "vegetable", "g", 15, 1.4, 2.9, 0.2, 1.3],
                ["Celery", "vegetable", "g", 14, 0.7, 1.8, 0.2, 1.4],
                ["Enoki Mushrooms", "vegetable", "g", 37, 2.7, 7.8, 0.3, 2.7],
                ["Seaweed Flakes", "seasoning", "g", 306, 7, 45, 3, 30],
                ["Chia Seeds", "seed", "g", 486, 16.5, 42.1, 30.7, 34.4],
            ],
            columns=[
                "food_name",
                "category",
                "unit",
                "kcal_per_100g",
                "protein_per_100g",
                "carbs_per_100g",
                "fat_per_100g",
                "fiber_per_100g",
            ],
        ).to_csv(FOOD_DB_PATH, index=False)

    if not EXERCISE_LIBRARY_PATH.exists():
        pd.DataFrame(DEFAULT_EXERCISE_LIBRARY).to_csv(EXERCISE_LIBRARY_PATH, index=False)

    for path, cols in [
        (FOOD_LOG_PATH, ["date", "meal", "food_name", "weight_g", "kcal", "protein", "carbs", "fat", "fiber"]),
        (WORKOUT_LOG_PATH, ["date", "type", "duration_min", "distance_km", "avg_hr", "active_kcal", "knee_pain", "ankle_pain", "rpe", "notes"]),
        (WORKOUT_DETAIL_LOG_PATH, ["date", "session_name", "exercise_name", "section", "set_index", "planned_sets", "planned_reps", "planned_weight", "actual_sets", "actual_reps", "actual_weight", "rpe", "completed", "notes"]),
        (LATEST_TRAINING_PLAN_PATH, ["session_name", "section", "exercise_name", "sets", "reps", "target_weight", "rest_sec", "rpe_range", "duration_min", "note"]),
        (BODY_LOG_PATH, ["date", "morning_weight", "evening_weight", "waist_cm", "stool_status", "notes"]),
    ]:
        if not path.exists():
            pd.DataFrame(columns=cols).to_csv(path, index=False)


@st.cache_data
def load_food_db() -> pd.DataFrame:
    df = pd.read_csv(FOOD_DB_PATH)
    df = df.copy()
    df["food_name"] = df["food_name"].astype(str)
    df["category"] = df["category"].astype(str).str.lower()

    # Personal database cleanup:
    # Keep eggplant simple. For fat-loss tracking, cooking style is less useful than
    # separating the vegetable from added oil. Remove raw/steamed/roasted/braised
    # aubergine variants and use one clean entry instead.
    aubergine_mask = df["food_name"].str.lower().str.contains("aubergine|eggplant", regex=True, na=False)
    df = df.loc[~aubergine_mask].copy()

    extra_foods = pd.DataFrame(
        [
            {
                "food_name": "Aubergine / Eggplant",
                "category": "vegetable",
                "unit": "g",
                "kcal_per_100g": 25,
                "protein_per_100g": 1.0,
                "carbs_per_100g": 5.9,
                "fat_per_100g": 0.2,
                "fiber_per_100g": 3.0,
            },
            {
                "food_name": "Cooking Oil / Spray Oil",
                "category": "oil",
                "unit": "g",
                "kcal_per_100g": 884,
                "protein_per_100g": 0,
                "carbs_per_100g": 0,
                "fat_per_100g": 100,
                "fiber_per_100g": 0,
            },
        ]
    )

    existing_names = set(df["food_name"].str.lower())
    extra_foods = extra_foods[~extra_foods["food_name"].str.lower().isin(existing_names)]
    df = pd.concat([df, extra_foods], ignore_index=True)

    df["display"] = df["food_name"] + "  ·  " + df["category"].str.title()
    return df


def load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def append_csv(path: Path, rows: List[Dict]) -> None:
    old = load_csv(path)
    new = pd.DataFrame(rows)
    pd.concat([old, new], ignore_index=True).to_csv(path, index=False)


def safe_key(text: str) -> str:
    return (
        str(text)
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
        .replace("·", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "_")
        .lower()
    )


def calc_row(food: pd.Series, weight_g: float) -> Dict:
    factor = weight_g / 100.0
    return {
        "food_name": food["food_name"],
        "category": food["category"],
        "weight_g": round(float(weight_g), 1),
        "kcal": round(float(food["kcal_per_100g"]) * factor, 1),
        "protein": round(float(food["protein_per_100g"]) * factor, 1),
        "carbs": round(float(food["carbs_per_100g"]) * factor, 1),
        "fat": round(float(food["fat_per_100g"]) * factor, 1),
        "fiber": round(float(food["fiber_per_100g"]) * factor, 1),
    }


def meal_totals(df: pd.DataFrame) -> Dict[str, float]:
    if df.empty:
        return {k: 0.0 for k in ["kcal", "protein", "carbs", "fat", "fiber"]}
    return {k: round(float(df[k].sum()), 1) for k in ["kcal", "protein", "carbs", "fat", "fiber"]}


def calculate_meal_from_weights(food_db: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    rows = []
    for food_name, weight in weights.items():
        food_match = food_db[food_db["food_name"] == food_name]
        if food_match.empty or float(weight) <= 0:
            continue
        rows.append(calc_row(food_match.iloc[0], float(weight)))
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["category", "food_name"])


def generate_meal(food_db: pd.DataFrame, selected_foods: List[str], meal_type: str) -> pd.DataFrame:
    if not selected_foods:
        return pd.DataFrame()

    selected = food_db[food_db["food_name"].isin(selected_foods)].copy()
    if selected.empty:
        return pd.DataFrame()

    weights: Dict[str, float] = {}
    for _, row in selected.iterrows():
        weights[row["food_name"]] = CATEGORY_DEFAULT_GRAMS.get(row["category"], 100)

    target = MEAL_TARGETS.get(meal_type, MEAL_TARGETS["Lunch"])

    def build() -> pd.DataFrame:
        return pd.DataFrame([calc_row(row, weights[row["food_name"]]) for _, row in selected.iterrows()])

    # Protein adjustment
    for _ in range(12):
        m = build()
        totals = meal_totals(m)
        protein_foods = selected[selected["category"] == "protein"]
        if protein_foods.empty:
            break
        if totals["protein"] < target["protein"] * 0.9:
            for name in protein_foods["food_name"]:
                lo, hi = CATEGORY_LIMITS["protein"]
                weights[name] = min(hi, weights[name] + 15)
        elif totals["protein"] > target["protein"] * 1.25:
            for name in protein_foods["food_name"]:
                lo, hi = CATEGORY_LIMITS["protein"]
                weights[name] = max(lo, weights[name] - 10)
        else:
            break

    # Calorie adjustment via carbs
    for _ in range(12):
        m = build()
        totals = meal_totals(m)
        carb_foods = selected[selected["category"] == "carb"]
        if carb_foods.empty:
            break
        if totals["kcal"] < target["kcal"] * 0.85:
            for name in carb_foods["food_name"]:
                lo, hi = CATEGORY_LIMITS["carb"]
                weights[name] = min(hi, weights[name] + 15)
        elif totals["kcal"] > target["kcal"] * 1.10:
            for name in carb_foods["food_name"]:
                lo, hi = CATEGORY_LIMITS["carb"]
                weights[name] = max(lo, weights[name] - 15)
        else:
            break


    # Final calorie pass: the automatically generated plan should normally be
    # inside the meal-specific calorie range. This prevents the generated plan
    # itself from showing a calorie warning before the user manually adjusts it.
    low_kcal, high_kcal = calorie_band(meal_type)
    for _ in range(18):
        m = build()
        totals = meal_totals(m)

        if low_kcal <= totals["kcal"] <= high_kcal:
            break

        carb_foods = selected[selected["category"] == "carb"]
        protein_foods = selected[selected["category"] == "protein"]

        if totals["kcal"] < low_kcal:
            if not carb_foods.empty:
                for name in carb_foods["food_name"]:
                    lo, hi = CATEGORY_LIMITS["carb"]
                    weights[name] = min(hi, weights[name] + 10)
            elif not protein_foods.empty:
                for name in protein_foods["food_name"]:
                    lo, hi = CATEGORY_LIMITS["protein"]
                    weights[name] = min(hi, weights[name] + 10)
            else:
                break

        elif totals["kcal"] > high_kcal:
            if not carb_foods.empty:
                for name in carb_foods["food_name"]:
                    lo, hi = CATEGORY_LIMITS["carb"]
                    weights[name] = max(lo, weights[name] - 10)
            elif not protein_foods.empty:
                for name in protein_foods["food_name"]:
                    lo, hi = CATEGORY_LIMITS["protein"]
                    weights[name] = max(lo, weights[name] - 10)
            else:
                break


    # Fiber control
    m = build()
    totals = meal_totals(m)
    if totals["fiber"] > target["fiber"] * 1.4:
        for _, row in selected[selected["category"] == "vegetable"].iterrows():
            lo, _ = CATEGORY_LIMITS["vegetable"]
            weights[row["food_name"]] = max(lo, weights[row["food_name"]] - 30)

    return build().sort_values(["category", "food_name"])


def save_latest_plan(meal_type: str, plan_df: pd.DataFrame) -> None:
    if plan_df.empty:
        return
    out = plan_df.copy()
    out.insert(0, "planned_at", str(date.today()))
    out.insert(1, "meal", meal_type)
    out.to_csv(LATEST_PLAN_PATH, index=False)


def load_latest_plan() -> pd.DataFrame:
    if LATEST_PLAN_PATH.exists():
        return pd.read_csv(LATEST_PLAN_PATH)
    return pd.DataFrame()


def food_group(food_name: str, category: str) -> str:
    if food_name in BREAKFAST_STAPLES:
        return "Breakfast Staples"
    category = str(category).lower()
    if category in {"protein", "carb", "vegetable", "fruit", "dairy", "supplement", "seasoning", "oil", "seed"}:
        return category.title()
    return "Other"


def build_food_groups(food_db: pd.DataFrame, meal_type: str) -> Dict[str, pd.DataFrame]:
    df = food_db.copy()
    df["group"] = [food_group(name, cat) for name, cat in zip(df["food_name"], df["category"])]

    if meal_type == "Breakfast":
        order = ["Breakfast Staples", "Fruit", "Dairy", "Supplement", "Carb", "Protein", "Vegetable", "Seed", "Oil", "Other"]
    else:
        order = ["Protein", "Carb", "Vegetable", "Seasoning", "Oil", "Fruit", "Dairy", "Supplement", "Seed", "Other"]

    groups: Dict[str, pd.DataFrame] = {}
    for group_name in order:
        g = df[df["group"] == group_name].sort_values("food_name")
        if not g.empty:
            groups[group_name] = g
    return groups


def dual_weight_input(food_name: str, category: str, default_weight: float, key_prefix: str) -> float:
    cat = str(category).lower()
    lo, hi = CATEGORY_LIMITS.get(cat, CATEGORY_LIMITS["other"])
    max_value = float(max(hi, default_weight + 50, 100))
    base_key = f"{key_prefix}_{safe_key(food_name)}"
    value_key = f"{base_key}_value"
    slider_key = f"{base_key}_slider"
    number_key = f"{base_key}_number"

    if value_key not in st.session_state:
        st.session_state[value_key] = float(default_weight)
    if slider_key not in st.session_state:
        st.session_state[slider_key] = float(default_weight)
    if number_key not in st.session_state:
        st.session_state[number_key] = float(default_weight)

    def sync_from_slider() -> None:
        value = float(st.session_state[slider_key])
        st.session_state[value_key] = value
        st.session_state[number_key] = value

    def sync_from_number() -> None:
        value = float(st.session_state[number_key])
        value = max(float(lo), min(value, max_value))
        st.session_state[value_key] = value
        st.session_state[slider_key] = value
        st.session_state[number_key] = value

    c1, c2 = st.columns([2.2, 1])
    with c1:
        st.slider(
            food_name,
            min_value=float(lo),
            max_value=max_value,
            step=5.0,
            key=slider_key,
            on_change=sync_from_slider,
        )
    with c2:
        st.number_input(
            "g/ml",
            min_value=float(lo),
            max_value=max_value,
            step=5.0,
            format="%.0f",
            key=number_key,
            on_change=sync_from_number,
            label_visibility="collapsed",
        )

    return float(st.session_state[value_key])


def ingredient_selector(food_db: pd.DataFrame, meal_type: str, default_selected: List[str], key_prefix: str) -> List[str]:
    default_selected_set = set(default_selected)
    selected_foods: List[str] = []

    st.caption("Select ingredients first. The app will generate reasonable weights in the next step.")

    groups = build_food_groups(food_db, meal_type)
    for group_name, group_df in groups.items():
        expanded = group_name in {"Breakfast Staples", "Protein", "Carb", "Vegetable"}
        with st.expander(group_name, expanded=expanded):
            cols = st.columns(2)
            for i, (_, row) in enumerate(group_df.iterrows()):
                food_name = row["food_name"]
                category = str(row["category"]).title()
                unit = str(row.get("unit", "g"))
                checked = cols[i % 2].checkbox(
                    f"{food_name}",
                    value=food_name in default_selected_set,
                    help=f"{category} · {float(row['kcal_per_100g']):.0f} kcal/100{unit}",
                    key=f"{key_prefix}_select_{safe_key(meal_type)}_{safe_key(food_name)}",
                )
                if checked:
                    selected_foods.append(food_name)

    return selected_foods


def plan_weight_editor(food_db: pd.DataFrame, plan_df: pd.DataFrame, key_prefix: str) -> pd.DataFrame:
    if plan_df.empty:
        return pd.DataFrame()

    st.subheader("Adjust weights")
    st.caption("Use the slider for quick adjustment, or type the exact weight in the box.")

    weights: Dict[str, float] = {}
    for _, row in plan_df.iterrows():
        food_name = row["food_name"]
        category = str(row["category"]).lower()
        default_weight = float(row["weight_g"])

        with st.container():
            weights[food_name] = dual_weight_input(
                food_name=food_name,
                category=category,
                default_weight=default_weight,
                key_prefix=key_prefix,
            )

    return calculate_meal_from_weights(food_db, weights)


def food_picker_with_weights(
    food_db: pd.DataFrame,
    meal_type: str,
    default_selected: List[str],
    weight_defaults: Dict[str, float],
    key_prefix: str,
) -> pd.DataFrame:
    """Food groups are visible. Checked foods show slider + exact input."""
    default_selected_set = set(default_selected)
    groups = build_food_groups(food_db, meal_type)

    st.caption("Select foods from the list, then use slider or exact input for weights.")

    weights: Dict[str, float] = {}
    for group_name, group_df in groups.items():
        expanded = group_name in {"Breakfast Staples", "Protein", "Carb", "Vegetable"}
        with st.expander(group_name, expanded=expanded):
            for _, row in group_df.iterrows():
                food_name = row["food_name"]
                category = str(row["category"]).title()
                unit = str(row.get("unit", "g"))
                checked_key = f"{key_prefix}_check_{safe_key(meal_type)}_{safe_key(food_name)}"

                checked = st.checkbox(
                    f"{food_name}",
                    value=food_name in default_selected_set,
                    help=f"{category} · {float(row['kcal_per_100g']):.0f} kcal/100{unit}",
                    key=checked_key,
                )

                if checked:
                    default_weight = weight_defaults.get(
                        food_name,
                        CATEGORY_DEFAULT_GRAMS.get(str(row["category"]).lower(), 100),
                    )
                    weights[food_name] = dual_weight_input(
                        food_name=food_name,
                        category=str(row["category"]),
                        default_weight=float(default_weight),
                        key_prefix=f"{key_prefix}_weight_{safe_key(meal_type)}",
                    )

    return calculate_meal_from_weights(food_db, weights)


def show_meal_summary(edited: pd.DataFrame, meal_type: str) -> Dict[str, float]:
    totals = meal_totals(edited)
    c1, c2, c3 = st.columns(3)
    c1.metric("Calories", f"{totals['kcal']:.0f} kcal")
    c2.metric("Protein", f"{totals['protein']:.1f} g")
    c3.metric("Fiber", f"{totals['fiber']:.1f} g")

    if totals["fiber"] > MEAL_TARGETS[meal_type]["fiber"] * 1.4:
        st.warning("Fiber is high. If stool is watery, reduce raw vegetables, apples or chia seeds for a few days.")
    if totals["protein"] < MEAL_TARGETS[meal_type]["protein"] * 0.8:
        st.warning("Protein is low. Add beef tripe, beef omasum, mackerel, mussels, prawns or whey.")

    with st.expander("Nutrition breakdown"):
        st.dataframe(
            edited[["food_name", "weight_g", "kcal", "protein", "carbs", "fat", "fiber"]],
            use_container_width=True,
            hide_index=True,
        )

    return totals


def training_recommendation(
    yesterday_type: str,
    avg_hr: int,
    knee_pain: int,
    ankle_pain: int,
    fatigue: int,
    goal: str,
) -> Tuple[str, List[str]]:
    pain = max(knee_pain, ankle_pain)
    high_load_run = yesterday_type in ["5 km Run", "Outdoor Run", "Treadmill Run"] and avg_hr >= 150

    if pain >= 4:
        return "Recovery / Joint-friendly Day", [
            "Elliptical: 30-40 min, target HR 120-135 bpm.",
            "Do not run today. Finish with 8-10 min calf, glute and hip mobility.",
            "If pain persists or worsens, reduce training and consider seeing a doctor or physiotherapist.",
        ]

    if pain >= 2 or high_load_run or fatigue >= 7:
        return "Low-impact Zone 2 Day", [
            "Treadmill incline walk: 35-45 min, speed 5.5-6.2 km/h, incline 8%-10%.",
            "Target HR 125-140 bpm. You should be able to speak in full sentences.",
            "No HIIT, no sprinting, and do not chase high Apple Watch calories.",
        ]

    if goal == "Recovery Cardio":
        return "Easy Cardio Day", [
            "Incline walk 40 min or elliptical 35 min.",
            "Target HR 125-140 bpm.",
            "Eat normally after training and hit your protein target.",
        ]

    if goal == "Fat-loss Cardio":
        return "Zone 2 Fat-loss Day", [
            "Treadmill incline walk: 40-50 min, speed 6.0 km/h, incline 8%-12%.",
            "Target HR 130-145 bpm.",
            "If your knee or ankle feels uncomfortable, switch to the elliptical immediately.",
        ]

    if goal == "Strength Training":
        return "Beginner Strength + Light Cardio", [
            "Full-body strength 35-45 min: Leg Press / Chest Press / Seated Row / Lat Pulldown / RDL, 2-3 sets each.",
            "8-12 reps per set, RPE 6-7. Do not train to failure.",
            "Finish with elliptical 10-15 min, HR 120-135 bpm.",
        ]

    return "Balanced Day", [
        "Easy run 20-25 min or incline walk 40 min.",
        "Target HR 130-145 bpm.",
        "After training, record average HR, active kcal, knee status and ankle status.",
    ]


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --card-bg: #ffffff;
            --card-border: #dbeafe;
            --muted: #667085;
            --accent: #2563eb;
            --accent-strong: #1d4ed8;
            --accent-soft: #eff6ff;
            --accent-line: #bfdbfe;
            --dark: #0f172a;
        }

        .stApp { background: #ffffff; }

        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 6.5rem !important;
            max-width: 940px !important;
        }

        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stSidebar"] {
            display: none !important;
        }

        h1, h2, h3 { letter-spacing: -0.02em; }

        div[data-testid="stMetric"] {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 14px 16px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        }

        div[data-testid="stMetricLabel"] { color: var(--muted); }

        .mobile-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 16px 18px;
            margin: 10px 0;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        }

        .hero-card {
            background: linear-gradient(135deg, #0f3b89 0%, #2563eb 58%, #38bdf8 100%);
            color: white;
            border-radius: 24px;
            padding: 22px 20px;
            margin: 4px 0 16px 0;
            box-shadow: 0 12px 36px rgba(29, 78, 216, 0.25);
        }

        .hero-card h1 { margin: 0; font-size: 2.0rem; }

        .hero-card p {
            margin: 8px 0 0 0;
            color: rgba(255,255,255,0.82);
        }

        .pill {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: #eef4ff;
            color: #1d4ed8;
            font-size: 0.85rem;
            font-weight: 600;
            margin: 4px 6px 4px 0;
        }

        .meal-template {
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 14px 16px;
            margin: 10px 0;
            background: white;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        }

        .meal-template-title {
            font-weight: 800;
            font-size: 1.05rem;
            margin-bottom: 4px;
        }

        .meal-template-body {
            color: #667085;
            line-height: 1.55;
        }

        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 99999;
            background: rgba(255,255,255,0.96);
            border-top: 1px solid #e5e7eb;
            padding: 8px 8px 12px 8px;
            display: flex;
            justify-content: space-around;
            gap: 6px;
            box-shadow: 0 -8px 24px rgba(15, 23, 42, 0.08);
        }

        .bottom-nav a {
            text-decoration: none !important;
            color: #475467 !important;
            font-size: 0.76rem;
            font-weight: 700;
            padding: 8px 6px;
            border-radius: 14px;
            text-align: center;
            min-width: 54px;
        }

        .bottom-nav a.active {
            background: #eef4ff;
            color: #1d4ed8 !important;
        }

        .stButton button,
        .stDownloadButton button {
            border-radius: 999px;
            min-height: 44px;
            font-weight: 700;
        }

        div[data-testid="stExpander"] {
            border-radius: 18px;
            border-color: #e8edf3;
        }


        .panel-card {
            background: #ffffff;
            border: 1px solid var(--card-border);
            border-radius: 22px;
            padding: 18px 18px;
            margin: 8px 0 16px 0;
            box-shadow: 0 10px 28px rgba(37, 99, 235, 0.08);
        }

        .panel-title {
            font-weight: 900;
            font-size: 1.05rem;
            margin-bottom: 4px;
            color: #0f172a;
        }

        .panel-subtitle {
            color: #667085;
            font-size: 0.88rem;
            margin-bottom: 12px;
        }

        .result-card {
            background: linear-gradient(180deg, #ffffff 0%, #eff6ff 100%);
            border: 1px solid var(--accent-line);
            border-radius: 18px;
            padding: 14px 14px;
            margin-bottom: 12px;
            box-shadow: 0 8px 22px rgba(37, 99, 235, 0.06);
        }

        .result-label {
            color: #1d4ed8;
            font-size: 0.82rem;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .result-value {
            color: #0f172a;
            font-size: 1.45rem;
            font-weight: 900;
            line-height: 1.15;
        }

        .result-note {
            color: #667085;
            font-size: 0.82rem;
            line-height: 1.35;
        }

        .status-good {
            display: inline-block;
            padding: 7px 10px;
            border-radius: 999px;
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
            font-weight: 800;
            font-size: 0.82rem;
            margin: 4px 4px 4px 0;
        }

        .status-warn {
            display: inline-block;
            padding: 7px 10px;
            border-radius: 999px;
            background: #fffbeb;
            color: #b45309;
            border: 1px solid #fde68a;
            font-weight: 800;
            font-size: 0.82rem;
            margin: 4px 4px 4px 0;
        }

        .workflow-step {
            color: #2563eb;
            font-weight: 900;
            font-size: 0.86rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 8px;
        }

        .small-divider {
            height: 1px;
            background: #dbeafe;
            margin: 12px 0 16px 0;
        }

        .success-animation {
            border: 1px solid #93c5fd;
            border-radius: 18px;
            padding: 14px 16px;
            margin: 12px 0;
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            color: #1d4ed8;
            font-weight: 900;
            box-shadow: 0 10px 28px rgba(37, 99, 235, 0.14);
            animation: successPulse 1.15s ease-out;
        }

        .success-animation .check {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            border-radius: 999px;
            background: #2563eb;
            color: white;
            margin-right: 8px;
            animation: checkPop 0.55s ease-out;
        }

        @keyframes successPulse {
            0% { transform: translateY(8px); opacity: 0; box-shadow: 0 0 0 rgba(37, 99, 235, 0); }
            55% { transform: translateY(0); opacity: 1; box-shadow: 0 0 0 10px rgba(37, 99, 235, 0.10); }
            100% { transform: translateY(0); opacity: 1; box-shadow: 0 10px 28px rgba(37, 99, 235, 0.14); }
        }

        @keyframes checkPop {
            0% { transform: scale(0.65); opacity: 0; }
            70% { transform: scale(1.12); opacity: 1; }
            100% { transform: scale(1.0); opacity: 1; }
        }

        /* Streamlit widgets: push everything toward the same blue theme */
        .stButton button,
        .stDownloadButton button {
            border-radius: 999px;
            min-height: 44px;
            font-weight: 800;
            border-color: #bfdbfe !important;
        }

        .stButton button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, #2563eb 0%, #38bdf8 100%) !important;
            color: white !important;
            border: 0 !important;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.22);
        }

        div[data-testid="stExpander"] {
            border-radius: 18px;
            border-color: #dbeafe !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.04);
        }

        div[data-baseweb="radio"] label,
        div[role="radiogroup"] label {
            border-color: #bfdbfe !important;
        }

        div[data-baseweb="radio"] label:has(input:checked),
        div[role="radiogroup"] label:has(input:checked) {
            background: #eff6ff !important;
            border-color: #2563eb !important;
            color: #1d4ed8 !important;
        }

        [data-testid="stSlider"] [role="slider"] {
            background-color: #2563eb !important;
            border-color: #2563eb !important;
        }

        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 99999;
            background: rgba(255,255,255,0.96);
            border-top: 1px solid #bfdbfe;
            padding: 8px 8px 12px 8px;
            display: flex;
            justify-content: space-around;
            gap: 6px;
            box-shadow: 0 -8px 24px rgba(37, 99, 235, 0.10);
        }

        .bottom-nav a {
            text-decoration: none !important;
            color: #475467 !important;
            font-size: 0.76rem;
            font-weight: 800;
            padding: 8px 6px;
            border-radius: 14px;
            text-align: center;
            min-width: 54px;
        }

        .bottom-nav a.active {
            background: #eff6ff;
            color: #1d4ed8 !important;
            border: 1px solid #bfdbfe;
        }


        /* v0.9 unified blue control overrides */
        html, body, [class*="css"] {
            --primary-color: #2563eb;
            --primary: #2563eb;
        }

        /* Sliders */
        [data-testid="stSlider"] [role="slider"] {
            background: #2563eb !important;
            border-color: #2563eb !important;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.14) !important;
        }

        [data-testid="stSlider"] [data-baseweb="slider"] div {
            color: #2563eb !important;
        }

        [data-testid="stSlider"] [data-baseweb="slider"] div[style*="background"] {
            background-color: #2563eb !important;
        }

        /* Checkbox and radio controls */
        [data-baseweb="checkbox"] svg,
        [data-testid="stCheckbox"] svg {
            color: #2563eb !important;
            fill: #2563eb !important;
        }

        [data-baseweb="checkbox"] div[aria-checked="true"],
        [data-testid="stCheckbox"] div[aria-checked="true"] {
            background-color: #2563eb !important;
            border-color: #2563eb !important;
        }

        [role="radiogroup"] label:has(input:checked) {
            background: #eff6ff !important;
            color: #1d4ed8 !important;
            border-color: #bfdbfe !important;
        }

        [role="radiogroup"] input:checked + div,
        [data-baseweb="radio"] input:checked + div {
            background-color: #2563eb !important;
            border-color: #2563eb !important;
        }

        /* Numeric inputs focus */
        input:focus,
        textarea:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 1px #2563eb !important;
        }

        /* Remove red Streamlit accents when selected */
        [aria-checked="true"] {
            border-color: #2563eb !important;
        }

        /* Buttons */
        .stButton button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 65%, #38bdf8 100%) !important;
            color: white !important;
            border: 0 !important;
        }


        /* v0.10 softer selected states and tooltip polish */
        [role="radiogroup"] label:has(input:checked),
        div[data-baseweb="radio"] label:has(input:checked) {
            background: #eff6ff !important;
            color: #1d4ed8 !important;
            border-color: #bfdbfe !important;
            box-shadow: inset 0 0 0 1px #bfdbfe !important;
        }

        [role="radiogroup"] label:has(input:checked) *,
        div[data-baseweb="radio"] label:has(input:checked) * {
            background-color: transparent !important;
            color: #1d4ed8 !important;
        }

        [role="radiogroup"] input:checked + div,
        [data-baseweb="radio"] input:checked + div {
            background-color: #2563eb !important;
            border-color: #2563eb !important;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12) !important;
        }

        [data-testid="stTooltipIcon"],
        button[data-testid="stTooltipIcon"] {
            background: #2563eb !important;
            border-radius: 999px !important;
            width: 18px !important;
            height: 18px !important;
            min-width: 18px !important;
            min-height: 18px !important;
            padding: 0 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            border: 1px solid #1d4ed8 !important;
            box-shadow: 0 3px 8px rgba(37, 99, 235, 0.18) !important;
        }

        [data-testid="stTooltipIcon"] svg,
        button[data-testid="stTooltipIcon"] svg,
        [data-testid="stTooltipIcon"] svg path,
        button[data-testid="stTooltipIcon"] svg path {
            color: #ffffff !important;
            fill: #ffffff !important;
            stroke: #ffffff !important;
        }

        /* Extra fallback for Streamlit help icons in some versions */
        [aria-label="Show help tooltip"] {
            background: #2563eb !important;
            border-radius: 999px !important;
            color: #ffffff !important;
            border: 1px solid #1d4ed8 !important;
        }

        [aria-label="Show help tooltip"] svg,
        [aria-label="Show help tooltip"] svg path {
            color: #ffffff !important;
            fill: #ffffff !important;
            stroke: #ffffff !important;
        }


        /* v0.11 pill-style meal type selector */
        div[data-testid="stRadio"] div[role="radiogroup"] {
            gap: 0.6rem !important;
            flex-wrap: wrap !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label {
            border: 1px solid #dbeafe !important;
            border-radius: 999px !important;
            padding: 8px 16px !important;
            min-height: 42px !important;
            background: #ffffff !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.04) !important;
            transition: all 0.18s ease !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            border-color: #93c5fd !important;
            background: #eff6ff !important;
        }

        /* Hide the default radio circle, so the choice looks like a clean pill tab */
        div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
            display: none !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            border-color: #1d4ed8 !important;
            border-radius: 999px !important;
            color: #ffffff !important;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.22) !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) *,
        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,
        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) span,
        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) div {
            color: #ffffff !important;
            background: transparent !important;
            border-radius: 999px !important;
            font-weight: 800 !important;
        }

        /* Remove the old square selected inner block effect */
        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) > div,
        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) > div > div {
            background: transparent !important;
            box-shadow: none !important;
        }

        /* Keep tooltip icon: blue background + white question mark */
        [data-testid="stTooltipIcon"],
        button[data-testid="stTooltipIcon"],
        [aria-label="Show help tooltip"] {
            background: #2563eb !important;
            color: #ffffff !important;
            border-radius: 999px !important;
            border: 1px solid #1d4ed8 !important;
        }

        [data-testid="stTooltipIcon"] svg,
        button[data-testid="stTooltipIcon"] svg,
        [data-testid="stTooltipIcon"] svg path,
        button[data-testid="stTooltipIcon"] svg path,
        [aria-label="Show help tooltip"] svg,
        [aria-label="Show help tooltip"] svg path {
            color: #ffffff !important;
            fill: #ffffff !important;
            stroke: #ffffff !important;
        }

        @media (max-width: 640px) {
            div[data-testid="stRadio"] div[role="radiogroup"] {
                gap: 0.45rem !important;
            }

            div[data-testid="stRadio"] div[role="radiogroup"] label {
                padding: 7px 13px !important;
                min-height: 40px !important;
            }
        }

        @media (max-width: 640px) {
            .block-container {
                padding-top: 0.25rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            .hero-card h1 { font-size: 1.65rem; }

            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
            }

            div[data-testid="stDataFrame"] { font-size: 0.78rem; }

            .bottom-nav a {
                min-width: 45px;
                font-size: 0.66rem;
                padding: 8px 3px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_page() -> str:
    raw = st.query_params.get("page", "Meal Planner")
    if isinstance(raw, list):
        raw = raw[0]
    page = str(raw)
    return page if page in PAGE_OPTIONS else "Meal Planner"


def bottom_nav(current_page: str) -> None:
    items = [
        ("Meal Planner", "🍽️", "Plan"),
        ("Diet Log", "📝", "Diet"),
        ("Training Planner", "🏋️", "Train"),
        ("Workout Log", "⌚", "Log"),
        ("Progress", "📈", "Progress"),
        ("Settings", "⚙️", "Settings"),
    ]

    links = []
    for key, icon, label in items:
        active = "active" if current_page == key else ""
        links.append(f'<a class="{active}" href="?page={key}">{icon}<br>{label}</a>')

    st.markdown(f'<div class="bottom-nav">{"".join(links)}</div>', unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero-card">
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, text: str) -> None:
    st.markdown(
        f"""
        <div class="mobile-card">
          <strong>{title}</strong><br>
          <span style="color:#667085;">{text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel_header(step: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="workflow-step">{step}</div>
        <div class="panel-title">{title}</div>
        <div class="panel-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def result_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="result-card">
          <div class="result-label">{label}</div>
          <div class="result-value">{value}</div>
          <div class="result-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def animated_success(message: str) -> None:
    if hasattr(st, "toast"):
        st.toast(message, icon="✅")

    st.markdown(
        f"""
        <div class="success-animation">
          <span class="check">✓</span>{message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def calorie_band(meal_type: str) -> Tuple[float, float]:
    target = MEAL_TARGETS[meal_type]["kcal"]
    tol = CALORIE_TOLERANCE.get(meal_type, 0.18)
    return target * (1 - tol), target * (1 + tol)


def calorie_status(totals: Dict[str, float], meal_type: str) -> str:
    low, high = calorie_band(meal_type)
    if totals["kcal"] < low:
        return "low"
    if totals["kcal"] > high:
        return "high"
    return "good"


def nutrition_status_badges(
    totals: Dict[str, float],
    meal_type: str,
    show_calorie_warning: bool = True,
) -> None:
    target = MEAL_TARGETS[meal_type]
    badges = []

    if totals["protein"] >= target["protein"] * 0.9:
        badges.append("<span class='status-good'>Protein target reached</span>")
    else:
        badges.append("<span class='status-warn'>Protein is low</span>")

    if totals["fiber"] <= target["fiber"] * 1.4:
        badges.append("<span class='status-good'>Fiber is moderate</span>")
    else:
        badges.append("<span class='status-warn'>Fiber is high</span>")

    c_status = calorie_status(totals, meal_type)
    if c_status == "good":
        badges.append("<span class='status-good'>Calories are balanced</span>")
    elif show_calorie_warning:
        if c_status == "low":
            badges.append("<span class='status-warn'>Calories are low</span>")
        else:
            badges.append("<span class='status-warn'>Calories are high</span>")

    st.markdown("".join(badges), unsafe_allow_html=True)


def nutrition_results_panel(
    edited: pd.DataFrame,
    meal_type: str,
    context: str = "Plan",
    show_calorie_warning: bool = True,
) -> Dict[str, float]:
    totals = meal_totals(edited)
    low, high = calorie_band(meal_type)

    result_card("Calories", f"{totals['kcal']:.0f} kcal", f"Target range: {low:.0f}-{high:.0f} kcal")
    result_card("Protein", f"{totals['protein']:.1f} g", f"Target: {MEAL_TARGETS[meal_type]['protein']}g")
    result_card("Fiber", f"{totals['fiber']:.1f} g", f"Target: around {MEAL_TARGETS[meal_type]['fiber']}g")
    result_card("Carbs / Fat", f"{totals['carbs']:.1f}g / {totals['fat']:.1f}g", "Balance check")

    nutrition_status_badges(totals, meal_type, show_calorie_warning=show_calorie_warning)

    if show_calorie_warning:
        c_status = calorie_status(totals, meal_type)
        if c_status == "low":
            st.info("Calories are below the target range. This can be fine for a light meal, but check whether the whole day is still enough.")
        elif c_status == "high":
            st.warning("Calories are above the target range. Check rice, oil, nuts/seeds, or fatty fish portions.")

    if totals["fiber"] > MEAL_TARGETS[meal_type]["fiber"] * 1.4:
        st.warning("Fiber is high. If stool is watery, reduce raw vegetables, apples or chia seeds for a few days.")
    if totals["protein"] < MEAL_TARGETS[meal_type]["protein"] * 0.8:
        st.warning("Protein is low. Add beef tripe, beef omasum, mackerel, mussels, prawns or whey.")

    return totals


def compact_breakdown(edited: pd.DataFrame) -> None:
    with st.expander("Nutrition breakdown"):
        st.dataframe(
            edited[["food_name", "weight_g", "kcal", "protein", "carbs", "fat", "fiber"]],
            use_container_width=True,
            hide_index=True,
        )


def meal_template_card(title: str, items: List[str], kcal: str, protein: str) -> None:
    body = "<br>".join(items)
    st.markdown(
        f"""
        <div class="meal-template">
          <div class="meal-template-title">{title}</div>
          <div class="meal-template-body">{body}</div>
          <div style="margin-top:8px;">
            <span class="pill">{kcal}</span>
            <span class="pill">{protein}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def suggested_foods(food_db: pd.DataFrame, foods: List[str]) -> List[str]:
    available = set(food_db["food_name"].tolist())
    return [f for f in foods if f in available]


def meal_planner_page(food_db: pd.DataFrame) -> None:
    hero("Meal Planner", "Professional meal workflow: select ingredients, generate weights, review nutrition.")

    meal_type = st.radio("Meal type", list(MEAL_TARGETS.keys()), horizontal=True, index=1, key="planner_meal_type")

    left, middle, right = st.columns([1.05, 1.35, 0.9], gap="large")

    with left:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        panel_header("Step 1", "Food Selection", "Choose foods from grouped ingredient lists.")
        default_selected = suggested_foods(food_db, MEAL_DEFAULT_FOODS[meal_type])
        selected_foods = ingredient_selector(food_db, meal_type, default_selected, key_prefix="planner")

        st.markdown("<div class='small-divider'></div>", unsafe_allow_html=True)
        if st.button("Generate Meal Plan", type="primary", use_container_width=True):
            generated = generate_meal(food_db, selected_foods, meal_type)
            st.session_state["active_meal_type"] = meal_type
            st.session_state["active_meal_plan"] = generated
            st.session_state["meal_plan_generated_animation"] = True
        st.markdown("</div>", unsafe_allow_html=True)

    generated = st.session_state.get("active_meal_plan", pd.DataFrame())
    generated_meal_type = st.session_state.get("active_meal_type", meal_type)

    if st.session_state.pop("meal_plan_generated_animation", False):
        animated_success("Meal plan generated. Suggested weights are ready.")

    edited = pd.DataFrame()

    with middle:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        panel_header("Step 2", "Suggested Weights", "Use sliders for quick changes, or type exact grams from your kitchen scale.")

        if generated.empty:
            st.info("Select ingredients on the left, then click Generate Meal Plan.")
        else:
            st.caption(f"Active plan: {generated_meal_type}")
            edited = plan_weight_editor(food_db, generated, key_prefix="planner_edit")
            compact_breakdown(edited)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        panel_header("Step 3", "Nutrition Results", "Quick decision cards for fat-loss planning.")

        if edited.empty:
            result_card("Calories", "—", "Generate a plan first")
            result_card("Protein", "—", "Generate a plan first")
            result_card("Fiber", "—", "Generate a plan first")
        else:
            totals = nutrition_results_panel(edited, generated_meal_type, context="Planned meal", show_calorie_warning=False)
            st.caption(
                f"Planner total: {totals['kcal']:.0f} kcal · "
                f"{totals['protein']:.1f}g protein · {totals['fiber']:.1f}g fiber"
            )
            if st.button("Use this plan in Diet Log", use_container_width=True):
                save_latest_plan(generated_meal_type, edited)
                animated_success("Plan saved. You can now open Diet Log and choose the date.")
        st.markdown("</div>", unsafe_allow_html=True)


def diet_log_page(food_db: pd.DataFrame) -> None:
    hero("Diet Log", "Date-indexed cooking and food record. Use your latest plan as the default, then adjust actual weights.")

    latest = load_latest_plan()
    has_latest = not latest.empty

    latest_meal_type = None
    if has_latest and "meal" in latest.columns:
        latest_meal_type = str(latest["meal"].iloc[0])

    default_meal_index = list(MEAL_TARGETS.keys()).index(latest_meal_type) if latest_meal_type in MEAL_TARGETS else 1

    left, middle, right = st.columns([1.05, 1.35, 0.9], gap="large")

    with left:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        panel_header("Step 1", "Date & Meal", "Choose the date you want to record, not necessarily today.")

        log_date = st.date_input(
            "Log date",
            value=date.today() + timedelta(days=1),
            help="For example, if you cook tomorrow's lunch today, choose tomorrow's date.",
        )
        meal_type = st.radio("Meal", list(MEAL_TARGETS.keys()), horizontal=False, index=default_meal_index, key="diet_log_meal_type")

        use_latest = False
        latest_for_meal = pd.DataFrame()
        if has_latest and latest_meal_type == meal_type:
            use_latest = st.checkbox("Use latest generated meal plan", value=True)
            latest_for_meal = latest.copy()
        elif has_latest:
            st.caption(f"Latest saved plan is for {latest_meal_type}. Select that meal type to use it.")

        st.markdown("</div>", unsafe_allow_html=True)

    if use_latest and not latest_for_meal.empty:
        default_selected = latest_for_meal["food_name"].tolist()
        weight_defaults = dict(zip(latest_for_meal["food_name"], latest_for_meal["weight_g"]))
    else:
        default_selected = suggested_foods(food_db, MEAL_DEFAULT_FOODS[meal_type])
        weight_defaults = {}

    edited = pd.DataFrame()

    with middle:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        panel_header("Step 2", "Actual Weights", "Keep the planned weights or adjust them based on your kitchen scale.")

        edited = food_picker_with_weights(
            food_db=food_db,
            meal_type=meal_type,
            default_selected=default_selected,
            weight_defaults=weight_defaults,
            key_prefix=f"diet_log_{safe_key(str(log_date))}",
        )

        if edited.empty:
            st.info("Select at least one food.")
        else:
            compact_breakdown(edited)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        panel_header("Step 3", "Log Results", "Review nutrition, then save to the selected date.")

        if edited.empty:
            result_card("Calories", "—", "Select foods first")
            result_card("Protein", "—", "Select foods first")
            result_card("Fiber", "—", "Select foods first")
        else:
            totals = nutrition_results_panel(edited, meal_type, context="Actual meal")
            st.caption(
                f"Selected date: {log_date} · {meal_type} · "
                f"{totals['kcal']:.0f} kcal · {totals['protein']:.1f}g protein"
            )

            if st.button("Save to Diet Log", type="primary", use_container_width=True):
                rows = []
                for _, row in edited.iterrows():
                    rows.append(
                        {
                            "date": str(log_date),
                            "meal": meal_type,
                            "food_name": row["food_name"],
                            "weight_g": row["weight_g"],
                            "kcal": row["kcal"],
                            "protein": row["protein"],
                            "carbs": row["carbs"],
                            "fat": row["fat"],
                            "fiber": row["fiber"],
                        }
                    )
                append_csv(FOOD_LOG_PATH, rows)
                animated_success(f"Saved {meal_type} for {log_date}.")
        st.markdown("</div>", unsafe_allow_html=True)



@st.cache_data
def load_exercise_library() -> pd.DataFrame:
    df = pd.read_csv(EXERCISE_LIBRARY_PATH)
    if "selected" in df.columns:
        df["selected"] = df["selected"].astype(str).str.lower().isin(["true", "1", "yes"])
    return df


def get_exercise_row(ex_df: pd.DataFrame, exercise_name: str) -> Dict:
    match = ex_df[ex_df["exercise_name"] == exercise_name]
    if match.empty:
        return {
            "exercise_name": exercise_name,
            "category": "Strength",
            "pattern": "General",
            "primary_muscle": "General",
            "equipment": "Gym",
            "difficulty": "Beginner",
            "joint_stress": "Moderate",
            "default_sets": 3,
            "default_reps": "10",
            "default_weight": 0,
            "rest_sec": 60,
            "rpe_range": "6-8",
            "cues": "",
            "avoid_if": "",
            "notes": "",
        }
    return match.iloc[0].to_dict()


def training_status_badges(intensity: str, joint_stress: str, time_min: int) -> None:
    badges = [
        f"<span class='status-good'>{time_min} min</span>",
        f"<span class='status-good'>{intensity}</span>",
    ]
    if "High" in str(joint_stress):
        badges.append("<span class='status-warn'>High joint stress</span>")
    elif "Moderate" in str(joint_stress):
        badges.append("<span class='status-warn'>Moderate joint stress</span>")
    else:
        badges.append("<span class='status-good'>Joint-friendly</span>")

    st.markdown("".join(badges), unsafe_allow_html=True)


def choose_session_focus(goal: str, preferred_focus: str, knee: int, ankle: int, fatigue: int) -> Tuple[str, str]:
    pain = max(knee, ankle)
    if pain >= 4 or fatigue >= 8:
        return "Recovery Cardio", "Modified because pain/fatigue is high."
    if pain >= 2 and preferred_focus in ["Lower + Core", "Full Body B"]:
        return "Upper + Conditioning", "Modified to reduce lower-body joint stress."
    if goal == "Recovery":
        return "Recovery Cardio", "Recovery goal selected."
    if preferred_focus == "Auto":
        if goal == "Strength Rebuild":
            return "Full Body A", "Auto-selected for strength rebuild."
        if goal == "Fat Loss + Conditioning":
            return "Upper + Conditioning", "Auto-selected for conditioning while keeping strength work."
        return "Full Body A", "Auto-selected balanced full-body session."
    return preferred_focus, "Using selected focus."


def build_training_session(
    ex_df: pd.DataFrame,
    goal: str,
    preferred_focus: str,
    available_min: int,
    knee: int,
    ankle: int,
    fatigue: int,
) -> Tuple[str, pd.DataFrame, str]:
    focus, reason = choose_session_focus(goal, preferred_focus, knee, ankle, fatigue)
    template = SESSION_TEMPLATES.get(focus, SESSION_TEMPLATES["Full Body A"])

    rows = []
    for section, exercise_name in template:
        ex = get_exercise_row(ex_df, exercise_name)
        category = ex.get("category", "Strength")

        if category == "Cardio":
            duration = 8 if section == "Warm-up" else 20
            sets = 0
            reps = str(ex.get("default_reps", "20 min"))
            target_weight = 0
        else:
            duration = 0
            sets = int(float(ex.get("default_sets", 3) or 3))
            reps = str(ex.get("default_reps", "10"))
            target_weight = float(ex.get("default_weight", 0) or 0)

        rows.append(
            {
                "session_name": focus,
                "section": section,
                "exercise_name": exercise_name,
                "sets": sets,
                "reps": reps,
                "target_weight": target_weight,
                "rest_sec": int(float(ex.get("rest_sec", 60) or 60)),
                "rpe_range": str(ex.get("rpe_range", "6-8")),
                "duration_min": duration,
                "note": str(ex.get("cues", "")),
                "joint_stress": str(ex.get("joint_stress", "Moderate")),
                "primary_muscle": str(ex.get("primary_muscle", "")),
            }
        )

    session = pd.DataFrame(rows)

    # Trim if time is short
    if available_min <= 35:
        keep_sections = ["Warm-up", "Strength", "Core", "Cardio"]
        session = session[session["section"].isin(keep_sections)].head(6)
    elif available_min <= 45:
        session = session[session["section"] != "Accessory"].append(session[session["section"] == "Accessory"].head(2), ignore_index=True) if False else session.head(7)

    title = f"{focus} · {goal}"
    return title, session.reset_index(drop=True), reason


def save_latest_training_plan(session_df: pd.DataFrame) -> None:
    if session_df.empty:
        return
    cols = ["session_name", "section", "exercise_name", "sets", "reps", "target_weight", "rest_sec", "rpe_range", "duration_min", "note"]
    session_df[cols].to_csv(LATEST_TRAINING_PLAN_PATH, index=False)


def load_latest_training_plan() -> pd.DataFrame:
    if LATEST_TRAINING_PLAN_PATH.exists():
        return pd.read_csv(LATEST_TRAINING_PLAN_PATH)
    return pd.DataFrame()


def training_plan_card(session_df: pd.DataFrame) -> None:
    if session_df.empty:
        st.info("Generate a session first.")
        return

    for section in session_df["section"].drop_duplicates():
        st.markdown(f"**{section}**")
        sub = session_df[session_df["section"] == section]
        for _, row in sub.iterrows():
            if int(row.get("sets", 0) or 0) == 0:
                text = f"{row['exercise_name']} · {row.get('duration_min', 0)} min · {row.get('rpe_range', '')}"
            else:
                weight = row.get("target_weight", 0)
                weight_text = f"{weight:g} kg" if float(weight) > 0 else "bodyweight"
                text = f"{row['exercise_name']} · {int(row['sets'])} × {row['reps']} · {weight_text} · rest {int(row['rest_sec'])}s"
            st.markdown(f"<span class='pill'>{text}</span>", unsafe_allow_html=True)


def programme_overview_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Weeks 1-4", "Adaptation", "3 strength + 2 low-impact cardio", "RPE 6-7, rebuild movement skill"],
            ["Weeks 5-8", "Progression", "3 strength + 2-3 cardio", "Add small load/reps when form is good"],
            ["Weeks 9-12", "Consolidation", "3 strength + conditioning", "Keep joints happy, improve consistency"],
        ],
        columns=["Phase", "Focus", "Weekly structure", "Progression rule"],
    )


def weekly_template_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Day 1", "Full Body A", "Strength + easy conditioning"],
            ["Day 2", "Zone 2 Cardio", "Incline walk / elliptical / bike"],
            ["Day 3", "Full Body B", "Strength rebuild"],
            ["Day 4", "Recovery", "Light cardio + mobility"],
            ["Day 5", "Upper + Conditioning", "Upper strength + low-impact cardio"],
            ["Day 6", "Optional", "Table tennis, easy walk, or rest"],
            ["Day 7", "Rest", "Recovery and meal prep"],
        ],
        columns=["Day", "Session", "Purpose"],
    )



def parse_default_reps(reps_text: str) -> int:
    nums = re.findall(r"\d+", str(reps_text))
    if not nums:
        return 10
    nums = [int(x) for x in nums]
    if len(nums) >= 2:
        return int(round(sum(nums[:2]) / 2))
    return nums[0]


def dual_value_input(
    label: str,
    min_value: float,
    max_value: float,
    default_value: float,
    step: float,
    key_prefix: str,
    unit: str = "",
) -> float:
    value_key = f"{key_prefix}_value"
    slider_key = f"{key_prefix}_slider"
    number_key = f"{key_prefix}_number"

    default_value = float(default_value)
    if value_key not in st.session_state:
        st.session_state[value_key] = default_value
    if slider_key not in st.session_state:
        st.session_state[slider_key] = default_value
    if number_key not in st.session_state:
        st.session_state[number_key] = default_value

    def sync_from_slider() -> None:
        value = float(st.session_state[slider_key])
        st.session_state[value_key] = value
        st.session_state[number_key] = value

    def sync_from_number() -> None:
        value = float(st.session_state[number_key])
        value = max(float(min_value), min(value, float(max_value)))
        st.session_state[value_key] = value
        st.session_state[slider_key] = value
        st.session_state[number_key] = value

    c1, c2 = st.columns([2.2, 0.9])
    with c1:
        st.slider(
            label,
            min_value=float(min_value),
            max_value=float(max_value),
            value=float(st.session_state[value_key]),
            step=float(step),
            key=slider_key,
            on_change=sync_from_slider,
        )
    with c2:
        st.number_input(
            unit or label,
            min_value=float(min_value),
            max_value=float(max_value),
            value=float(st.session_state[value_key]),
            step=float(step),
            format="%.0f" if step >= 1 else "%.1f",
            key=number_key,
            on_change=sync_from_number,
            label_visibility="collapsed",
        )

    return float(st.session_state[value_key])


def set_row_card(exercise_name: str, set_no: int, planned_weight: float, planned_reps: int, key_prefix: str) -> Dict:
    st.markdown(
        f"""
        <div class="mobile-card" style="padding:12px 14px; margin:8px 0;">
            <strong>{exercise_name} · Set {set_no}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    done = st.checkbox(
        f"Completed Set {set_no}",
        value=False,
        key=f"{key_prefix}_completed_{set_no}",
        help="Tick this after you finish the set.",
    )

    weight_max = max(100.0, float(planned_weight) + 60.0)
    weight = dual_value_input(
        "Weight",
        min_value=0.0,
        max_value=weight_max,
        default_value=float(planned_weight),
        step=2.5,
        key_prefix=f"{key_prefix}_weight_{set_no}",
        unit="kg",
    )

    reps = dual_value_input(
        "Reps",
        min_value=0.0,
        max_value=max(30.0, float(planned_reps) + 10.0),
        default_value=float(planned_reps),
        step=1.0,
        key_prefix=f"{key_prefix}_reps_{set_no}",
        unit="reps",
    )

    rpe = st.slider(
        "RPE",
        min_value=1,
        max_value=10,
        value=7,
        key=f"{key_prefix}_rpe_{set_no}",
        help="Rate of perceived exertion. 6-8 is usually enough for your current phase.",
    )

    notes = st.text_input(
        "Set notes",
        value="",
        key=f"{key_prefix}_notes_{set_no}",
        placeholder="Optional: form, difficulty, pain, etc.",
    )

    return {
        "set_index": set_no,
        "actual_sets": 1,
        "actual_reps": reps,
        "actual_weight": weight,
        "rpe": rpe,
        "completed": done,
        "notes": notes,
    }


def cardio_row_card(exercise_name: str, planned_duration: float, key_prefix: str) -> Dict:
    done = st.checkbox(
        f"Completed {exercise_name}",
        value=False,
        key=f"{key_prefix}_completed_cardio",
        help="Tick this when the cardio block is completed.",
    )

    duration = dual_value_input(
        "Duration",
        min_value=0.0,
        max_value=90.0,
        default_value=float(planned_duration),
        step=1.0,
        key_prefix=f"{key_prefix}_duration",
        unit="min",
    )

    avg_hr = dual_value_input(
        "Average HR",
        min_value=80.0,
        max_value=190.0,
        default_value=130.0,
        step=1.0,
        key_prefix=f"{key_prefix}_hr",
        unit="bpm",
    )

    rpe = st.slider("RPE", 1, 10, 5, key=f"{key_prefix}_rpe_cardio")
    notes = st.text_input("Notes", value="", key=f"{key_prefix}_notes_cardio")

    return {
        "set_index": 1,
        "actual_sets": 0,
        "actual_reps": duration,
        "actual_weight": avg_hr,
        "rpe": rpe,
        "completed": done,
        "notes": notes,
    }


def exercise_input_cards(plan_df: pd.DataFrame, log_date: date) -> pd.DataFrame:
    rows = []
    if plan_df.empty:
        return pd.DataFrame()

    for i, row in plan_df.iterrows():
        exercise_name = str(row["exercise_name"])
        section = str(row["section"])
        planned_sets = int(float(row.get("sets", 0) or 0))
        planned_reps_text = str(row.get("reps", "10"))
        planned_reps_value = parse_default_reps(planned_reps_text)
        planned_weight = float(row.get("target_weight", 0) or 0)

        with st.expander(f"{section} · {exercise_name}", expanded=i < 2):
            st.caption(str(row.get("note", "")))

            if planned_sets <= 0:
                planned_duration = float(row.get("duration_min", 20) or 20)
                actual = cardio_row_card(
                    exercise_name=exercise_name,
                    planned_duration=planned_duration,
                    key_prefix=f"log_{safe_key(exercise_name)}_{i}",
                )

                rows.append(
                    {
                        "date": str(log_date),
                        "session_name": row["session_name"],
                        "exercise_name": exercise_name,
                        "section": section,
                        "set_index": actual["set_index"],
                        "planned_sets": 0,
                        "planned_reps": planned_reps_text,
                        "planned_weight": 0,
                        "actual_sets": actual["actual_sets"],
                        "actual_reps": actual["actual_reps"],
                        "actual_weight": actual["actual_weight"],
                        "rpe": actual["rpe"],
                        "completed": actual["completed"],
                        "notes": actual["notes"],
                    }
                )

            else:
                st.caption(
                    f"Planned: {planned_sets} sets × {planned_reps_text} reps · "
                    f"{planned_weight:g} kg · RPE {row.get('rpe_range', '6-8')}"
                )

                for set_no in range(1, planned_sets + 1):
                    actual = set_row_card(
                        exercise_name=exercise_name,
                        set_no=set_no,
                        planned_weight=planned_weight,
                        planned_reps=planned_reps_value,
                        key_prefix=f"log_{safe_key(exercise_name)}_{i}",
                    )

                    rows.append(
                        {
                            "date": str(log_date),
                            "session_name": row["session_name"],
                            "exercise_name": exercise_name,
                            "section": section,
                            "set_index": actual["set_index"],
                            "planned_sets": planned_sets,
                            "planned_reps": planned_reps_text,
                            "planned_weight": planned_weight,
                            "actual_sets": actual["actual_sets"],
                            "actual_reps": actual["actual_reps"],
                            "actual_weight": actual["actual_weight"],
                            "rpe": actual["rpe"],
                            "completed": actual["completed"],
                            "notes": actual["notes"],
                        }
                    )

    return pd.DataFrame(rows)


def training_planner_page() -> None:
    hero("Training Planner", "Programme baseline + daily readiness adjustment, based on your previous 12-week training record.")

    ex_df = load_exercise_library()

    mode = st.radio(
        "Training module",
        ["Daily Planner", "12-week Programme", "Exercise Library"],
        horizontal=True,
        key="training_module_mode",
    )

    if mode == "Daily Planner":
        left, middle, right = st.columns([1.05, 1.35, 0.9], gap="large")

        with left:
            st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
            panel_header("Step 1", "Readiness Inputs", "The programme gives direction; readiness decides today's execution.")
            goal = st.selectbox("Goal", ["Strength Rebuild", "Fat Loss + Conditioning", "Recovery", "Balanced"], index=0)
            preferred_focus = st.selectbox("Preferred session", ["Auto", "Full Body A", "Full Body B", "Lower + Core", "Upper + Conditioning", "Recovery Cardio"], index=0)
            available_min = st.slider("Available time", 25, 75, 50, step=5)
            yesterday = st.selectbox("Yesterday", ["Rest", "5 km Run", "Incline Walk", "Elliptical", "Strength Training", "Table Tennis"], index=0)
            knee = st.slider("Knee discomfort", 0, 10, 0)
            ankle = st.slider("Ankle discomfort", 0, 10, 0)
            fatigue = st.slider("Fatigue", 0, 10, 3)

            if st.button("Generate Training Session", type="primary", use_container_width=True):
                title, session_df, reason = build_training_session(
                    ex_df=ex_df,
                    goal=goal,
                    preferred_focus=preferred_focus,
                    available_min=available_min,
                    knee=knee,
                    ankle=ankle,
                    fatigue=fatigue,
                )
                st.session_state["active_training_title"] = title
                st.session_state["active_training_plan"] = session_df
                st.session_state["active_training_reason"] = reason
                st.session_state["training_plan_generated_animation"] = True

            st.markdown("</div>", unsafe_allow_html=True)

        session_df = st.session_state.get("active_training_plan", pd.DataFrame())
        title = st.session_state.get("active_training_title", "")
        reason = st.session_state.get("active_training_reason", "")

        if st.session_state.pop("training_plan_generated_animation", False):
            animated_success("Training session generated. Exercises are ready.")

        with middle:
            st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
            panel_header("Step 2", "Generated Session", "A practical gym session using exercises you already know.")
            if session_df.empty:
                st.info("Enter readiness inputs, then generate a session.")
            else:
                st.subheader(title)
                st.caption(reason)
                training_plan_card(session_df)
                with st.expander("Detailed session table"):
                    st.dataframe(
                        session_df[["section", "exercise_name", "sets", "reps", "target_weight", "rest_sec", "rpe_range"]],
                        use_container_width=True,
                        hide_index=True,
                    )
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
            panel_header("Step 3", "Session Summary", "Save the generated session to use it in Workout Log.")
            if session_df.empty:
                result_card("Session", "—", "Generate first")
                result_card("Intensity", "—", "Generate first")
                result_card("Joint Stress", "—", "Generate first")
            else:
                duration_est = int(available_min)
                highest_joint = "Moderate" if session_df["joint_stress"].astype(str).str.contains("Moderate", case=False).any() else "Low"
                result_card("Session", str(session_df["session_name"].iloc[0]), "Current plan")
                result_card("Exercises", f"{len(session_df)}", "Including warm-up/cardio")
                result_card("Duration", f"{duration_est} min", "Estimated")
                training_status_badges("RPE 6-8", highest_joint, duration_est)
                if st.button("Use this plan in Workout Log", use_container_width=True):
                    save_latest_training_plan(session_df)
                    animated_success("Training plan saved. Open Workout Log to record actual performance.")
            st.markdown("</div>", unsafe_allow_html=True)

    elif mode == "12-week Programme":
        left, right = st.columns([1, 1], gap="large")
        with left:
            st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
            panel_header("Programme", "12-week Fat Loss + Strength Rebuild", "Baseline structure inspired by your previous personal training programme.")
            st.dataframe(programme_overview_df(), use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
            panel_header("Weekly Template", "Programme + Daily Adjustment", "This is the weekly plan. Daily Planner modifies it when pain or fatigue is high.")
            st.dataframe(weekly_template_df(), use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

    elif mode == "Exercise Library":
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        panel_header("Library", "Exercise Library", "Selected exercises are from your uploaded 12-week training record; recommended exercises support fat loss and joint-friendly training.")

        source_filter = st.radio("Source", ["All", "Selected", "Recommended"], horizontal=True)
        view = ex_df.copy()
        if source_filter == "Selected":
            view = view[view["selected"] == True]
        elif source_filter == "Recommended":
            view = view[view["source"] == "Recommended"]

        pattern_filter = st.multiselect("Movement pattern", sorted(view["pattern"].dropna().unique().tolist()))
        if pattern_filter:
            view = view[view["pattern"].isin(pattern_filter)]

        st.dataframe(
            view[[
                "exercise_name", "source", "selected", "pattern", "primary_muscle",
                "equipment", "joint_stress", "default_sets", "default_reps",
                "default_weight", "rpe_range", "cues"
            ]],
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def workout_log_page() -> None:
    hero("Workout Log", "Date-indexed actual training record. Use the latest generated training plan as default.")

    latest = load_latest_training_plan()

    left, middle, right = st.columns([1.0, 1.45, 0.85], gap="large")

    with left:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        panel_header("Step 1", "Workout Date", "Choose the actual training date.")
        log_date = st.date_input("Workout date", date.today())
        use_latest = False
        if not latest.empty:
            use_latest = st.checkbox("Use latest generated training plan", value=True)
            st.caption(f"Latest plan: {latest['session_name'].iloc[0]}")
        else:
            st.info("No latest training plan. Generate one in Training Planner first.")
        session_name = st.text_input("Session name", value=latest["session_name"].iloc[0] if use_latest and not latest.empty else "Manual Workout")
        st.markdown("</div>", unsafe_allow_html=True)

    detail_df = pd.DataFrame()

    with middle:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        panel_header("Step 2", "Exercise Log", "Each planned set becomes one row with a checkbox, weight slider and reps slider.")
        if use_latest and not latest.empty:
            detail_df = exercise_input_cards(latest, log_date)
        else:
            st.info("Manual logging is available in the summary panel for now. Generate a plan first for detailed exercise cards.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        panel_header("Step 3", "Workout Summary", "Save a summary and detailed exercise rows.")

        duration = st.number_input("Duration (min)", min_value=0.0, max_value=300.0, value=50.0, step=1.0)
        active_kcal = st.number_input("Active kcal", min_value=0, max_value=2000, value=300, step=10)
        avg_hr = st.number_input("Avg HR", min_value=0, max_value=220, value=135, step=1)
        knee_after = st.slider("Knee after", 0, 10, 0)
        ankle_after = st.slider("Ankle after", 0, 10, 0)
        rpe_session = st.slider("Session RPE", 1, 10, 6)
        notes = st.text_area("Session notes")

        if st.button("Save Workout", type="primary", use_container_width=True):
            append_csv(
                WORKOUT_LOG_PATH,
                [
                    {
                        "date": str(log_date),
                        "type": session_name,
                        "duration_min": duration,
                        "distance_km": 0,
                        "avg_hr": avg_hr,
                        "active_kcal": active_kcal,
                        "knee_pain": knee_after,
                        "ankle_pain": ankle_after,
                        "rpe": rpe_session,
                        "notes": notes,
                    }
                ],
            )
            if not detail_df.empty:
                detail_rows = detail_df.to_dict("records")
                append_csv(WORKOUT_DETAIL_LOG_PATH, detail_rows)
                completed_sets = int(detail_df["completed"].sum()) if "completed" in detail_df.columns else 0
                total_rows = len(detail_df)
                animated_success(f"Workout saved for {log_date}. Completed {completed_sets}/{total_rows} logged rows.")
            else:
                animated_success(f"Workout saved for {log_date}.")
        st.markdown("</div>", unsafe_allow_html=True)


def progress_page() -> None:
    hero("Progress", "Weight trend, workout calories and nutrition consistency.")

    body = load_csv(BODY_LOG_PATH)
    workouts = load_csv(WORKOUT_LOG_PATH)
    workout_details = load_csv(WORKOUT_DETAIL_LOG_PATH)
    food = load_csv(FOOD_LOG_PATH)

    with st.expander("Add body metrics", expanded=True):
        with st.form("body_form"):
            d = st.date_input("Date", date.today())
            morning = st.number_input("Morning weight (kg)", min_value=40.0, max_value=120.0, value=74.9, step=0.1)
            evening = st.number_input("Evening weight (kg)", min_value=40.0, max_value=120.0, value=75.5, step=0.1)
            waist = st.number_input("Waist (cm, optional)", min_value=0.0, max_value=150.0, value=0.0, step=0.5)
            stool = st.selectbox("Stool status", ["Formed", "Soft", "Mushy", "Watery", "Constipated"])
            notes = st.text_area("Notes")
            if st.form_submit_button("Save Body Metrics"):
                append_csv(
                    BODY_LOG_PATH,
                    [
                        {
                            "date": str(d),
                            "morning_weight": morning,
                            "evening_weight": evening,
                            "waist_cm": waist if waist > 0 else None,
                            "stool_status": stool,
                            "notes": notes,
                        }
                    ],
                )
                st.success("Saved.")

    if not body.empty:
        body["date"] = pd.to_datetime(body["date"])
        body = body.sort_values("date")
        body["7-day avg"] = body["morning_weight"].rolling(7, min_periods=1).mean()
        fig = px.line(body, x="date", y=["morning_weight", "7-day avg"], markers=True, title="Weight Trend")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No body records yet.")

    if not workouts.empty:
        workouts["date"] = pd.to_datetime(workouts["date"])
        fig2 = px.bar(workouts, x="date", y="active_kcal", color="type", title="Workout Active Calories")
        st.plotly_chart(fig2, use_container_width=True)

    if not workout_details.empty:
        st.subheader("Recent Detailed Exercise Logs")
        st.dataframe(workout_details.tail(30), use_container_width=True, hide_index=True)

    if not food.empty:
        daily = food.groupby("date", as_index=False)[["kcal", "protein", "fiber"]].sum()
        fig3 = px.line(daily, x="date", y=["kcal", "protein", "fiber"], markers=True, title="Nutrition Trend")
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Diet Log")
        st.dataframe(food.tail(30), use_container_width=True, hide_index=True)


def settings_page(food_db: pd.DataFrame) -> None:
    hero("Settings", "Food database, logs and old spreadsheet import.")

    st.subheader("Food Database")
    st.caption("The database uses English names for the UI.")
    st.dataframe(food_db.drop(columns=["display"]), use_container_width=True, hide_index=True)

    uploaded = st.file_uploader("Upload a new food_database.csv", type=["csv"])
    if uploaded is not None:
        new_df = pd.read_csv(uploaded)
        required = {
            "food_name",
            "category",
            "unit",
            "kcal_per_100g",
            "protein_per_100g",
            "carbs_per_100g",
            "fat_per_100g",
            "fiber_per_100g",
        }
        if required.issubset(set(new_df.columns)):
            new_df.to_csv(FOOD_DB_PATH, index=False)
            st.cache_data.clear()
            st.success("Food database updated. Refresh the app.")
        else:
            st.error(f"Missing columns: {required - set(new_df.columns)}")

    st.subheader("Import old training spreadsheet")
    old = st.file_uploader("Upload Exercise Tracking.xlsx", type=["xlsx"])
    if old is not None:
        sheets = pd.read_excel(old, sheet_name=None)
        st.write("Sheets:", list(sheets.keys()))
        for name, df in sheets.items():
            st.markdown(f"**{name}**")
            st.dataframe(df.head(12), use_container_width=True)

    st.subheader("Raw Logs")
    st.dataframe(load_csv(FOOD_LOG_PATH), use_container_width=True, hide_index=True)
    st.dataframe(load_csv(WORKOUT_LOG_PATH), use_container_width=True, hide_index=True)
    st.dataframe(load_csv(WORKOUT_DETAIL_LOG_PATH), use_container_width=True, hide_index=True)
    st.dataframe(load_exercise_library(), use_container_width=True, hide_index=True)
    st.dataframe(load_latest_training_plan(), use_container_width=True, hide_index=True)
    st.dataframe(load_csv(BODY_LOG_PATH), use_container_width=True, hide_index=True)
    st.dataframe(load_latest_plan(), use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Fitness OS", page_icon="🏋️", layout="wide")
    ensure_files()
    inject_css()
    food_db = load_food_db()

    page = get_page()

    if page == "Meal Planner":
        meal_planner_page(food_db)
    elif page == "Diet Log":
        diet_log_page(food_db)
    elif page == "Training Planner":
        training_planner_page()
    elif page == "Workout Log":
        workout_log_page()
    elif page == "Progress":
        progress_page()
    elif page == "Settings":
        settings_page(food_db)

    bottom_nav(page)


if __name__ == "__main__":
    main()
