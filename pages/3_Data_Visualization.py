import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from src.auth import auth_guard


# Theme-aware colors
THEME_BASE = st.get_option("theme.base")
PLOTLY_COLORS = px.colors.qualitative.Dark24 if THEME_BASE == "dark" else px.colors.qualitative.Set2

st.set_page_config(layout="wide")
auth_guard()

st.title("📊 Dynamic Financial Visualizations")

if "clean_df" not in st.session_state:
    st.warning("Please upload and preprocess data on the 'Overview' page.")
    if st.button("Go to File Upload"):
        st.switch_page("pages/1_File_Upload.py")
    st.stop()

df = st.session_state["clean_df"]
column_types = st.session_state.get("column_types", {})


# Session state init
if "plots" not in st.session_state:
    st.session_state["plots"] = []

if st.button("🗑️ Clear All Plots"):
    st.session_state["plots"] = []

# Typed column groups
numeric_cols = [col for col, typ in column_types.items() if typ == "numeric"]
categorical_cols = [col for col, typ in column_types.items() if typ == "categorical"]
boolean_cols = [col for col, typ in column_types.items() if typ == "boolean"]
datetime_cols = [col for col, typ in column_types.items() if typ == "datetime"]
text_cols = [col for col, typ in column_types.items() if typ == "text"]

# Sidebar: Column type selector
st.sidebar.header("🔧 Plot Controls")
col_type = st.sidebar.radio("Column Type", ["Numeric", "Categorical", "Boolean", "Datetime", "Text", "Mixed"])

# Plot Controls 
if col_type == "Numeric" and numeric_cols:
    selected_cols = st.sidebar.multiselect("Select numeric columns", numeric_cols, key="numeric_cols")
    plot_options = []

    if len(selected_cols) == 1:
        plot_options = ["Histogram", "Box Plot", "Line Plot", "Area Plot"]
    elif len(selected_cols) == 2:
        plot_options = ["Line Plot", "Scatter Plot", "Area Plot"]
    elif len(selected_cols) >= 2:
        plot_options = ["Line Plot", "Box Plot", "Correlation Heatmap", "Pair Plot"]

    selected_plots = st.sidebar.multiselect("Select plots", plot_options, key="numeric_plots")

    if st.sidebar.button("➕ Add Plot"):
        for plot in selected_plots:
            st.session_state["plots"].append({
                "type": "numeric",
                "plot": plot,
                "columns": selected_cols.copy()
            })

elif col_type == "Categorical" and categorical_cols:
    selected_cols = st.sidebar.multiselect("Select categorical columns", categorical_cols, key="cat_cols")
    cat_plot_type = st.sidebar.radio("Plot Type", ["Bar Plot", "Pie Chart", "Treemap"], key="cat_plot_type")

    agg_col = None
    if cat_plot_type == "Treemap" and numeric_cols:
        agg_col = st.sidebar.selectbox("Value Column for Treemap", numeric_cols, key="agg_col")

    if st.sidebar.button("➕ Add Plot"):
        for col in selected_cols:
            st.session_state["plots"].append({
                "type": "categorical",
                "column": col,
                "plot": cat_plot_type,
                "value_col": agg_col
            })

elif col_type == "Boolean" and boolean_cols:
    selected_cols = st.sidebar.multiselect("Select boolean columns", boolean_cols, key="bool_cols")
    if st.sidebar.button("➕ Add Plot"):
        for col in selected_cols:
            st.session_state["plots"].append({
                "type": "boolean",
                "column": col
            })

elif col_type == "Datetime" and datetime_cols:
    selected_col = st.sidebar.selectbox("Select datetime column", datetime_cols, key="dt_col")
    freq = st.sidebar.selectbox("Resample Frequency", ["D", "W", "ME", "QE", "YE"], index=2, key="dt_freq")
    agg_method = st.sidebar.selectbox("Aggregation", ["Count", "Sum", "Mean"], key="agg_method")

    value_col = None
    if agg_method in ["Sum", "Mean"] and numeric_cols:
        value_col = st.sidebar.selectbox("Numeric Column to Aggregate", numeric_cols, key="value_col")

    if st.sidebar.button("➕ Add Plot", key="add_datetime_plot"):
        st.session_state["plots"].append({
            "type": "datetime",
            "column": selected_col,
            "freq": freq,
            "agg": agg_method.lower(),
            "value_col": value_col
        })

