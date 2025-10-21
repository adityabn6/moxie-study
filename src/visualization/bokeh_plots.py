"""
Interactive Bokeh visualizations for MOXIE physiological data.

Creates interactive HTML plots with quality overlays and time window annotations.
"""

import os
import numpy as np
from pathlib import Path
from typing import List, Optional
from bokeh.plotting import figure, output_file, save
from bokeh.models import Range1d, BoxAnnotation, Label, RangeSlider, CustomJS
from bokeh.layouts import column
from bokeh.palettes import Category20

from core.data_models import BioData
from core.config import VISUALIZATION_PARAMS


# Global color palette
COLOR_PALETTE = Category20[20]
COLOR_INDEX = 0


def color_picker() -> str:
    """Get next color from palette (cycles through)."""
    global COLOR_INDEX
    color = COLOR_PALETTE[COLOR_INDEX % len(COLOR_PALETTE)]
    COLOR_INDEX += 1
    return color


def save_bokeh_plot(
    biodata: BioData,
    filename: str,
    sampling_rates: List[float],
    channel_names: List[str],
    plot_width: int = 800,
    plot_height: int = 300
) -> None:
    """
    Create interactive Bokeh plot with quality overlays.

    Args:
        biodata: BioData object with channels and quality metrics
        filename: Output HTML file path
        sampling_rates: List of sampling rates for downsampling each channel
        channel_names: List of channel names to plot
        plot_width: Width of each plot in pixels
        plot_height: Height of each plot in pixels
    """
    # Create shared x-axis range
    shared_x_range = Range1d(start=0, end=biodata.end_time)

    # Create range slider for navigation
    range_slider = RangeSlider(
        start=0,
        end=biodata.end_time,
        value=(0, min(100, biodata.end_time)),
        step=5,
        title="Time Range (seconds)"
    )

    plots = []
    window_colors = VISUALIZATION_PARAMS["color_palette"]

    for idx, channel in enumerate(channel_names):
        if channel not in biodata.ChannelNames:
            print(f"  Warning: {channel} not found, skipping...")
            continue

        # Create figure
        p = figure(
            title=f"{channel} over Time",
            x_axis_label='Time (seconds)',
            y_axis_label=channel,
            width=plot_width,
            height=plot_height,
            x_range=shared_x_range
        )

        # Get and plot main signal
        signal_y, signal_x = biodata.return_downsample_dataframe(
            channel,
            sampling_rates[idx]
        )

        if signal_y is None:
            continue

        p.line(signal_x, signal_y, line_width=1, color=color_picker(), alpha=0.6)

        # Style adjustments
        p.xaxis.axis_label_text_font_size = "12pt"
        p.yaxis.axis_label_text_font_size = "12pt"
        p.title.text_font_size = "14pt"

        # Plot SNR quality flags
        snr_feature = biodata.get_snr_feature(channel)
        if snr_feature is not None:
            # Get time vector for SNR
            for data_obj in biodata.Data:
                if data_obj.name == channel:
                    snr_time = data_obj.time_column
                    break

            # Find flagged times
            flag_times = snr_time[snr_feature == 1]
            if len(flag_times) > 0:
                flag_x, flag_y = [], []
                for t in flag_times:
                    idx_closest = np.argmin(np.abs(signal_x - t))
                    flag_x.append(signal_x[idx_closest])
                    flag_y.append(signal_y[idx_closest])

                # Add markers above signal
                offset = 0.03 * np.ptp(signal_y)
                p.triangle(
                    flag_x,
                    np.array(flag_y) + offset,
                    size=10,
                    color="red",
                    alpha=0.8,
                    legend_label="SNR=1 (poor)"
                )

        # Plot amplitude quality flags
        amplitude_feature = biodata.get_amplitude_feature(channel)
        if amplitude_feature is not None:
            # Get time vector for amplitude
            for data_obj in biodata.Data:
                if data_obj.name == channel:
                    amplitude_time = data_obj.time_column
                    break

            # Find flagged times
            flag_times = amplitude_time[amplitude_feature == 1]
            if len(flag_times) > 0:
                flag_x, flag_y = [], []
                for t in flag_times:
                    idx_closest = np.argmin(np.abs(signal_x - t))
                    flag_x.append(signal_x[idx_closest])
                    flag_y.append(signal_y[idx_closest])

                # Add markers above signal
                offset = 0.06 * np.ptp(signal_y)
                p.square(
                    flag_x,
                    np.array(flag_y) + offset,
                    size=10,
                    color="green",
                    alpha=0.8,
                    legend_label="Amplitude=1 (poor)"
                )

        # Draw time windows
        for window_idx, window in enumerate(biodata.Window_List):
            if not window.is_valid():
                continue

            color = window_colors[window_idx % len(window_colors)]

            # Add shaded box
            box = BoxAnnotation(
                left=window.start_time,
                right=window.end_time,
                fill_color=color,
                fill_alpha=0.15,
                line_color='black',
                line_dash='dashed'
            )
            p.add_layout(box)

            # Add label at top
            y_max = signal_y.max()
            label = Label(
                x=(window.start_time + window.end_time) / 2,
                y=y_max * 1.05,
                text=window.name,
                text_align='center',
                text_baseline='top',
                text_font_size='10pt',
                background_fill_color='white',
                background_fill_alpha=0.5
            )
            p.add_layout(label)

        plots.append(p)

    # Link range slider to x-axis
    range_slider.js_link("value", shared_x_range, "start", attr_selector=0)
    range_slider.js_link("value", shared_x_range, "end", attr_selector=1)

    # Create output directory
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save plot
    layout = column(range_slider, *plots)
    output_file(filename)
    save(layout)

    print(f"  Saved: {filename}")


