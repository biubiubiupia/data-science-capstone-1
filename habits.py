import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.models import (
    ColumnDataSource,
    Legend,
    Range1d,
    LinearAxis,
    LabelSet,
    BasicTicker,
    ColorBar,
    LinearColorMapper,
    FactorRange,
)
from bokeh.transform import transform, factor_cmap
from bokeh.palettes import RdGy

df_clean = pd.read_csv("df_clean.csv")

colors = ["#f26843", "#89AAE6", "#1f191a", "#ef4434", "#C4DACF"]

# 📊 Listening Habit Y/N Chart

# Define columns
habit_cols = [
    "While working",
    "Instrumentalist",
    "Composer",
    "Exploratory",
    "Foreign languages",
]
yes_counts = []
no_counts = []

# Count 'Yes' and 'No' responses for each column
for col in habit_cols:
    counts = df_clean[col].value_counts()
    yes_counts.append(counts.get("Yes", 0))
    no_counts.append(counts.get("No", 0))

total_counts = [yes + no for yes, no in zip(yes_counts, no_counts)]
yes_percents = [
    round((yes / total) * 100) for yes, total in zip(yes_counts, total_counts)
]
no_percents = [round((no / total) * 100) for no, total in zip(no_counts, total_counts)]

# Create data for Bokeh
source = ColumnDataSource(
    data=dict(
        category=habit_cols,
        Yes=yes_counts,
        No=no_counts,
        Yes_pct=[f"{p}%" for p in yes_percents],
        No_pct=[f"{p}%" for p in no_percents],
        Yes_plus_No=[y + n for y, n in zip(yes_counts, no_counts)],
    )
)
# Step 2: Plot
habits = figure(
    x_range=habit_cols,
    height=400,
    title="Yes/No Distribution per Question",
    toolbar_location=None,
    tools="",
)

visual = habits.vbar_stack(
    ["Yes", "No"], x="category", width=0.6, color=["#f26843", "#1f191a"], source=source
)

# Add labels for 'Yes'
yes_labels = LabelSet(
    x="category",
    y="Yes",
    text="Yes_pct",
    source=source,
    text_font_size="10pt",
    text_color="white",
    x_offset=0,
    y_offset=0,
    text_align="center",
    text_baseline="bottom",
)

source.data["Yes_plus_No"] = [
    y + n for y, n in zip(source.data["Yes"], source.data["No"])
]

no_labels = LabelSet(
    x="category",
    y="Yes_plus_No",
    text="No_pct",
    source=source,
    text_font_size="10pt",
    text_color="black",
    x_offset=0,
    y_offset=0,
    text_align="center",
    text_baseline="bottom",
)

# Manually create legend items
legend = Legend(
    items=[("Yes", [visual[0]]), ("No", [visual[1]])],
    orientation="horizontal",
    location="center",
    background_fill_color="#faf9f4",
)

# Style
habits.y_range.start = 0
habits.xgrid.grid_line_color = None
habits.axis.minor_tick_line_color = None
habits.outline_line_color = None
habits.add_layout(legend, "below")
habits.background_fill_color = "#faf9f4"
habits.add_layout(yes_labels)
habits.add_layout(no_labels)

output_file("stacked_bars.html")
show(habits)


yesno_map = {"Yes": 1, "No": 0}
for col in habit_cols:
    df_clean[col] = df_clean[col].map(yesno_map)

mental_cols = ["Anxiety", "Depression", "Insomnia", "OCD"]
correlation_df = df_clean[habit_cols + mental_cols]
corr_matrix = correlation_df.corr().loc[habit_cols, mental_cols]

data = {"habit": [], "metric": [], "value": [], "value_str": []}
for habit in corr_matrix.index:
    for metric in corr_matrix.columns:
        val = round(corr_matrix.loc[habit, metric], 3)
        data["habit"].append(habit)
        data["metric"].append(metric)
        data["value"].append(val)
        data["value_str"].append(str(val))

source = ColumnDataSource(data)

# Step 4: Color mapper
mapper = LinearColorMapper(palette=RdGy[11], low=-1, high=1)

# Step 5: Plot
habits_corr = figure(
    x_range=mental_cols,
    y_range=list(reversed(habit_cols)),
    height=400,
    width=600,
    title="Correlation Between Listening Habits & Mental Health",
    toolbar_location=None,
    tools="",
)

