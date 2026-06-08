from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
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
    "protein": (100, 280),
    "carb": (80, 200),
    "vegetable": (50, 180),
    "fruit": (80, 200),
    "dairy": (100, 350),
    "supplement": (20, 35),
    "seasoning": (1, 15),
    "seed": (5, 12),
}


def ensure_files() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    for path, cols in [
        (FOOD_LOG_PATH, ["date", "meal", "food_name", "weight_g", "kcal", "protein", "carbs", "fat", "fiber"]),
        (WORKOUT_LOG_PATH, ["date", "type", "duration_min", "distance_km", "avg_hr", "active_kcal", "knee_pain", "ankle_pain", "rpe", "notes"]),
        (BODY_LOG_PATH, ["date", "morning_weight", "evening_weight", "waist_cm", "stool_status", "notes"]),
    ]:
        if not path.exists():
            pd.DataFrame(columns=cols).to_csv(path, index=False)


@st.cache_data
def load_food_db() -> pd.DataFrame:
    df = pd.read_csv(FOOD_DB_PATH)
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


def generate_meal(food_db: pd.DataFrame, selected_foods: List[str], meal_type: str) -> pd.DataFrame:
    if not selected_foods:
        return pd.DataFrame()
    selected = food_db[food_db["food_name"].isin(selected_foods)].copy()

    weights: Dict[str, float] = {}
    for _, row in selected.iterrows():
        weights[row["food_name"]] = CATEGORY_DEFAULT_GRAMS.get(row["category"], 100)

    target = MEAL_TARGETS[meal_type]

    def build() -> pd.DataFrame:
        return pd.DataFrame([calc_row(row, weights[row["food_name"]]) for _, row in selected.iterrows()])

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

    m = build()
    totals = meal_totals(m)
    if totals["fiber"] > target["fiber"] * 1.4:
        for _, row in selected[selected["category"] == "vegetable"].iterrows():
            lo, hi = CATEGORY_LIMITS["vegetable"]
            weights[row["food_name"]] = max(lo, weights[row["food_name"]] - 30)

    return build().sort_values(["category", "food_name"])