def save_quality_comparison_plot(
    biodata: BioData,
    channel_name: str,
    filename: str
) -> None:
    """
    Create a comparison plot showing signal with SNR and amplitude quality metrics.

    Args:
        biodata: BioData object
        channel_name: Channel to visualize
        filename: Output HTML file path
    """
    if channel_name not in biodata.ChannelNames:
        print(f"Error: Channel '{channel_name}' not found")
        return

    # Shared x-axis
    shared_x_range = Range1d(start=0, end=biodata.end_time)
    plots = []

    # 1. Raw signal
    p1 = figure(
        title=f"{channel_name} - Raw Signal",
        x_axis_label='Time (seconds)',
        y_axis_label='Signal',
        width=800,
        height=250,
        x_range=shared_x_range
    )

    signal_y, signal_x = biodata.get_dataframe(channel_name)
    if signal_y is not None:
        # Downsample for visualization
        downsample_rate = 20
        signal_y_ds, signal_x_ds = biodata.return_downsample_dataframe(
            channel_name,
            downsample_rate
        )
        p1.line(signal_x_ds, signal_y_ds, line_width=1, color="blue", alpha=0.6)
        plots.append(p1)

    # 2. SNR metric
    snr_channel = f"{channel_name}_SNR"
    if snr_channel in biodata.ChannelNames:
        p2 = figure(
            title="SNR (dB)",
            x_axis_label='Time (seconds)',
            y_axis_label='SNR',
            width=800,
            height=200,
            x_range=shared_x_range
        )

        snr_y, snr_x = biodata.get_dataframe(snr_channel)
        p2.line(snr_x, snr_y, line_width=2, color="red")

        # Mark flagged regions
        snr_flags = biodata.get_snr_feature(snr_channel)
        if snr_flags is not None:
            flagged_times = snr_x[snr_flags == 1]
            flagged_values = snr_y[snr_flags == 1]
            p2.circle(flagged_times, flagged_values, size=8, color="red", alpha=0.6)

        plots.append(p2)

    # 3. Amplitude metric
    amp_channel = f"{channel_name}_Amplitude"
    if amp_channel in biodata.ChannelNames:
        p3 = figure(
            title="Amplitude",
            x_axis_label='Time (seconds)',
            y_axis_label='Amplitude',
            width=800,
            height=200,
            x_range=shared_x_range
        )

        amp_y, amp_x = biodata.get_dataframe(amp_channel)
        p3.line(amp_x, amp_y, line_width=2, color="green")

        # Mark flagged regions
        amp_flags = biodata.get_amplitude_feature(amp_channel)
        if amp_flags is not None:
            flagged_times = amp_x[amp_flags == 1]
            flagged_values = amp_y[amp_flags == 1]
            p3.circle(flagged_times, flagged_values, size=8, color="green", alpha=0.6)

        plots.append(p3)

    # Save
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    layout = column(*plots)
    output_file(filename)
    save(layout)

    print(f"  Saved quality comparison: {filename}")


def create_interactive_dashboard(
    biodata: BioData,
    output_dir: Path,
    channels: List[str],
    sampling_rate: float
) -> None:
    """
    Create a complete dashboard with individual channel plots.

    Args:
        biodata: BioData object
        output_dir: Output directory for HTML files
        channels: List of channels to create plots for
        sampling_rate: Sampling rate for downsampling
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating visualizations in: {output_dir}")

    for channel in channels:
        if channel not in biodata.ChannelNames:
            continue

        # Create individual plot
        safe_channel_name = channel.replace(" ", "_").replace(",", "")
        filename = output_dir / f"{safe_channel_name}.html"

        save_bokeh_plot(
            biodata=biodata,
            filename=str(filename),
            sampling_rates=[sampling_rate],
            channel_names=[channel]
        )

    print(f"Dashboard created with {len(channels)} plots\n")
