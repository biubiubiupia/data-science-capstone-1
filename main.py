import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, Legend, Range1d, LinearAxis, LabelSet

# Load CSV
df = pd.read_csv("mxmh_survey_results.csv")

# Assessing Data
# print(df.head())
# print(df.info())
# print(df.describe())
# print(df.isnull().sum())

# Data Cleaning
# From the codes above, we noticed that there are
# - 107 missing values from the BPM column
# - 8 missing from the Music Effects
# - a few missing from "While Working", "Instrumentalist", "Foreign languages", etc.
df_clean = df.dropna(
    subset=[
        "Age",
        "Primary streaming service",
        "While working",
        "Instrumentalist",
        "Foreign languages",
        "Music effects",
        "BPM",
    ]
)
df_clean = df_clean[df_clean["Age"].between(14, 90) & df_clean["BPM"].between(0, 200)]
# print(df_clean.describe())  # Returns 608 samples with all columns contain values
df_clean.to_csv("df_clean.csv", index=False)

# Understanding the Samples (608)
# for col in df_clean.select_dtypes(include="object").columns:
#     if col != "Timestamp":
#         print(f"\n--- {col} ---")
#         print(df_clean[col].value_counts(dropna=False))




# 📊 Mental Health Chart 

mental_health_cols = ["Anxiety", "Depression", "Insomnia", "OCD"]

# Calculate % affected (non-zero score)
total = len(df_clean)
percent_affected = {
    col: round((df_clean[col] > 0).sum() / total * 100, 1) for col in mental_health_cols
}

# Calculate average score
avg_scores = df_clean[mental_health_cols].mean().round(2)

# Data for chart
data = {
    "category": mental_health_cols,
    "percent": [percent_affected[col] for col in mental_health_cols],
    "average": [avg_scores[col] for col in mental_health_cols],
    "label_pos_avg": [avg_scores[col] + 0.3 for col in mental_health_cols],  # above dot
    "average_label": [f"{avg_scores[col]:.1f}" for col in mental_health_cols],
    "label_pos_percent": [
        percent_affected[col] + 2 for col in mental_health_cols
    ],  # above bar
    "percent_label": [f"{percent_affected[col]}%" for col in mental_health_cols],
}

source = ColumnDataSource(data)

# Set up figure with extra y-axis for average score (0–10)
mental_health = figure(
    x_range=mental_health_cols,
    height=540,
    title="Mental Health: % Affected vs. Average Score",
    toolbar_location=None,
    tools="",
)

# Draw % affected bars
mental_health.vbar(
    x="category",
    top="percent",
    width=0.6,
    source=source,
    color="#f26843",
    legend_label="% Affected",
)

# Second y-axis for average scores
mental_health.extra_y_ranges = {"avg_score": Range1d(start=0, end=10)}
mental_health.add_layout(
    LinearAxis(y_range_name="avg_score", axis_label="Average Score (0–10)"), "right"
)

# Line and points (using dark gray)
mental_health.line(
    x="category",
    y="average",
    source=source,
    y_range_name="avg_score",
    line_width=2,
    color="#1f191a",
    legend_label="Avg Score",
)

mental_health.scatter(
    x="category",
    y="average",
    source=source,
    y_range_name="avg_score",
    size=8,
    color="#1f191a",
)

# Average score labels above dots
avg_labels = LabelSet(
    x="category",
    y="label_pos_avg",
    text="average_label",
    y_range_name="avg_score",
    source=source,
    text_align="center",
    text_font_size="10pt",
    text_color="#1f191a",
)
mental_health.add_layout(avg_labels)

# % labels above bars
percent_labels = LabelSet(
    x="category",
    y="label_pos_percent",
    text="percent_label",
    source=source,
    text_align="center",
    text_font_size="10pt",
    text_color="#f26843",
)
mental_health.add_layout(percent_labels)

# Style
mental_health.y_range.start = 0
mental_health.yaxis.axis_label = "% of Respondents (scored > 0)"
mental_health.xgrid.grid_line_color = None
mental_health.background_fill_color = "#faf9f4"
mental_health.outline_line_color = None
mental_health.legend.background_fill_color = "#faf9f4"

# Output
output_file("mental_health_combined_labeled.html")
# show(mental_health)
