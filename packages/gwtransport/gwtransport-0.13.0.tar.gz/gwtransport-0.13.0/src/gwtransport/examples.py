"""
Example data generation for groundwater transport modeling.

This module provides utilities to generate synthetic temperature and flow data
for demonstrating and testing groundwater transport models. It was separated
from the utils module to resolve circular import dependencies.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from gwtransport.advection import gamma_infiltration_to_extraction
from gwtransport.gamma import mean_std_to_alpha_beta
from gwtransport.utils import compute_time_edges, get_soil_temperature


def generate_example_data(
    *,
    date_start="2020-01-01",
    date_end="2021-12-31",
    date_freq="D",
    flow_mean=100.0,  # m3/day
    flow_amplitude=30.0,  # m3/day
    flow_noise=10.0,  # m3/day
    temp_infiltration_method="synthetic",  # Method for generating infiltration temperature
    temp_infiltration_mean=12.0,  # °C
    temp_infiltration_amplitude=8.0,  # °C
    temp_infiltration_noise=1.0,  # °C
    aquifer_pore_volume_gamma_mean=1000.0,  # m3
    aquifer_pore_volume_gamma_std=200.0,  # m3
    retardation_factor=1.0,
):
    """
    Generate synthetic temperature and flow data for groundwater transport examples.

    Parameters
    ----------
    date_start : str, default "2020-01-01"
        Start date for the time series in 'YYYY-MM-DD' format
    date_end : str, default "2021-12-31"
        End date for the time series in 'YYYY-MM-DD' format
    date_freq : str, default "D"
        Frequency for the time series (pandas frequency string)
    flow_mean : float, default 100.0
        Mean flow rate in m3/day
    flow_amplitude : float, default 30.0
        Seasonal amplitude of flow rate in m3/day
    flow_noise : float, default 10.0
        Random noise level for flow rate in m3/day
    temp_infiltration_method : str, default "synthetic"
        Method for generating infiltration temperature. Options:
        - "synthetic": Seasonal pattern with random noise
        - "constant": Constant temperature equal to temp_infiltration_mean
        - "soil_temperature": Use real soil temperature data from KNMI station
    temp_infiltration_mean : float, default 12.0
        Mean temperature of infiltrating water in °C
    temp_infiltration_amplitude : float, default 8.0
        Seasonal amplitude of infiltration temperature in °C (only used for "synthetic" method)
    temp_infiltration_noise : float, default 1.0
        Random noise level for infiltration temperature in °C (only used for "synthetic" method)
    aquifer_pore_volume_gamma_mean : float, default 1000.0
        Mean pore volume of the aquifer gamma distribution in m3
    aquifer_pore_volume_gamma_std : float, default 200.0
        Standard deviation of aquifer pore volume gamma distribution in m3
    retardation_factor : float, default 1.0
        Retardation factor for temperature transport

    Returns
    -------
    tuple
        A tuple containing:
        - pandas.DataFrame: DataFrame with columns 'flow', 'temp_infiltration', 'temp_extraction'
          and metadata attributes for the aquifer parameters
        - pandas.DatetimeIndex: Time edges (tedges) used for the flow calculations

    Raises
    ------
    ValueError
        If temp_infiltration_method is not one of the supported methods
    """
    # Create date range
    dates = pd.date_range(start=date_start, end=date_end, freq=date_freq).tz_localize("UTC")
    days = (dates - dates[0]).days.values

    # Generate flow data with seasonal pattern (higher in winter)
    seasonal_flow = flow_mean + flow_amplitude * np.sin(2 * np.pi * days / 365 + np.pi)
    flow = seasonal_flow + np.random.normal(0, flow_noise, len(dates))
    flow = np.maximum(flow, 5.0)  # Ensure flow is not too small or negative

    min_days_for_spills = 60
    if len(dates) > min_days_for_spills:  # Only add spills for longer time series
        n_spills = np.random.randint(6, 16)
        for _ in range(n_spills):
            spill_start = np.random.randint(0, len(dates) - 30)
            spill_duration = np.random.randint(15, 45)
            spill_magnitude = np.random.uniform(2.0, 5.0)

            flow[spill_start : spill_start + spill_duration] /= spill_magnitude

    # Generate infiltration temperature
    if temp_infiltration_method == "synthetic":
        # Seasonal pattern with noise
        infiltration_temp = temp_infiltration_mean + temp_infiltration_amplitude * np.sin(2 * np.pi * days / 365)
        infiltration_temp += np.random.normal(0, temp_infiltration_noise, len(dates))
    elif temp_infiltration_method == "constant":
        # Constant temperature
        infiltration_temp = np.full(len(dates), temp_infiltration_mean)
    elif temp_infiltration_method == "soil_temperature":
        # Use soil temperature data
        infiltration_temp = (
            get_soil_temperature(
                station_number=260,  # Example station number
                interpolate_missing_values=True,
            )["TB3"]
            .resample(date_freq)
            .mean()[dates]
            .values
        )
    else:
        msg = f"Unknown temperature method: {temp_infiltration_method}"
        raise ValueError(msg)

    # Create data frame
    df = pd.DataFrame(
        data={
            "flow": flow,
            "temp_infiltration": infiltration_temp,
        },
        index=dates,
    )
    # Compute tedges for the flow series
    tedges = compute_time_edges(tedges=None, tstart=None, tend=df.index, number_of_bins=len(df))

    df["temp_extraction"] = gamma_infiltration_to_extraction(
        cin=df["temp_infiltration"],
        flow=df["flow"],
        tedges=tedges,
        cout_tedges=tedges,
        mean=aquifer_pore_volume_gamma_mean,  # Use mean pore volume
        std=aquifer_pore_volume_gamma_std,  # Use standard deviation for heterogeneity
        n_bins=250,  # Discretization resolution
        retardation_factor=retardation_factor,
    )

    # Add some noise to represent measurement errors and other factors
    df["temp_extraction"] += np.random.normal(0, 0.1, len(df))

    # Add some spills (periods with lower extraction temperature due to external factors)
    # Simulate 2-3 spill events of varying duration
    # n_spills = np.random.randint(2, 4)
    # for _ in range(n_spills):
    #     spill_start = np.random.randint(0, len(dates) - 30)
    #     spill_duration = np.random.randint(5, 15)
    #     spill_magnitude = np.random.uniform(2.0, 5.0)
    #     df.iloc[spill_start : spill_start + spill_duration, df.columns.get_loc("temp_extraction")] -= spill_magnitude

    # Add metadata for reference
    alpha, beta = mean_std_to_alpha_beta(mean=aquifer_pore_volume_gamma_mean, std=aquifer_pore_volume_gamma_std)
    df.attrs["aquifer_pore_volume_mean"] = aquifer_pore_volume_gamma_mean
    df.attrs["aquifer_pore_volume_std"] = aquifer_pore_volume_gamma_std
    df.attrs["aquifer_pore_volume_gamma_alpha"] = alpha
    df.attrs["aquifer_pore_volume_gamma_beta"] = beta
    df.attrs["retardation_factor"] = retardation_factor

    return df, tedges
