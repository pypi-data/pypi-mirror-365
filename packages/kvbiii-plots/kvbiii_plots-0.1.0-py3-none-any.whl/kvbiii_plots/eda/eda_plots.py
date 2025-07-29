import numpy as np
import pandas as pd
import plotly.graph_objects as go


class Plots:
    def check_data(self, data):
        if (
            not isinstance(data, pd.DataFrame)
            and not isinstance(data, pd.Series)
            and not isinstance(data, np.ndarray)
        ):
            raise TypeError(
                "Wrong type of data. It should be pandas DataFrame, pandas Series, numpy array"
            )
        data = np.array(data)
        data = data[~np.isnan(data)]
        if data.ndim == 2:
            data = data.squeeze()
        return data

    def heatmap(self, data, xaxis_title="", yaxis_title=""):
        values = np.array(data).T
        x_labels = list(data.index)
        y_labels = list(data.columns)
        fig = go.Figure()
        fig.add_trace(
            go.Heatmap(
                z=values,
                x=x_labels,
                y=y_labels,
                colorscale="blues",
                text=[list(map(str, i)) for i in values],
                texttemplate="%{text}",
                showscale=True,
                ygap=1,
                xgap=1,
            )
        )
        fig.update_layout(
            template="simple_white",
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            width=800,
            height=800,
            title=f"<b>Heatmap<b>",
            title_x=0.5,
            font=dict(family="Times New Roman", size=16, color="Black"),
        )
        fig.show("png")

    def barplot_missing_values(self, data, features_names, name=""):
        data = self.check_data(data=data)
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=features_names,
                y=data,
                marker=dict(
                    color=data, colorscale="rainbow", line=dict(color="black", width=1)
                ),
            )
        )
        fig.update_layout(
            template="simple_white",
            width=max(30 * len(features_names), 1600),
            height=max(30 * len(features_names), 800),
            title=f"<b>Bar chart {name.title()}<b>",
            title_x=0.5,
            yaxis_title="Frequency",
            xaxis=dict(title="Features", showticklabels=True),
            font=dict(family="Times New Roman", size=16, color="Black"),
        )
        fig.show("png")
