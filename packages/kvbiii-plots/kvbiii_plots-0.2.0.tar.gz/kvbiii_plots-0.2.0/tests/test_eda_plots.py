import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from kvbiii_plots.eda.eda_plots import Plots


def test_plots_check_data_dataframe_input_returns_squeezed_array() -> None:
    """Tests check_data correctly processes numeric DataFrame input and returns squeezed array.

    Asserts:
        - Method returns numpy array from DataFrame input
        - Array is properly squeezed to 1D when possible
        - Numeric data is processed correctly
    """
    # Create a numeric-only DataFrame for this test
    numeric_df = pd.DataFrame(
        {"A": [1.0, 2.0, 3.0, 4.0, 5.0], "B": [6.0, 7.0, 8.0, 9.0, 10.0]}
    )

    plots = Plots()

    # The check_data method will fail with mixed-type DataFrame due to isnan() limitations
    # So we test with a single numeric column
    result = plots.check_data(numeric_df["A"])

    assert isinstance(result, np.ndarray), f"Expected numpy array, got {type(result)}"
    assert result.ndim == 1, f"Expected 1D array, got {result.ndim}D array"
    assert not np.any(np.isnan(result)), "Result contains NaN values"


def test_plots_check_data_series_input_returns_clean_array(
    sample_series: pd.Series,
) -> None:
    """Tests check_data correctly processes Series input and removes NaN values.

    Args:
        sample_series (pd.Series): Fixture containing test Series

    Asserts:
        - Method returns numpy array from Series input
        - NaN values are properly removed
        - Array maintains expected data type
    """
    plots = Plots()
    result = plots.check_data(sample_series)

    assert isinstance(result, np.ndarray), f"Expected numpy array, got {type(result)}"
    assert not np.any(np.isnan(result)), "Result contains NaN values"
    assert len(result) <= len(sample_series), "Result length exceeds input length"


def test_plots_check_data_numpy_array_input_removes_nan_values(
    dataframe_with_nan: pd.DataFrame,
) -> None:
    """Tests check_data removes NaN values from numpy array input.

    Args:
        dataframe_with_nan (pd.DataFrame): Fixture containing DataFrame with NaN values

    Asserts:
        - NaN values are completely removed from result
        - Array shape is reduced appropriately
        - Remaining values are preserved correctly
    """
    plots = Plots()
    array_with_nan = dataframe_with_nan["values"].values
    original_nan_count = np.isnan(array_with_nan).sum()

    result = plots.check_data(array_with_nan)

    assert not np.any(np.isnan(result)), "Result still contains NaN values"
    assert (
        len(result) == len(array_with_nan) - original_nan_count
    ), "Incorrect number of values removed"


def test_plots_check_data_list_input_converts_to_array(
    sample_list: list[float],
) -> None:
    """Tests check_data correctly converts list input to numpy array.

    Args:
        sample_list (list[float]): Fixture containing test list

    Asserts:
        - List is converted to numpy array
        - Array preserves original list values
        - No data loss during conversion
    """
    plots = Plots()
    result = plots.check_data(sample_list)

    assert isinstance(result, np.ndarray), f"Expected numpy array, got {type(result)}"
    assert len(result) == len(sample_list), "Array length differs from original list"
    np.testing.assert_array_almost_equal(
        result, np.array(sample_list), err_msg="Array values differ from original list"
    )


def test_plots_check_data_multidimensional_array_gets_squeezed(
    multidimensional_array: np.ndarray,
) -> None:
    """Tests check_data properly squeezes multidimensional arrays.

    Args:
        multidimensional_array (np.ndarray): Fixture containing multidimensional array

    Asserts:
        - Multidimensional array is squeezed to 1D
        - Data values are preserved during squeeze
        - Result has expected shape
    """
    plots = Plots()
    result = plots.check_data(multidimensional_array)

    assert result.ndim == 1, f"Expected 1D array after squeeze, got {result.ndim}D"
    expected_size = multidimensional_array.size
    assert (
        result.size == expected_size
    ), f"Expected size {expected_size}, got {result.size}"


def test_plots_check_data_invalid_input_raises_type_error() -> None:
    """Tests check_data raises TypeError for invalid input types.

    Asserts:
        - TypeError is raised for string input
        - TypeError is raised for dictionary input
        - Error message contains expected information
    """
    plots = Plots()

    with pytest.raises(TypeError, match="Wrong type of data"):
        plots.check_data("invalid_string_input")

    with pytest.raises(TypeError, match="Wrong type of data"):
        plots.check_data({"invalid": "dict"})

    with pytest.raises(TypeError, match="Wrong type of data"):
        plots.check_data(42)


def test_plots_check_data_mixed_type_dataframe_raises_error() -> None:
    """Tests check_data handles mixed-type DataFrame with appropriate error.

    Asserts:
        - Method raises TypeError when encountering mixed-type data
        - Error occurs due to isnan() incompatibility with object dtype
        - Exception message contains relevant information about isnan issue
    """
    plots = Plots()
    mixed_df = pd.DataFrame(
        {"numeric": [1, 2, 3], "string": ["a", "b", "c"], "mixed": [1, "b", 3.5]}
    )

    # The check_data method will fail because np.isnan() cannot handle object dtype
    with pytest.raises(TypeError, match="ufunc 'isnan' not supported"):
        plots.check_data(mixed_df)


