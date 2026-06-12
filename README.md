# Fitness OS

Fitness OS is a personal food, training and recovery planning app built with Streamlit.

The app is designed for daily practical use rather than perfect laboratory-level precision. The main goal is to help me plan meals, log actual food intake, generate training sessions, record workouts, and track progress with a workflow that is easy enough to use consistently.

---

## 1. Core Design Philosophy

Fitness OS follows three principles:

1. **Plan and log are separate**
   - A planner is used to generate a reasonable plan.
   - A log is used to record what actually happened on a specific date.

2. **Practical accuracy is better than unrealistic precision**
   - High-impact foods such as rice, meat, milk, oats and whey can be logged in grams.
   - Low-calorie vegetables and fruits can be logged by practical portions.
   - Seasoning and oil are hidden from the normal workflow unless needed.

3. **Programme gives direction, daily readiness decides execution**
   - Training can follow a 12-week programme structure.
   - Daily training plans can be adjusted based on knee discomfort, ankle discomfort, fatigue and available time.

---

## 2. Main Pages

The app currently contains six main pages:

| Page | Purpose |
|---|---|
| Meal Planner | Generate a meal plan without binding it to a date |
| Diet Log | Record actual food intake for a selected date |
| Training Planner | Generate a training session based on goal and readiness |
| Workout Log | Record actual workout details, either from a generated plan or manually |
| Progress | Review food, body and workout history |
| Settings | View raw logs and internal data |

---

# Meal Planner

## Purpose

Meal Planner is used to generate a reasonable meal plan before cooking or eating. It is not date-indexed.

Typical use case:

> I want to prepare tomorrow's lunch. I choose the ingredients today, generate a meal plan, and then use that plan later in Diet Log.

## Workflow

1. Choose meal type:
   - Breakfast
   - Lunch
   - Dinner
   - Snack

2. Select main ingredients from the food library.

3. Click **Generate Meal Plan**.

4. The app suggests reasonable weights or portions.

5. Review nutrition:
   - Calories
   - Protein
   - Fiber
   - Carbs / Fat

6. Save the generated plan for Diet Log.

## Important Logic

The generated meal plan is designed to be reasonable by default. It should not show calorie warnings immediately after automatic generation.

Calorie warnings are mainly for cases where the user manually changes the amount of food.

---

# Diet Log

## Purpose

Diet Log is used to record actual food intake for a selected date.

This is different from Meal Planner:

| Meal Planner | Diet Log |
|---|---|
| Generate a plan | Record actual intake |
| Not date-indexed | Date-indexed |
| Used before cooking | Used during or after eating |
| Suggests weights | Records actual portions or grams |

## Practical Portion Mode

For low-friction daily logging, some foods support practical portion input.

Examples:

### Celery

| Portion | Approximate grams |
|---|---:|
| 1/4 Lidl pack | 100 g |
| 1/2 Lidl pack | 200 g |
| 1 Lidl pack | 400 g |

### Lettuce

| Portion | Approximate grams |
|---|---:|
| 1/2 head | 90 g |
| 1 head | 180 g |
| 2 heads | 360 g |

### Enoki Mushrooms

| Portion | Approximate grams |
|---|---:|
| 1/2 pack | 75 g |
| 1 pack | 150 g |
| 2 packs | 300 g |

### Fruits

Banana, apple, blueberries and strawberries also support practical portion choices such as small, medium, large, handful or bowl.

## Grams Mode

For higher-impact foods, grams mode is still recommended:

- Cooked mixed brown rice
- Beef tripe
- Beef omasum
- Mackerel
- Oats
- Milk
- Whey protein
- Chia seeds
- Other calorie-dense foods

These foods have a larger impact on calories and protein, so more precise input is useful.

## Seasoning and Oil

Seasoning and oil are hidden by default.

The normal workflow should focus on main foods:

- Protein
- Carbs
- Vegetables
- Fruits
- Dairy
- Supplements

Seasoning and oil can be shown only when needed by enabling:

> Show optional seasoning/oil

This keeps the app easier to use every day.

### Recommended rule

- Do not record normal salt, pepper, chili, Sichuan pepper or basic seasoning in daily logs.
- Only record oil if it is important for that meal.
- For stir-fried foods such as eggplant, it is better to record:
  - Aubergine / Eggplant
  - Optional light oil, only if needed

---

# Training Planner

## Purpose

Training Planner generates a training session. It is not a workout log.

It follows the logic:

> 12-week programme gives the baseline, daily readiness adjusts the session.

## Goal Options

The goal dropdown currently includes four options.

| Goal | Main purpose | Typical session | Best used when |
|---|---|---|---|
| Strength Rebuild | Rebuild strength and preserve muscle | Full body strength session | Normal energy, no major joint discomfort |
| Fat Loss + Conditioning | Increase calorie burn and conditioning | Strength + low-impact cardio | Want more energy expenditure |
| Recovery | Reduce stress and support recovery | Zone 2 cardio, light movement | Knee/ankle discomfort or high fatigue |
| Balanced | General all-round session | Moderate full body session | Not sure what to choose |

