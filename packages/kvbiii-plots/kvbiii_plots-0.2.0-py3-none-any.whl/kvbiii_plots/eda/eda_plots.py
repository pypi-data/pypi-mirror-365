import numpy as np
import pandas as pd
import plotly.graph_objects as go


class Plots:
    """A class for creating exploratory data analysis plots."""

    def check_data(
        self, data: pd.DataFrame | pd.Series | np.ndarray | list
    ) -> np.ndarray:
        """
        Validates and converts input data to a NumPy array.

        Args:
            data (pd.DataFrame | pd.Series | np.ndarray | list): Input data to validate.

        Returns:
            np.ndarray: Converted data as a NumPy array with NaN values removed.

        Raises:
            TypeError: If data is not a pandas DataFrame, Series, numpy array, or list.
        """
        if not isinstance(data, (pd.DataFrame, pd.Series, np.ndarray, list)):
            raise TypeError(
                "Wrong type of data. It should be pandas DataFrame, pandas Series, numpy array, or list"
            )
        data = np.array(data)
        data = data[~np.isnan(data)]
        if data.ndim == 2:
            data = data.squeeze()
        return data

    def heatmap(
        self, data: pd.DataFrame, xaxis_title: str = "", yaxis_title: str = ""
    ) -> None:
        """
        Creates and displays a heatmap visualization.

        Args:
            data (pd.DataFrame): Input DataFrame for heatmap visualization.
            xaxis_title (str, optional): Title for the x-axis. Defaults to "".
            yaxis_title (str, optional): Title for the y-axis. Defaults to "".
        """
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
            title="<b>Heatmap</b>",
            title_x=0.5,
            font=dict(family="Times New Roman", size=16, color="Black"),
        )
        fig.show("png")

    def barplot_missing_values(
        self,
        data: pd.DataFrame | pd.Series | np.ndarray,
        features_names: list[str],
        name: str = "",
    ) -> None:
        """
        Creates and displays a bar plot for missing values visualization.

        Args:
            data (pd.DataFrame | pd.Series | np.ndarray): Input data for the bar plot.
            features_names (list[str]): List of feature names for x-axis labels.
            name (str, optional): Name to include in the plot title. Defaults to "".
        """
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
            title=f"<b>Bar chart {name.title()}</b>",
            title_x=0.5,
            yaxis_title="Frequency",
            xaxis=dict(title="Features", showticklabels=True),
            font=dict(family="Times New Roman", size=16, color="Black"),
        )
        fig.show("png")


if __name__ == "__main__":
    # Example usage of the Plots class
    import numpy as np
    import pandas as pd

    # Create sample data
    sample_data = pd.DataFrame(
        {"A": [1, 2, 3, 4, 5], "B": [2, 4, 6, 8, 10], "C": [1, 3, 5, 7, 9]}
    )

    # Initialize the Plots class
    plots = Plots()

    # Example 1: Create a heatmap
    correlation_matrix = sample_data.corr()
    plots.heatmap(correlation_matrix, xaxis_title="Features", yaxis_title="Features")

    # Example 2: Create a bar plot for missing values
    missing_counts = [0, 2, 1]  # Example missing value counts
    feature_names = ["Feature A", "Feature B", "Feature C"]
    plots.barplot_missing_values(missing_counts, feature_names, name="Missing Values")