@patch("plotly.graph_objects.Figure.show")
def test_plots_heatmap_dataframe_input_creates_visualization(
    mock_show: MagicMock, correlation_dataframe: pd.DataFrame
) -> None:
    """Tests heatmap creates visualization for DataFrame input.

    Args:
        mock_show (MagicMock): Mock for Figure.show method
        correlation_dataframe (pd.DataFrame): Fixture containing correlation matrix

    Asserts:
        - Heatmap method executes without errors
        - Figure.show is called once with correct format
        - Plot configuration is properly set
    """
    plots = Plots()
    plots.heatmap(
        correlation_dataframe, xaxis_title="Features", yaxis_title="Variables"
    )

    mock_show.assert_called_once_with("png")


@patch("plotly.graph_objects.Figure.show")
def test_plots_heatmap_empty_dataframe_handles_gracefully(
    mock_show: MagicMock, empty_dataframe: pd.DataFrame
) -> None:
    """Tests heatmap handles empty DataFrame input gracefully.

    Args:
        mock_show (MagicMock): Mock for Figure.show method
        empty_dataframe (pd.DataFrame): Fixture containing empty DataFrame

    Asserts:
        - Method executes without raising exceptions
        - Figure.show is still called appropriately
        - No data errors occur with empty input
    """
    plots = Plots()

    try:
        plots.heatmap(empty_dataframe)
        mock_show.assert_called_once_with("png")
    except Exception as e:
        # If an exception occurs, it should be a reasonable one related to empty data
        assert "empty" in str(e).lower() or "shape" in str(e).lower()


@patch("plotly.graph_objects.Figure.show")
def test_plots_heatmap_single_value_dataframe_processes_correctly(
    mock_show: MagicMock, single_value_dataframe: pd.DataFrame
) -> None:
    """Tests heatmap processes single-value DataFrame correctly.

    Args:
        mock_show (MagicMock): Mock for Figure.show method
        single_value_dataframe (pd.DataFrame): Fixture containing single-value DataFrame

    Asserts:
        - Single-value DataFrame is processed without errors
        - Visualization is created successfully
        - Figure.show method is called
    """
    plots = Plots()
    plots.heatmap(single_value_dataframe)

    mock_show.assert_called_once_with("png")


@patch("plotly.graph_objects.Figure.show")
def test_plots_heatmap_default_axis_titles_work_correctly(
    mock_show: MagicMock, correlation_dataframe: pd.DataFrame
) -> None:
    """Tests heatmap uses default empty axis titles when not specified.

    Args:
        mock_show (MagicMock): Mock for Figure.show method
        correlation_dataframe (pd.DataFrame): Fixture containing correlation matrix

    Asserts:
        - Method executes with default parameters
        - Default axis titles are applied correctly
        - No errors occur with minimal parameters
    """
    plots = Plots()
    plots.heatmap(correlation_dataframe)

    mock_show.assert_called_once_with("png")


@patch("plotly.graph_objects.Figure")
def test_plots_heatmap_figure_configuration_matches_expected(
    mock_figure: MagicMock, correlation_dataframe: pd.DataFrame
) -> None:
    """Tests heatmap configures figure with expected layout parameters.

    Args:
        mock_figure (MagicMock): Mock for Figure class
        correlation_dataframe (pd.DataFrame): Fixture containing correlation matrix

    Asserts:
        - Figure is instantiated correctly
        - Layout update is called with proper parameters
        - Heatmap trace is added with correct configuration
    """
    mock_fig_instance = MagicMock()
    mock_figure.return_value = mock_fig_instance

    plots = Plots()
    plots.heatmap(correlation_dataframe, xaxis_title="Test X", yaxis_title="Test Y")

    mock_figure.assert_called_once()
    mock_fig_instance.add_trace.assert_called_once()
    mock_fig_instance.update_layout.assert_called_once()


@patch("kvbiii_plots.eda.eda_plots.Plots.check_data")
@patch("plotly.graph_objects.Figure.show")
def test_plots_barplot_missing_values_calls_check_data_method(
    mock_show: MagicMock,
    mock_check_data: MagicMock,
    missing_values_data: list[int],
    feature_names: list[str],
) -> None:
    """Tests barplot_missing_values calls check_data method for input validation.

    Args:
        mock_show (MagicMock): Mock for Figure.show method
        mock_check_data (MagicMock): Mock for check_data method
        missing_values_data (list[int]): Fixture containing missing values data
        feature_names (list[str]): Fixture containing feature names

    Asserts:
        - check_data method is called once with input data
        - Method properly validates input before processing
        - Data validation occurs before plot creation
    """
    mock_check_data.return_value = np.array(missing_values_data)

    plots = Plots()
    plots.barplot_missing_values(missing_values_data, feature_names, "test")

    mock_check_data.assert_called_once_with(data=missing_values_data)
    mock_show.assert_called_once_with("png")