habits_corr.rect(
    x="metric",
    y="habit",
    width=1,
    height=1,
    source=source,
    fill_color=transform("value", mapper),
    line_color=None,
)

# Add labels to each cell
labels = LabelSet(
    x="metric",
    y="habit",
    text="value_str",
    source=source,
    text_align="center",
    text_baseline="middle",
    text_font_size="9pt",
    text_color="#1f191a",
)
habits_corr.add_layout(labels)

# Add color bar
color_bar = ColorBar(
    color_mapper=mapper,
    location=(0, 0),
    ticker=BasicTicker(desired_num_ticks=5),
    title="Correlation",
)
habits_corr.add_layout(color_bar, "right")

# Style
habits_corr.background_fill_color = "#faf9f4"
habits_corr.grid.grid_line_color = None
habits_corr.outline_line_color = None
habits_corr.xaxis.axis_label = "Mental Health Metric"
habits_corr.yaxis.axis_label = "Listening Habit"

output_file("habit_vs_mental_health.html")
# show(habits_corr)

# ❓ How does listening hours correlates with mental health?

correlations = {}
for col in mental_cols:
    corr = df_clean["Hours per day"].corr(df_clean[col])
    correlations[col] = round(corr, 3)

# Print the result
# for metric, value in correlations.items():
#     print(f"Correlation between Hours per day and {metric}: {value}")


# ❓ What habits or patterns are most common among people who report the highest mental health issue scores?
threshold = df_clean["Depression"].quantile(0.75)
high_depression = df_clean[df_clean["Depression"] >= threshold]

behavior_summary = high_depression[habit_cols].mean().sort_values(ascending=False)
# print(behavior_summary)

rest = df_clean[df_clean["Depression"] < threshold]
comparison = pd.DataFrame(
    {
        "High Scorers": high_depression[habit_cols].mean(),
        "Others": rest[habit_cols].mean(),
    }
)
comparison["Difference"] = comparison["High Scorers"] - comparison["Others"]
# print(comparison.sort_values("Difference", ascending=False))

for metric in mental_cols:
    # print(f"\n=== {metric.upper()} ===")

    # 1. Define top 25% threshold
    threshold = df_clean[metric].quantile(0.75)
    high_group = df_clean[df_clean[metric] >= threshold]
    rest_group = df_clean[df_clean[metric] < threshold]

    # 2. Compare behavior frequencies
    comparison = pd.DataFrame(
        {
            "High Scorers": high_group[habit_cols].mean(),
            "Others": rest_group[habit_cols].mean(),
        }
    )
    comparison["Difference"] = comparison["High Scorers"] - comparison["Others"]
    # print(comparison.sort_values("Difference", ascending=False))

habit_diffs = []

for metric in mental_cols:
    threshold = df_clean[metric].quantile(0.75)
    high_group = df_clean[df_clean[metric] >= threshold]
    rest_group = df_clean[df_clean[metric] < threshold]

    comparison = pd.DataFrame(
        {
            "High Scorers": high_group[habit_cols].mean(),
            "Others": rest_group[habit_cols].mean(),
        }
    )
    comparison["Difference"] = comparison["High Scorers"] - comparison["Others"]
    comparison["Habit"] = comparison.index
    comparison["Metric"] = metric

    # Reorder habits to match original order
    comparison = comparison.set_index("Habit").loc[habit_cols].reset_index()

    habit_diffs.append(comparison[["Metric", "Habit", "Difference"]])

    df_plot = pd.concat(habit_diffs)
df_plot["x"] = list(zip(df_plot["Metric"], df_plot["Habit"]))

source = ColumnDataSource(df_plot)

p = figure(
    x_range=FactorRange(*df_plot["x"]),
    height=450,
    width=950,
    title="Differences in Habit Use Across Mental Health Symptoms",
    toolbar_location=None,
    tools="",
)

p.vbar(
    x="x",
    top="Difference",
    width=0.9,
    source=source,
    line_color="white",
    fill_color=factor_cmap("x", palette=colors, factors=habit_cols, start=1, end=2),
)

p.yaxis.axis_label = "High Scorers – Others"
p.xaxis.major_label_orientation = 1.2
p.xgrid.grid_line_color = None
p.xaxis.group_text_font_style = "bold"

# show(p)
