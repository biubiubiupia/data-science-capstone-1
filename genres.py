import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar, LabelSet, Legend
from bokeh.transform import transform
from bokeh.palettes import RdGy

df_clean = pd.read_csv("df_clean.csv")

colors = ["#f26843", "#89AAE6", "#1f191a", "#ef4434", "#C4DACF"]

# 📊 Genre Frequency Chart

# Define genres and frequency levels
genres = [
    "Classical",
    "Country",
    "EDM",
    "Folk",
    "Gospel",
    "Hip hop",
    "Jazz",
    "K pop",
    "Latin",
    "Lofi",
    "Metal",
    "Pop",
    "R&B",
    "Rap",
    "Rock",
    "Video game music",
]

frequency_levels = ["Very frequently", "Sometimes", "Rarely", "Never"]

# Step 1: Build counts for each genre and level
genre_counts = {
    genre: {
        level: df_clean[f"Frequency [{genre}]"].value_counts().get(level, 0)
        for level in frequency_levels
    }
    for genre in genres
}

# Step 2: Sort genres by "Very frequently"
sorted_genres = sorted(genre_counts, key=lambda g: genre_counts[g]["Very frequently"])

# Step 3: Build source data
source_data = {"genre": sorted_genres}
for level in frequency_levels:
    source_data[level] = [genre_counts[genre][level] for genre in sorted_genres]

source = ColumnDataSource(data=source_data)

# Step 4: Configure spacing
bar_height = 0.4  # Smaller = more spacing
plot_height = int(len(sorted_genres) * 30)  # Adjust spacing per row

# Step 5: Create figure
genres = figure(
    y_range=sorted_genres,
    height=plot_height,
    title="Listening Frequency by Genre",
    toolbar_location=None,
    tools="",
)

# Stack bars
colors = ["#f26843", "#1f191a", "#ef4434", "#C4DACF"]
renderers = genres.hbar_stack(
    frequency_levels, y="genre", height=bar_height, color=colors, source=source
)

# Style
genres.x_range.start = 0
genres.ygrid.grid_line_color = None
genres.outline_line_color = None
genres.background_fill_color = "#faf9f4"
genres.yaxis.major_label_orientation = 1

# Legend
legend = Legend(
    items=[(label, [r]) for label, r in zip(frequency_levels, renderers)],
    location="center",
    orientation="horizontal",  # ← makes it horizontal
    background_fill_color="#faf9f4",
)
genres.add_layout(legend, "below")

# Output
output_file("genre_frequency_stacked.html")
show(genres)


# ANALYSIS
# ❓ Does listening to certain genres more frequently relate to higher or lower mental health scores?

# Step 1: Convert genre frequency strings to numeric scale
frequency_scale = {
    "Never": 0,
    "Rarely": 1,
    "Sometimes": 2,
    "Very frequently": 3,
}

# Step 2: Apply this scale to all genre frequency columns
# genres = [
#     "Classical",
#     "Country",
#     "EDM",
#     "Folk",
#     "Gospel",
#     "Hip hop",
#     "Jazz",
#     "K pop",
#     "Latin",
#     "Lofi",
#     "Metal",
#     "Pop",
#     "R&B",
#     "Rap",
#     "Rock",
#     "Video game music",
# ]

# Step 3: Loop through each genre column and map the values
for genre in genres:
    col = f"Frequency [{genre}]"
    df_clean[col] = df_clean[col].map(frequency_scale)

# ✅ Step 3: Compute Correlation Matrix
genre_cols = [f"Frequency [{g}]" for g in genres]
mental_health_cols = ["Anxiety", "Depression", "Insomnia", "OCD"]

corr_df = df_clean[genre_cols + mental_health_cols]

corr_matrix = corr_df.corr().loc[genre_cols, mental_health_cols]


corr_data = {"genre": [], "metric": [], "value": []}
for genre in corr_matrix.index:
    for metric in corr_matrix.columns:
        corr_data["genre"].append(genre.replace("Frequency [", "").replace("]", ""))
        corr_data["metric"].append(metric)
        corr_data["value"].append(round(corr_matrix.loc[genre, metric], 3))

source = ColumnDataSource(corr_data)

# Step 3: Set up color mapper
mapper = LinearColorMapper(palette=RdGy[11], low=-1, high=1)

# Step 4: Create figure
p = figure(
    x_range=mental_health_cols,
    y_range=list(
        reversed([g.replace("Frequency [", "").replace("]", "") for g in genre_cols])
    ),
    height=600,
    width=600,
    title="Correlation Between Genre Frequency & Mental Health",
    toolbar_location=None,
    tools="",
)

p.rect(
    x="metric",
    y="genre",
    width=1,
    height=1,
    source=source,
    fill_color=transform("value", mapper),
    line_color=None,
)

labels = LabelSet(
    x="metric",
    y="genre",
    text="value",
    source=source,
    text_align="center",
    text_baseline="middle",
    text_font_size="9pt",
    text_color="#1f191a",
)

# Add color bar
color_bar = ColorBar(color_mapper=mapper, location=(0, 0), title="Correlation")
p.add_layout(color_bar, "right")

# Style
p.xaxis.axis_label = "Mental Health Metric"
p.yaxis.axis_label = "Genre"
p.background_fill_color = "#faf9f4"
p.grid.grid_line_color = None
p.outline_line_color = None
p.add_layout(labels)


output_file("genre_vs_mental_health_heatmap.html")
# show(p)
