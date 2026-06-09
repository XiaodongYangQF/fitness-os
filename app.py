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
    "carb": (80, 220),
    "vegetable": (50, 180),
    "fruit": (80, 200),
    "dairy": (100, 350),
    "supplement": (20, 35),
    "seasoning": (1, 15),
    "seed": (5, 12),
}

PAGE_OPTIONS = ["Meal Planner", "Diet Log", "Training Planner", "Workout Log", "Progress", "Settings"]

MEAL_DEFAULT_FOODS = {
    "Breakfast": ["Low Fat Milk", "Oats", "Banana", "Blueberries", "Whey Protein"],
    "Lunch": ["Cooked Mixed Brown Rice", "Beef Tripe", "Lettuce", "Celery", "Enoki Mushrooms"],
    "Dinner": ["Mackerel", "Beef Omasum", "Lettuce", "Celery", "Enoki Mushrooms"],
    "Snack": ["Apple", "Banana"],
}

FOOD_GROUP_ORDER = [
    "Breakfast Staples",
    "Protein",
    "Carb",
    "Vegetable",
    "Fruit",
    "Dairy",
    "Supplement",
    "Seasoning",
    "Seed",
    "Other",
]

BREAKFAST_STAPLES = {
    "Low Fat Milk",
    "Oats",
    "Banana",
    "Blueberries",
    "Strawberries",
    "Whey Protein",
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
    df = df.copy()
    df["food_name"] = df["food_name"].astype(str)
    df["category"] = df["category"].astype(str).str.lower()
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
            lo, _ = CATEGORY_LIMITS["vegetable"]
            weights[row["food_name"]] = max(lo, weights[row["food_name"]] - 30)

    return build().sort_values(["category", "food_name"])


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


def food_group(food_name: str, category: str) -> str:
    if food_name in BREAKFAST_STAPLES:
        return "Breakfast Staples"
    category = str(category).lower()
    if category in {"protein", "carb", "vegetable", "fruit", "dairy", "supplement", "seasoning", "seed"}:
        return category.title()
    return "Other"


def build_food_groups(food_db: pd.DataFrame, meal_type: str) -> Dict[str, pd.DataFrame]:
    df = food_db.copy()
    df["group"] = [food_group(name, cat) for name, cat in zip(df["food_name"], df["category"])]

    groups: Dict[str, pd.DataFrame] = {}
    if meal_type == "Breakfast":
        order = ["Breakfast Staples", "Fruit", "Dairy", "Supplement", "Carb", "Seed", "Other"]
    else:
        order = ["Protein", "Carb", "Vegetable", "Seasoning", "Fruit", "Dairy", "Supplement", "Seed", "Other"]

    for group_name in order:
        g = df[df["group"] == group_name].sort_values("food_name")
        if not g.empty:
            groups[group_name] = g
    return groups


def food_picker_with_weights(
    food_db: pd.DataFrame,
    meal_type: str,
    default_selected: List[str],
    key_prefix: str,
) -> pd.DataFrame:
    """Select foods from visible groups and type weights directly."""
    default_selected_set = set(default_selected)
    suggested = generate_meal(food_db, default_selected, meal_type)
    suggested_weight = {
        row["food_name"]: float(row["weight_g"])
        for _, row in suggested.iterrows()
    } if not suggested.empty else {}

    st.caption("Select foods from the list below, then type the actual grams/ml from your kitchen scale.")

    weights: Dict[str, float] = {}
    groups = build_food_groups(food_db, meal_type)

    for group_name, group_df in groups.items():
        expanded = group_name in {"Breakfast Staples", "Protein", "Carb", "Vegetable"}
        with st.expander(group_name, expanded=expanded):
            for _, row in group_df.iterrows():
                food_name = row["food_name"]
                category = str(row["category"]).title()
                unit = str(row.get("unit", "g"))
                default_checked = food_name in default_selected_set

                c1, c2 = st.columns([1.2, 1.0])
                with c1:
                    checked = st.checkbox(
                        f"{food_name}",
                        value=default_checked,
                        key=f"{key_prefix}_check_{safe_key(meal_type)}_{safe_key(food_name)}",
                    )
                    st.caption(f"{category} · kcal {float(row['kcal_per_100g']):.0f}/100{unit}")

                with c2:
                    if checked:
                        default_weight = suggested_weight.get(
                            food_name,
                            CATEGORY_DEFAULT_GRAMS.get(str(row["category"]).lower(), 100),
                        )
                        weights[food_name] = st.number_input(
                            "Weight",
                            min_value=0.0,
                            max_value=1000.0,
                            value=float(default_weight),
                            step=5.0,
                            format="%.0f",
                            label_visibility="collapsed",
                            key=f"{key_prefix}_weight_{safe_key(meal_type)}_{safe_key(food_name)}",
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
            --card-border: #e8edf3;
            --muted: #667085;
            --accent: #2563eb;
            --dark: #0f172a;
        }

        .stApp { background: #ffffff; }

        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 6.5rem !important;
            max-width: 900px !important;
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
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
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

        /* Make food picker inputs more compact on phone */
        div[data-testid="stExpander"] {
            border-radius: 18px;
            border-color: #e8edf3;
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
    hero("Meal Planner", "Generate a meal plan independent of date. Use it before cooking tomorrow's lunch or dinner.")

    meal_type = st.radio("Meal type", list(MEAL_TARGETS.keys()), horizontal=True, index=1, key="planner_meal_type")

    st.subheader("Meal Templates")
    if meal_type == "Breakfast":
        meal_template_card(
            "Fixed Breakfast",
            ["Low Fat Milk 300ml", "Oats 45g", "Banana 120g", "Blueberries / Strawberries 80g", "Whey Protein 30g"],
            "≈ 520 kcal",
            "≈ 35g protein",
        )
    elif meal_type == "Lunch":
        meal_template_card(
            "Default Lunch",
            ["Cooked Mixed Brown Rice 150g", "Beef Tripe / Beef Omasum 180-220g", "Lettuce 100g", "Celery 120g", "Enoki Mushrooms 100g"],
            "≈ 550-650 kcal",
            "≈ 40-50g protein",
        )
    elif meal_type == "Dinner":
        meal_template_card(
            "Default Dinner",
            ["Mackerel / Mussels / Beef Omasum 180-220g", "Lettuce 100g", "Celery 100g", "Enoki Mushrooms 100g", "Rice 0-100g depending on hunger"],
            "≈ 450-650 kcal",
            "≈ 35-50g protein",
        )
    else:
        meal_template_card(
            "Snack",
            ["Apple 150-200g", "or Banana 100-120g", "Avoid stacking too much fruit if stool is watery."],
            "≈ 80-180 kcal",
            "Low protein",
        )

    st.subheader("Build Your Meal")
    default_selected = suggested_foods(food_db, MEAL_DEFAULT_FOODS[meal_type])
    edited = food_picker_with_weights(food_db, meal_type, default_selected, key_prefix="planner")

    if edited.empty:
        st.info("Select at least one food.")
        return

    totals = show_meal_summary(edited, meal_type)
    st.caption(
        f"Planner total: {totals['kcal']:.0f} kcal · "
        f"{totals['protein']:.1f}g protein · {totals['fiber']:.1f}g fiber"
    )


def diet_log_page(food_db: pd.DataFrame) -> None:
    hero("Diet Log", "Date-indexed actual food record. Use this when you cook or weigh food for a specific date.")

    log_date = st.date_input("Log date", value=date.today() + timedelta(days=1), help="For example, if you cook tomorrow's lunch today, choose tomorrow's date.")
    meal_type = st.radio("Meal", list(MEAL_TARGETS.keys()), horizontal=True, index=1, key="diet_log_meal_type")

    default_selected = suggested_foods(food_db, MEAL_DEFAULT_FOODS[meal_type])
    edited = food_picker_with_weights(food_db, meal_type, default_selected, key_prefix=f"diet_log_{log_date}")

    if edited.empty:
        st.info("Select at least one food.")
        return

    totals = show_meal_summary(edited, meal_type)
    st.caption(
        f"Selected date: {log_date} · {meal_type} · "
        f"{totals['kcal']:.0f} kcal · {totals['protein']:.1f}g protein"
    )

    if st.button("Save to Diet Log", type="primary"):
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
        st.success(f"Saved {meal_type} for {log_date}.")


def training_planner_page() -> None:
    hero("Training Planner", "Generate a training suggestion independent of date. Log the actual workout separately.")

    with st.form("training_planner_form"):
        y_type = st.selectbox(
            "Yesterday's main workout",
            ["None", "5 km Run", "Treadmill Run", "Incline Walk", "Elliptical", "Strength Training", "Table Tennis"],
        )
        avg_hr = st.slider("Yesterday average heart rate", 80, 180, 135)
        knee = st.slider("Knee discomfort today", 0, 10, 0)
        ankle = st.slider("Ankle discomfort today", 0, 10, 0)
        fatigue = st.slider("Overall fatigue", 0, 10, 3)
        goal = st.selectbox("Training goal", ["Fat-loss Cardio", "Recovery Cardio", "Strength Training", "Balanced"])
        submit = st.form_submit_button("Generate Training Plan", type="primary")

    if submit:
        title, plan = training_recommendation(y_type, avg_hr, knee, ankle, fatigue, goal)
        st.subheader(title)
        for item in plan:
            card("Plan item", item)


def workout_log_page() -> None:
    hero("Workout Log", "Date-indexed actual workout record from Apple Watch or gym notes.")

    with st.form("workout_log_form"):
        d = st.date_input("Workout date", date.today())
        t = st.selectbox("Workout type", ["Incline Walk", "5 km Run", "Elliptical", "Strength Training", "Table Tennis", "Other"])
        duration = st.number_input("Duration (min)", min_value=0.0, max_value=300.0, value=40.0, step=1.0)
        distance = st.number_input("Distance (km)", min_value=0.0, max_value=50.0, value=0.0, step=0.1)
        hr = st.number_input("Average heart rate", min_value=0, max_value=220, value=135, step=1)
        kcal = st.number_input("Apple Watch active kcal", min_value=0, max_value=2000, value=300, step=10)
        knee_log = st.slider("Knee discomfort after workout", 0, 10, 0)
        ankle_log = st.slider("Ankle discomfort after workout", 0, 10, 0)
        rpe = st.slider("RPE", 1, 10, 5)
        notes = st.text_area("Notes")

        if st.form_submit_button("Save Workout", type="primary"):
            append_csv(
                WORKOUT_LOG_PATH,
                [
                    {
                        "date": str(d),
                        "type": t,
                        "duration_min": duration,
                        "distance_km": distance,
                        "avg_hr": hr,
                        "active_kcal": kcal,
                        "knee_pain": knee_log,
                        "ankle_pain": ankle_log,
                        "rpe": rpe,
                        "notes": notes,
                    }
                ],
            )
            st.success(f"Workout saved for {d}.")


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
    st.dataframe(load_csv(BODY_LOG_PATH), use_container_width=True, hide_index=True)


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
