import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.models import (
    ColumnDataSource,
    LinearColorMapper,
    ColorBar,
    LabelSet,
    LinearAxis,
    Range1d,
)
from bokeh.transform import transform, dodge
from bokeh.palettes import RdGy


df_clean = pd.read_csv("df_clean.csv")

colors = ["#f26843", "#89AAE6", "#1f191a", "#ef4434", "#C4DACF"]

# Define columns
effect_col = "Music effects"
mental_cols = ["Anxiety", "Depression", "Insomnia", "OCD"]

# Group by music effect
mental_means = df_clean.groupby(effect_col)[mental_cols].mean().round(2)
hours_mean = df_clean.groupby(effect_col)["Hours per day"].mean().round(2)

# Combine for visualization
combined_df = mental_means.copy()
combined_df["Hours per day"] = hours_mean
combined_df.reset_index(inplace=True)

# Create ColumnDataSource
source = ColumnDataSource(combined_df)

# Bar plot setup
p = figure(
    x_range=combined_df["Music effects"],
    height=500,
    width=800,
    title="Music's Perceived Effect vs Mental Health & Listening Time",
    toolbar_location=None,
    y_range=Range1d(0, 10),
)

# Bar settings
metrics = ["Anxiety", "Depression", "Insomnia", "OCD"]
colors = ["#f26843", "#89AAE6", "#ef4434", "#C4DACF"]
bar_width = 0.18
offsets = [-0.3, -0.1, 0.1, 0.3]

# Plot grouped vertical bars
for i, (metric, color) in enumerate(zip(metrics, colors)):
    p.vbar(
        x=dodge("Music effects", offsets[i], range=p.x_range),
        top=metric,
        width=bar_width,
        source=source,
        color=color,
        legend_label=metric,
    )

# Add line for Hours per day (secondary y-axis)
p.extra_y_ranges = {"Hours": Range1d(start=0, end=5)}
p.add_layout(
    LinearAxis(y_range_name="Hours", axis_label="Listening Hours/Day"), "right"
)

p.line(
    x="Music effects",
    y="Hours per day",
    source=source,
    y_range_name="Hours",
    line_width=3,
    color="#1f191a",
    legend_label="Hours per day",
)

# Styling
p.yaxis.axis_label = "Mental Health Score (0–10)"
p.background_fill_color = "#faf9f4"
p.xgrid.grid_line_color = None
p.outline_line_color = None
p.legend.location = "top_center"
p.legend.orientation = "horizontal"

output_file("music_effects_vs_health.html")
show(p)

#                Anxiety  Depression  Insomnia   OCD
# Music effects
# Improve           6.10        4.95      3.79  2.78
# No effect         5.03        4.50      3.76  2.19
# Worsen            6.58        7.33      4.50  2.92
# Music effects
# Improve      3.77
# No effect    3.59
# Worsen       2.92
# Name: Hours per day, dtype: float64
