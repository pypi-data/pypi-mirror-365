from pfun_data.utils import get_data_dirpath
import pandas as pd
import pytest
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import importlib
from scipy.stats import ks_2samp

root_path = str(Path(__file__).parents[2])
mod_path = str(Path(__file__).parents[1])
if root_path not in sys.path:
    sys.path.insert(0, root_path)
if mod_path not in sys.path:
    sys.path.insert(0, mod_path)

CMAFitResult = importlib.import_module(
    ".fit", package="pfun_cma_model.engine").CMAFitResult
fit_model = importlib.import_module(
    ".fit", package="pfun_cma_model.engine").fit_model


class TestFitModel:
    # Test that the function returns a CMAFitResult object when given valid input data

    def test_valid_input_returns_CMAFitResult(self):
        """
        Test if valid input returns a CMAFitResult.

        This function tests the behavior of the test_valid_input_returns_CMAFitResult method.
        It checks if the function correctly returns a CMAFitResult object when given valid input.

        Parameters:
            self (object): The instance of the test class.

        Returns:
            None
        """

        data_fpath = str(get_data_dirpath()
                         .joinpath("data", "valid_data.csv"))
        data = pd.read_csv(data_fpath)
        result = fit_model(data)
        # trunk-ignore(bandit/B101)
        assert isinstance(result, CMAFitResult)
        print(result)

    def test_valid_input_produces_sufficient_power(self):
        """
        Test if valid input produces sufficient power.

        This function checks if the valid input produces sufficient power. It performs a statistical test using the `ks_2samp` function from the `scipy.stats` module. The parameters for the test are `out.formatted_data.G` and `out.cma.g_instant`. The result of the test is stored in the variable `res`. The function then asserts that the p-value of the test result is less than or equal to `1e-3`.

        Parameters:
        - self: The instance of the class.

        Returns:
        - None
        """

        data_fpath = str(get_data_dirpath()
                         .joinpath("data", "valid_data.csv"))
        data = pd.read_csv(data_fpath)
        result = fit_model(data)
        res = ks_2samp(result.formatted_data.G,
                       result.cma.g_instant)  # type: ignore
        # trunk-ignore(bandit/B101)
        assert (res.pvalue <= 1e-3)

    def test_json_serialization(self):
        """
        Test if the JSON serialization of the CMAFitResult object works.

        This function tests the behavior of the test_json_serialization method. It checks if the JSON serialization of the CMAFitResult object works.

        Parameters:
        - self: The instance of the class.

        Returns:
        - None
        """
        data_fpath = str(get_data_dirpath()
                         .joinpath("data", "valid_data.csv"))
        data = pd.read_csv(data_fpath)
        result = fit_model(data)
        # trunk-ignore(bandit/B101)
        assert isinstance(result.model_dump_json(), str)
        print(result.model_dump_json())


def interactive_plot():
    """
    Generate an interactive plot using the data from a CSV file.

    The function reads the data from a CSV file located in the "data" directory relative to the current file.
    It then fits a model to the data using the "fit_model" function.
    The resulting model solution is plotted against the time values in the "t" column and the corresponding "G" values in the "G" column.
    The model solution is plotted in red with markers denoted by circles, while the original data points are plotted in blue with markers also denoted by circles.
    The legend is displayed to indicate the meaning of the different markers.

    Returns:
        result (unknown): The result of the fit_model function.
    """
    data_fpath = str(get_data_dirpath()
                     .joinpath("data", "valid_data.csv"))
    data = pd.read_csv(data_fpath)
    result = fit_model(data)
    plt.ion()
    result.soln.plot(x='t', y='G', c='r', linestyle='',
                     marker='o', label='G_soln')
    result.formatted_data['G'].plot(
        c='b', linestyle='', marker='o', label='G_data')
    plt.legend()
    return result