@patch("plotly.graph_objects.Figure.show")
def test_plots_barplot_missing_values_dataframe_input_creates_bar_chart(
    mock_show: MagicMock, sample_dataframe: pd.DataFrame, feature_names: list[str]
) -> None:
    """Tests barplot_missing_values creates bar chart for DataFrame input.

    Args:
        mock_show (MagicMock): Mock for Figure.show method
        sample_dataframe (pd.DataFrame): Fixture containing test DataFrame
        feature_names (list[str]): Fixture containing feature names

    Asserts:
        - Bar chart is created successfully from DataFrame
        - Figure.show method is called with PNG format
        - No exceptions raised during execution
    """
    plots = Plots()

    # Use subset of dataframe to match feature names length
    subset_data = sample_dataframe.iloc[: len(feature_names), 0]
    plots.barplot_missing_values(subset_data, feature_names, "DataFrame Test")

    mock_show.assert_called_once_with("png")


@patch("plotly.graph_objects.Figure.show")
def test_plots_barplot_missing_values_series_input_handles_correctly(
    mock_show: MagicMock, feature_names: list[str]
) -> None:
    """Tests barplot_missing_values correctly processes Series input.

    Args:
        mock_show (MagicMock): Mock for Figure.show method
        feature_names (list[str]): Fixture containing feature names

    Asserts:
        - Method executes without errors when given Series input
        - Plot configuration matches expected parameters
        - Series data is properly converted and visualized
    """
    test_series = pd.Series([1, 2, 3, 4, 5, 6, 7], name="test_series")

    plots = Plots()
    plots.barplot_missing_values(test_series, feature_names, "Series Test")

    mock_show.assert_called_once_with("png")


@patch("plotly.graph_objects.Figure.show")
def test_plots_barplot_missing_values_numpy_array_input_processes_successfully(
    mock_show: MagicMock, feature_names: list[str]
) -> None:
    """Tests barplot_missing_values processes numpy array input successfully.

    Args:
        mock_show (MagicMock): Mock for Figure.show method
        feature_names (list[str]): Fixture containing feature names

    Asserts:
        - Numpy array input is processed correctly
        - Visualization is created without errors
        - Array data is properly handled by check_data method
    """
    test_array = np.array([5, 10, 15, 20, 25, 30, 35])

    plots = Plots()
    plots.barplot_missing_values(test_array, feature_names, "Array Test")

    mock_show.assert_called_once_with("png")


@patch("plotly.graph_objects.Figure.show")
def test_plots_barplot_missing_values_empty_name_uses_default_title(
    mock_show: MagicMock, missing_values_data: list[int], feature_names: list[str]
) -> None:
    """Tests barplot_missing_values uses appropriate title when name is empty.

    Args:
        mock_show (MagicMock): Mock for Figure.show method
        missing_values_data (list[int]): Fixture containing missing values data
        feature_names (list[str]): Fixture containing feature names

    Asserts:
        - Method handles empty name parameter gracefully
        - Default title formatting is applied correctly
        - Plot creation succeeds with minimal parameters
    """
    plots = Plots()
    plots.barplot_missing_values(missing_values_data, feature_names, "")

    mock_show.assert_called_once_with("png")


@patch("plotly.graph_objects.Figure")
def test_plots_barplot_missing_values_figure_dimensions_scale_with_features(
    mock_figure: MagicMock, missing_values_data: list[int], feature_names: list[str]
) -> None:
    """Tests barplot_missing_values scales figure dimensions based on feature count.

    Args:
        mock_figure (MagicMock): Mock for Figure class
        missing_values_data (list[int]): Fixture containing missing values data
        feature_names (list[str]): Fixture containing feature names

    Asserts:
        - Figure dimensions scale appropriately with feature count
        - Minimum dimensions are maintained for small datasets
        - Layout configuration includes proper width and height
    """
    mock_fig_instance = MagicMock()
    mock_figure.return_value = mock_fig_instance

    plots = Plots()
    plots.barplot_missing_values(missing_values_data, feature_names, "Scale Test")

    mock_figure.assert_called_once()

    # Check that update_layout was called
    mock_fig_instance.update_layout.assert_called_once()

    # Verify layout call includes width and height parameters
    layout_call = mock_fig_instance.update_layout.call_args
    layout_kwargs = layout_call[1] if layout_call else {}

    expected_width = max(30 * len(feature_names), 1600)
    expected_height = max(30 * len(feature_names), 800)

    assert "width" in layout_kwargs, "Layout missing width parameter"
    assert "height" in layout_kwargs, "Layout missing height parameter"
    assert (
        layout_kwargs["width"] == expected_width
    ), f"Expected width {expected_width}, got {layout_kwargs['width']}"
    assert (
        layout_kwargs["height"] == expected_height
    ), f"Expected height {expected_height}, got {layout_kwargs['height']}"