def training_recommendation(yesterday_type: str, avg_hr: int, knee_pain: int, ankle_pain: int, fatigue: int, goal: str) -> Tuple[str, List[str]]:
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
        :root { --card-bg: #ffffff; --card-border: #e8edf3; --muted: #667085; --accent: #2e7df6; }
        .block-container { padding-top: 1.0rem; padding-bottom: 5rem; max-width: 920px; }
        [data-testid="stSidebar"] { display: none; }
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
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
            color: white;
            border-radius: 24px;
            padding: 22px 20px;
            margin-bottom: 16px;
            box-shadow: 0 12px 36px rgba(29, 78, 216, 0.25);
        }
        .hero-card h1 { margin: 0; font-size: 2.0rem; }
        .hero-card p { margin: 8px 0 0 0; color: rgba(255,255,255,0.82); }
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
        div[role="radiogroup"] { gap: 0.35rem; flex-wrap: wrap; }
        div[role="radiogroup"] label {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 999px;
            padding: 8px 12px;
        }
        .stButton button, .stDownloadButton button {
            border-radius: 999px;
            min-height: 44px;
            font-weight: 700;
        }
        @media (max-width: 640px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; }
            .hero-card h1 { font-size: 1.65rem; }
            div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
            div[data-testid="stDataFrame"] { font-size: 0.78rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(f"""
    <div class="hero-card">
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def card(title: str, text: str) -> None:
    st.markdown(f"""
    <div class="mobile-card">
      <strong>{title}</strong><br>
      <span style="color:#667085;">{text}</span>
    </div>
    """, unsafe_allow_html=True)


def today_page(food_db: pd.DataFrame) -> None:
    hero("Fitness OS", "Today-first food, training and recovery planning.")

    body = load_csv(BODY_LOG_PATH)
    food = load_csv(FOOD_LOG_PATH)
    workouts = load_csv(WORKOUT_LOG_PATH)
    today = str(date.today())

    today_food = food[food["date"] == today] if not food.empty else pd.DataFrame()
    today_workouts = workouts[workouts["date"] == today] if not workouts.empty else pd.DataFrame()
    last_weight = None
    if not body.empty and body["morning_weight"].notna().any():
        last_weight = body["morning_weight"].dropna().iloc[-1]

    c1, c2 = st.columns(2)
    c1.metric("Weight", f"{last_weight:.1f} kg" if last_weight else "—")
    c2.metric("Training", f"{today_workouts['duration_min'].sum():.0f} min" if not today_workouts.empty else "0 min")
    c3, c4 = st.columns(2)
    kcal = today_food["kcal"].sum() if not today_food.empty else 0
    protein = today_food["protein"].sum() if not today_food.empty else 0
    c3.metric("Calories", f"{kcal:.0f} / {DAILY_TARGETS['kcal_max']} kcal")
    c4.metric("Protein", f"{protein:.0f} / {DAILY_TARGETS['protein_min']} g")

    st.subheader("Quick Plan")
    title, plan = training_recommendation("None", 135, 0, 0, 3, "Fat-loss Cardio")
    card("Default training suggestion", f"{title}: {plan[0]}")
    card("Food focus", "Protein 120-140g/day. Keep fiber around 25-35g/day until stool is formed again.")

    st.subheader("Fast Meal Generator")
    common = [x for x in ["Cooked Mixed Brown Rice", "Beef Tripe", "Lettuce", "Celery", "Enoki Mushrooms"] if x in food_db["food_name"].tolist()]
    selected = st.multiselect("Choose ingredients", food_db["food_name"].tolist(), default=common)
    if st.button("Generate Lunch Plan"):
        generated = generate_meal(food_db, selected, "Lunch")
        st.session_state["last_generated_meal"] = generated
    generated = st.session_state.get("last_generated_meal", pd.DataFrame())
    if not generated.empty:
        totals = meal_totals(generated)
        c1, c2, c3 = st.columns(3)
        c1.metric("Meal kcal", f"{totals['kcal']:.0f}")
        c2.metric("Protein", f"{totals['protein']:.1f}g")
        c3.metric("Fiber", f"{totals['fiber']:.1f}g")
        st.dataframe(generated[["food_name", "weight_g", "kcal", "protein", "fiber"]], use_container_width=True, hide_index=True)


def meal_page(food_db: pd.DataFrame) -> None:
    hero("Meal Builder", "Choose ingredients first. Fitness OS suggests reasonable weights and nutrition.")
    meal_type = st.segmented_control("Meal", list(MEAL_TARGETS.keys()), default="Lunch")
    selected = st.multiselect(
        "Ingredients",
        options=food_db["food_name"].tolist(),
        default=[x for x in ["Cooked Mixed Brown Rice", "Beef Tripe", "Lettuce", "Celery"] if x in food_db["food_name"].tolist()],
    )
    generated = generate_meal(food_db, selected, meal_type)
    if generated.empty:
        st.info("Select at least one ingredient.")
        return

    totals = meal_totals(generated)
    c1, c2, c3 = st.columns(3)
    c1.metric("Calories", f"{totals['kcal']:.0f} kcal")
    c2.metric("Protein", f"{totals['protein']:.1f} g")
    c3.metric("Fiber", f"{totals['fiber']:.1f} g")

    if totals["fiber"] > MEAL_TARGETS[meal_type]["fiber"] * 1.4:
        st.warning("Fiber is high. If stool is watery, reduce raw vegetables, apples or chia seeds for a few days.")
    if totals["protein"] < MEAL_TARGETS[meal_type]["protein"] * 0.8:
        st.warning("Protein is low. Add beef tripe, beef omasum, mackerel, mussels, prawns or whey.")

    st.subheader("Suggested weights")
    edited = st.data_editor(
        generated[["food_name", "category", "weight_g", "kcal", "protein", "carbs", "fat", "fiber"]],
        num_rows="fixed",
        use_container_width=True,
        hide_index=True,
    )
    totals2 = meal_totals(edited)
    st.caption(f"Actual totals after editing: {totals2['kcal']:.0f} kcal · {totals2['protein']:.1f}g protein · {totals2['fiber']:.1f}g fiber")

    if st.button("Save meal to Food Log", type="primary"):
        rows = []
        for _, row in edited.iterrows():
            rows.append({
                "date": str(date.today()),
                "meal": meal_type,
                "food_name": row["food_name"],
                "weight_g": row["weight_g"],
                "kcal": row["kcal"],
                "protein": row["protein"],
                "carbs": row["carbs"],
                "fat": row["fat"],
                "fiber": row["fiber"],
            })
        append_csv(FOOD_LOG_PATH, rows)
        st.success("Saved to Food Log.")


def training_page() -> None:
    hero("Training Planner", "Choose today's session based on soreness, fatigue and yesterday's load.")
    with st.form("training_planner_form"):
        y_type = st.selectbox("Yesterday's main workout", ["None", "5 km Run", "Treadmill Run", "Incline Walk", "Elliptical", "Strength Training", "Table Tennis"])
        avg_hr = st.slider("Yesterday average heart rate", 80, 180, 135)
        knee = st.slider("Knee discomfort today", 0, 10, 0)
        ankle = st.slider("Ankle discomfort today", 0, 10, 0)
        fatigue = st.slider("Overall fatigue", 0, 10, 3)
        goal = st.selectbox("Today's goal", ["Fat-loss Cardio", "Recovery Cardio", "Strength Training", "Balanced"])
        submit = st.form_submit_button("Generate Training Plan", type="primary")
    if submit:
        title, plan = training_recommendation(y_type, avg_hr, knee, ankle, fatigue, goal)
        st.subheader(title)
        for item in plan:
            st.markdown(f"<span class='pill'>{item}</span>", unsafe_allow_html=True)

    st.subheader("Save Workout")
    with st.form("workout_log_form"):
        d = st.date_input("Date", date.today())
        t = st.selectbox("Workout type", ["Incline Walk", "5 km Run", "Elliptical", "Strength Training", "Table Tennis", "Other"])
        duration = st.number_input("Duration (min)", min_value=0.0, max_value=300.0, value=40.0, step=1.0)
        distance = st.number_input("Distance (km)", min_value=0.0, max_value=50.0, value=0.0, step=0.1)
        hr = st.number_input("Average heart rate", min_value=0, max_value=220, value=135, step=1)
        kcal = st.number_input("Apple Watch active kcal", min_value=0, max_value=2000, value=300, step=10)
        knee_log = st.slider("Knee discomfort after workout", 0, 10, 0)
        ankle_log = st.slider("Ankle discomfort after workout", 0, 10, 0)
        rpe = st.slider("RPE", 1, 10, 5)
        notes = st.text_area("Notes")
        if st.form_submit_button("Save Workout"):
            append_csv(WORKOUT_LOG_PATH, [{
                "date": str(d), "type": t, "duration_min": duration, "distance_km": distance,
                "avg_hr": hr, "active_kcal": kcal, "knee_pain": knee_log, "ankle_pain": ankle_log,
                "rpe": rpe, "notes": notes,
            }])
            st.success("Workout saved.")


def progress_page() -> None:
    hero("Progress", "Weight trend, workout calories and nutrition consistency.")
    body = load_csv(BODY_LOG_PATH)
    workouts = load_csv(WORKOUT_LOG_PATH)
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
                append_csv(BODY_LOG_PATH, [{
                    "date": str(d), "morning_weight": morning, "evening_weight": evening,
                    "waist_cm": waist if waist > 0 else None, "stool_status": stool, "notes": notes,
                }])
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

    if not food.empty:
        daily = food.groupby("date", as_index=False)[["kcal", "protein", "fiber"]].sum()
        fig3 = px.line(daily, x="date", y=["kcal", "protein", "fiber"], markers=True, title="Nutrition Trend")
        st.plotly_chart(fig3, use_container_width=True)


def settings_page(food_db: pd.DataFrame) -> None:
    hero("Settings", "Food database, logs and old spreadsheet import.")
    st.subheader("Food Database")
    st.caption("The database uses English names for the UI. Chinese names are kept internally for reference.")
    st.dataframe(food_db.drop(columns=["display"]), use_container_width=True, hide_index=True)

    uploaded = st.file_uploader("Upload a new food_database.csv", type=["csv"])
    if uploaded is not None:
        new_df = pd.read_csv(uploaded)
        required = {"food_name", "category", "unit", "kcal_per_100g", "protein_per_100g", "carbs_per_100g", "fat_per_100g", "fiber_per_100g"}
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
    st.dataframe(load_csv(BODY_LOG_PATH), use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Fitness OS", page_icon="🏋️", layout="wide")
    ensure_files()
    inject_css()
    food_db = load_food_db()

    page = st.radio(
        "Navigate",
        ["🏠 Today", "🍽 Meal", "🏋 Training", "📈 Progress", "⚙ Settings"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if page == "🏠 Today":
        today_page(food_db)
    elif page == "🍽 Meal":
        meal_page(food_db)
    elif page == "🏋 Training":
        training_page()
    elif page == "📈 Progress":
        progress_page()
    elif page == "⚙ Settings":
        settings_page(food_db)


if __name__ == "__main__":
    main()