## Readiness Inputs

The planner can use:

- Yesterday's workout
- Available time
- Knee discomfort
- Ankle discomfort
- Fatigue
- Preferred session

These inputs help the app decide whether to keep the original training direction or reduce intensity.

## Example

If the selected goal is **Strength Rebuild** and readiness is good, the app may generate:

- Warm-up: Incline walk
- Strength: Leg press
- Strength: Lat pulldown
- Strength: Incline dumbbell bench press
- Strength: Dumbbell incline row
- Accessory: Hamstring curl
- Core: Dead bug
- Conditioning: Elliptical Zone 2

If knee or ankle discomfort is high, the app may modify the plan toward:

- Upper body strength
- Low-impact cardio
- Recovery work

---

# 12-week Programme

The app includes a baseline 12-week structure inspired by my previous personal training programme.

## Phase Structure

| Phase | Focus | Weekly structure | Progression rule |
|---|---|---|---|
| Weeks 1-4 | Adaptation | 3 strength + 2 low-impact cardio | RPE 6-7, rebuild movement skill |
| Weeks 5-8 | Progression | 3 strength + 2-3 cardio | Add small load or reps when form is good |
| Weeks 9-12 | Consolidation | 3 strength + conditioning | Keep joints happy and improve consistency |

## Weekly Template

| Day | Session | Purpose |
|---|---|---|
| Day 1 | Full Body A | Strength + easy conditioning |
| Day 2 | Zone 2 Cardio | Incline walk / elliptical / bike |
| Day 3 | Full Body B | Strength rebuild |
| Day 4 | Recovery | Light cardio + mobility |
| Day 5 | Upper + Conditioning | Upper strength + low-impact cardio |
| Day 6 | Optional | Table tennis, easy walk, or rest |
| Day 7 | Rest | Recovery and meal prep |

---

# Exercise Library

## Purpose

The exercise library contains exercises that can be used in Training Planner and Workout Log.

The first version includes exercises from my previous 12-week personal training programme, because I am already familiar with them.

## Selected Exercises

Examples include:

- Lat Pulldown
- Kettlebell Squat
- Incline Dumbbell Bench Press
- Dumbbell Incline Row
- Prone Machine Hamstring Curl
- Leg Extension
- T-Bar Row
- Dumbbell Renegade Row
- Sit-Up
- Barbell Bicep Curl
- Cable Triceps Extension
- Assisted Dip
- Leg Press
- Incline Dumbbell Reverse Fly
- Hip Adductor Machine
- Hip Abductor Machine
- Barbell Hip Thrust
- Dumbbell Shoulder Press

## Recommended Exercises

The app also contains recommended exercises for fat loss, strength rebuild and joint-friendly conditioning:

- Incline Walk
- Elliptical Zone 2
- Bike Zone 2
- Dead Bug
- Pallof Press
- Face Pull

## Exercise Metadata

Each exercise can include:

- Exercise name
- Category
- Movement pattern
- Primary muscle
- Equipment
- Difficulty
- Joint stress
- Default sets
- Default reps
- Default weight
- Rest time
- RPE range
- Coaching cues
- Avoid-if notes

This makes the app more like a personal training system rather than a simple workout tracker.

---

# Workout Log

## Purpose

Workout Log records what actually happened during training.

It supports two modes:

| Mode | Use case |
|---|---|
| Latest generated plan | Use a session generated by Training Planner |
| Manual workout | Log a workout without generating a plan first |

---

## Logging a Generated Plan

When using a generated training plan, the app expands each planned exercise into actual logging cards.

For strength exercises, each set is logged separately.

Example:

> Lat Pulldown: 35 kg × 10 reps × 3 sets

The app creates:

- Set 1
- Set 2
- Set 3

Each set includes:

- Completed checkbox
- Weight slider + exact input
- Reps slider + exact input
- RPE
- Notes

This is useful during actual training because I can tick off sets as I finish them.

---

## Manual Workout Logging

Manual logging is useful when I go to the gym without generating a plan first.

Examples:

- Treadmill incline walk
- Indoor run
- Elliptical
- Bike
- Table tennis
- Traditional strength training
- Mixed cardio + strength

---

## Apple Watch-style Cardio Logging

For cardio sessions, the app follows Apple Watch / Apple Fitness fields:

- Workout Time
- Distance
- Active Kilocalories
- Total Kilocalories
- Average Pace
- Average Heart Rate
- Effort
- Optional splits

Example:

| Field | Example |
|---|---:|
| Workout Time | 45.3 min |
| Distance | 4.05 km |
| Active Kilocalories | 435 kcal |
| Total Kilocalories | 504 kcal |
| Avg Heart Rate | 136 bpm |
| Effort | 6 |