elif col_type == "Text" and text_cols:
    selected_col = st.sidebar.selectbox("Select text column", text_cols, key="text_col")
    max_words = st.sidebar.slider("Top N frequent words", 5, 50, 15)
    if st.sidebar.button("➕ Add Word Frequency Plot"):
        st.session_state["plots"].append({
            "type": "text",
            "column": selected_col,
            "top_n": max_words
        })

elif col_type == "Mixed":
    st.sidebar.markdown("Create a heatmap between two categorical columns")
    cat1 = st.sidebar.selectbox("Categorical Column 1", categorical_cols, key="cat1")
    cat2 = st.sidebar.selectbox("Categorical Column 2", categorical_cols, key="cat2")

    if st.sidebar.button("➕ Add Heatmap"):
        st.session_state["plots"].append({
            "type": "cat_heatmap",
            "row": cat1,
            "col": cat2
        })

# Plot Rendering
left_col, right_col = st.columns(2)

for i, plot_data in enumerate(st.session_state["plots"]):
    col = left_col if i % 2 == 0 else right_col
    with col:
        with st.expander(f"🔸 Plot {i+1}", expanded=True):
            try:
                if plot_data["type"] == "numeric":
                    cols = plot_data["columns"]
                    plot = plot_data["plot"]

                    if plot == "Histogram" and len(cols) == 1:
                        fig = px.histogram(df, x=cols[0], nbins=30, color_discrete_sequence=PLOTLY_COLORS)
                        st.subheader(f"🔸 Histogram of {cols[0]}")
                        st.plotly_chart(fig, use_container_width=True)

                    elif plot == "Box Plot":
                        fig = px.box(df, y=cols, color_discrete_sequence=PLOTLY_COLORS)
                        st.subheader(f"🔸 Box Plot of {', '.join(cols)}")
                        st.plotly_chart(fig, use_container_width=True)

                    elif plot == "Line Plot":
                        melted = df[cols].reset_index().melt(id_vars="index", var_name="Variable", value_name="Value")
                        fig = px.line(melted, x="index", y="Value", color="Variable",
                                      color_discrete_sequence=PLOTLY_COLORS)
                        st.subheader(f"🔸 Line Plot of {', '.join(cols)}")
                        st.plotly_chart(fig, use_container_width=True)

                    elif plot == "Scatter Plot" and len(cols) == 2:
                        fig = px.scatter(df, x=cols[0], y=cols[1], color_discrete_sequence=PLOTLY_COLORS)
                        st.subheader(f"🔸 Scatter Plot: {cols[0]} vs {cols[1]}")
                        st.plotly_chart(fig, use_container_width=True)

                    elif plot == "Correlation Heatmap":
                        corr = df[cols].corr()
                        fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r")
                        st.subheader("🔸 Correlation Heatmap")
                        st.plotly_chart(fig, use_container_width=True)

                    elif plot == "Pair Plot":
                        fig = px.scatter_matrix(df, dimensions=cols, color_discrete_sequence=PLOTLY_COLORS)
                        st.subheader("🔸 Pair Plot")
                        st.plotly_chart(fig, use_container_width=True)

                    elif plot == "Area Plot":
                        melted = df[cols].reset_index().melt(id_vars="index", var_name="Variable", value_name="Value")
                        fig = px.area(melted, x="index", y="Value", color="Variable",
                                      color_discrete_sequence=PLOTLY_COLORS)
                        st.subheader(f"🔸 Area Plot of {', '.join(cols)}")
                        st.plotly_chart(fig, use_container_width=True)

                elif plot_data["type"] == "categorical":
                    colname = plot_data["column"]
                    plot_type = plot_data.get("plot", "Bar Plot")
                    value_col = plot_data.get("value_col", None)
                    counts = df[colname].value_counts().reset_index()
                    counts.columns = [colname, 'count']

                    if plot_type == "Bar Plot":
                        fig = px.bar(counts, x=colname, y='count',
                                     color=colname, color_discrete_sequence=PLOTLY_COLORS)
                        st.subheader(f"🔸 Bar Plot of {colname}")

                    elif plot_type == "Pie Chart":
                        fig = px.pie(counts, names=colname, values='count',
                                     color=colname, color_discrete_sequence=PLOTLY_COLORS, hole=0.4)
                        st.subheader(f"🔸 Pie Chart of {colname}")

                    elif plot_type == "Treemap" and value_col:
                        fig = px.treemap(df, path=[colname], values=value_col,
                                         color=colname, color_discrete_sequence=PLOTLY_COLORS)
                        st.subheader(f"🔸 Treemap: {colname} by {value_col}")

                    st.plotly_chart(fig, use_container_width=True)

                elif plot_data["type"] == "boolean":
                    colname = plot_data["column"]
                    counts = df[colname].value_counts().reset_index()
                    # Keep 0 and 1 as labels
                    counts.columns = [colname, 'count']
                    counts[colname] = counts[colname].astype(str)  # ensure string labels
                    fig = px.pie(counts, names=colname, values='count',
                        color=colname, color_discrete_sequence=PLOTLY_COLORS, hole=0.4)

                    st.subheader(f"🔸 Pie Chart of Boolean Column {colname}")
                    st.plotly_chart(fig, use_container_width=True)

                elif plot_data["type"] == "datetime":
                    colname = plot_data["column"]
                    freq = plot_data.get("freq", "ME")
                    agg = plot_data.get("agg", "count")
                    value_col = plot_data.get("value_col", None)

                    ts_df = df[[colname]].copy()

                    if agg == "count":
                        ts_df["__count"] = 1
                        ts = ts_df.set_index(colname).resample(freq)["__count"].count().reset_index()
                        y_col = "__count"
                        title = "Count"
                    elif agg in ["sum", "mean"] and value_col:
                        ts_df[value_col] = df[value_col]
                        resampled = ts_df.set_index(colname).resample(freq)[value_col]
                        ts = resampled.sum().reset_index() if agg == "sum" else resampled.mean().reset_index()
                        y_col = value_col
                        title = f"{agg.title()} of {value_col}"
                    else:
                        st.warning("⚠️ Missing value column or invalid aggregation.")
                        continue

                    fig = px.line(ts, x=colname, y=y_col, markers=True,
                                  title=f"> Time Series ({freq}) – {title}",
                                  labels={y_col: title, colname: "Date"},
                                  color_discrete_sequence=PLOTLY_COLORS)
                    fig.update_layout(xaxis_title="Date", yaxis_title=title, hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)

                elif plot_data["type"] == "cat_heatmap":
                    row = plot_data["row"]
                    col_ = plot_data["col"]
                    heat_df = pd.crosstab(df[row], df[col_])
                    fig = px.imshow(heat_df, text_auto=True, color_continuous_scale="Viridis")
                    st.subheader(f" 🔸Heatmap: {row} × {col_}")
                    st.plotly_chart(fig, use_container_width=True)

                elif plot_data["type"] == "text":
                    colname = plot_data["column"]
                    top_n = plot_data["top_n"]
                    text_data = df[colname].dropna().astype(str).str.cat(sep=' ')
                    words = [word.lower() for word in text_data.split()]
                    word_counts = Counter(words)
                    most_common = word_counts.most_common(top_n)
                    freq_df = pd.DataFrame(most_common, columns=['Word', 'Frequency'])
                    fig = px.bar(freq_df, x='Word', y='Frequency', color='Word',
                                 color_discrete_sequence=PLOTLY_COLORS)
                    st.subheader(f"🔸 Word Frequency for {colname}")
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"⚠️ Error rendering plot: {e}")

# Navigation links
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("Back to Home"):
        st.switch_page("Home.py")
with col2:
    if st.button("Back to File Upload "):
        st.switch_page("pages/1_File_Upload.py")
with col3:
    if st.button("Back to Data Analysis"):
        st.switch_page("pages/2_Data_Analysis.py")
with col4:
    if st.button(" Go to OpenAI Summary"):
        st.switch_page("pages/4_OpenAI_Summary.py")
with col5:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