The app calculates average pace automatically.

---

## Apple Watch-style Strength Logging

For Traditional Strength Training, Apple Watch usually provides only summary-level information:

- Workout Time
- Active Kilocalories
- Total Kilocalories
- Avg Heart Rate
- Effort

Apple Watch does not record detailed strength sets, reps and weights.

Therefore, Fitness OS records strength training in two layers:

### Layer 1: Apple Watch summary

- Workout Time
- Active Kilocalories
- Total Kilocalories
- Avg Heart Rate
- Effort

### Layer 2: Gym details

- Exercise
- Set number
- Weight
- Reps
- RPE
- Completed checkbox
- Notes

This gives both Apple Watch compatibility and proper strength training records.

---

# Progress Page

The Progress page is used to review historical data.

It can show:

- Body weight history
- Workout active calories
- Recent detailed exercise logs
- Food logs
- Body logs

This page can be expanded later to include:

- Weekly training volume
- Strength progression by exercise
- Calories and protein trends
- Cardio duration trends
- Knee and ankle discomfort trends
- Body weight and waist trend

---

# Settings Page

The Settings page is mainly for checking raw data.

It can show:

- Food database
- Food log
- Workout summary log
- Detailed workout log
- Exercise library
- Latest meal plan
- Latest training plan
- Body log

This is useful for debugging and checking whether the app is saving data correctly.

---

# Data Files

The app stores data in the `data/` folder.

Important files include:

| File | Purpose |
|---|---|
| food_database.csv | Food database |
| food_log.csv | Date-indexed food log |
| latest_meal_plan.csv | Most recent generated meal plan |
| workout_log.csv | Workout summary log |
| workout_detail_log.csv | Set-level and exercise-level workout log |
| exercise_library.csv | Exercise library |
| latest_training_plan.csv | Most recent generated training plan |
| body_log.csv | Body weight and body status log |

---

# Current Workflow

## Meal Workflow

1. Open Meal Planner.
2. Select meal type.
3. Select main ingredients.
4. Generate meal plan.
5. Review nutrition.
6. Save plan to Diet Log.
7. Open Diet Log.
8. Select date.
9. Use latest generated meal plan.
10. Adjust portions or grams if needed.
11. Save meal.

## Training Workflow

1. Open Training Planner.
2. Select goal.
3. Enter readiness inputs.
4. Generate training session.
5. Save it to Workout Log.
6. Open Workout Log.
7. Use latest generated plan.
8. Complete each set and tick the checkbox.
9. Adjust weight, reps and RPE if needed.
10. Save workout.

## Manual Workout Workflow

1. Open Workout Log.
2. Select Manual workout.
3. Choose Cardio, Strength or Mixed.
4. Enter Apple Watch-style summary fields.
5. Add strength exercise details if needed.
6. Save workout.

---

# Current Design Choices

## Why not weigh everything?

Weighing every vegetable increases the cost of using the app. For long-term consistency, practical portion mode is better for low-calorie foods.

## Why hide seasoning and oil?

Seasoning is usually low-calorie and hard to measure. Oil is high-calorie but difficult to estimate precisely. To keep the workflow usable, oil and seasoning are hidden by default and only shown when needed.

## Why separate planner and log?

Planning and logging are different tasks.

A plan is what I intend to do.

A log is what I actually did.

Keeping them separate makes the app more realistic.

## Why include both programme and daily planner?

A programme provides long-term structure.

Daily readiness protects against overtraining and allows adjustment based on fatigue, knee discomfort or ankle discomfort.

---

# Known Limitations

This is still a personal MVP.

Current limitations:

- Portion gram values are approximate and should be refined over time.
- Food database values may need updates from real package labels.
- Exercise default weights may need calibration from actual training logs.
- The training recommendation engine is rule-based, not machine learning.
- The app does not yet sync directly with Apple Health or Apple Watch.
- The Progress page is still basic.
- Oil and seasoning estimation is intentionally simplified.

---

# Future Improvements

Potential next steps:

1. Add editable portion presets in the app UI.
2. Add weekly training volume charts.
3. Add strength progression by exercise.
4. Add protein and calorie weekly averages.
5. Add knee/ankle discomfort trend.
6. Add recovery recommendation after high-intensity days.
7. Add Apple Watch import manually from exported data.
8. Add photo-based food logging later if useful.
9. Add a proper 12-week programme calendar.
10. Add exercise demo links or personal cue notes.
11. Add a mobile-first iOS version later if needed.

---

# Version Notes

Current version represented by this README:

**Fitness OS v0.19 Practical Portion Mode**

Key updates in this version:

- Practical portion mode for celery, lettuce, enoki mushrooms and fruits.
- Seasoning and oil hidden from the normal workflow.
- Apple Watch-style cardio logging.
- Apple Watch-style strength summary logging.
- Set-by-set strength logging.
- Exercise library based on my previous 12-week programme.
- Blue unified UI theme.
