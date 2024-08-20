import json
import os

import numpy as np
from scipy.signal import sawtooth, square
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches


def sample_waveforms():
    # Signal parameters
    frequency = 3 / 120  # Frequency in Hz
    amplitude = 1  # Amplitude
    duration = 120  # Duration in seconds
    sampling_rate = 1000  # Sampling rate in Hz

    # Time array
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    # Generate signals
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)
    cosine_wave = amplitude * np.cos(2 * np.pi * frequency * t)
    # sawtooth_wave = amplitude * sawtooth(2 * np.pi * frequency * t)
    triangular_wave = amplitude * sawtooth(2 * np.pi * frequency * t, width=0.5)
    square_wave = amplitude * square(2 * np.pi * frequency * t)

    # Plot the signals
    plt.figure(figsize=(12, 8))

    plt.subplot(4, 1, 1)
    plt.plot(t, sine_wave)
    plt.title('Sine Wave')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.grid(True)

    plt.subplot(4, 1, 2)
    plt.plot(t, cosine_wave)
    plt.title('Cosine Wave')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.grid(True)

    plt.subplot(4, 1, 3)
    plt.plot(t, triangular_wave)
    plt.title('Triangular Wave')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.grid(True)

    plt.subplot(4, 1, 4)
    plt.plot(t, square_wave)
    plt.title('Square Wave')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def pv_oscillation(amplitude=1.0, frequency=1.0 / 60.0, duration=2.0, sampling_rate=1000):
    """
    :param amplitude: in engineering units
    :param frequency: frequency in Hz
    :param duration: duration of oscillations in seconds
    :param sampling_rate: sampling rate in Hz
    :return:
    """

    # Time array
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    return amplitude * np.sin(2 * np.pi * frequency * t)


def pv_high(amplitude=2.0, frequency=1.0 / 60.0, duration=60, sampling_rate=1000):
    """
    :param amplitude: in engineering units
    :param frequency: frequency in Hz
    :param duration: duration of oscillations in seconds
    :param sampling_rate: sampling rate in Hz
    :return:
    """

    # Time array
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    return amplitude + amplitude * sawtooth(2 * np.pi * frequency * t, width=0.5)


def pv_low(amplitude=2.0, frequency=1.0 / 60.0, duration=60, sampling_rate=1000):
    """
    :param amplitude: in engineering units
    :param frequency: frequency in Hz
    :param duration: duration of oscillations in seconds
    :param sampling_rate: sampling rate in Hz
    :return:
    """

    # Time array
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    return -1 * (amplitude + amplitude * sawtooth(2 * np.pi * frequency * t, width=0.5))


def process_value(amplitude=15.0, duration_fill=45.0, duration_steady=360.0, duration_empty=45.0, sampling_rate=1000,
                  high_threshold=17.0, low_threshold=13.0, high_high_threshold=19.0, low_low_threshold=11.0,
                  high_range=20.0, low_range=0.0, animation=True):
    """

    :param animation: whether animation is desired
    :param amplitude: Amplitude in engineering units
    :param duration_fill: Duration of filling time in seconds
    :param duration_steady: Duration of steady state time in seconds
    :param duration_empty: Duration of emptying time in seconds
    :param sampling_rate: Sampling rate in Hz
    :param low_threshold: low threshold value in engineering units
    :param high_threshold: high threshold value in engineering units
    :param low_low_threshold: low low threshold value in engineering units
    :param high_high_threshold: high high threshold value in engineering units
    :param low_range: low range value in engineering units
    :param high_range: high range value in engineering units
    :return:
    """

    # Time arrays for each phase
    t_fill = np.linspace(0, duration_fill, int(sampling_rate * duration_fill), endpoint=False)
    t_steady = np.linspace(0, duration_steady, int(sampling_rate * duration_steady), endpoint=False)
    t_empty = np.linspace(0, duration_empty, int(sampling_rate * duration_empty), endpoint=False)

    # Generate signals for each phase
    fill_wave = amplitude * (t_fill / duration_fill)  # Ramp-up (filling)
    steady_wave = amplitude * np.ones_like(t_steady)  # Steady state (constant level)
    steady_wave += pv_oscillation(amplitude=0.5,
                                  frequency=1 / 60,
                                  duration=duration_steady,
                                  sampling_rate=sampling_rate)
    steady_wave[60 * sampling_rate:2 * 60 * sampling_rate] += pv_high(amplitude=2,
                                                                      frequency=1 / 60,
                                                                      duration=60,
                                                                      sampling_rate=sampling_rate)
    steady_wave[4 * 60 * sampling_rate:5 * 60 * sampling_rate] += pv_low(amplitude=2,
                                                                         frequency=1 / 60,
                                                                         duration=60,
                                                                         sampling_rate=sampling_rate)
    empty_wave = amplitude * (1 - t_empty / duration_empty)  # Ramp-down (emptying)

    # Concatenate the phases to form the complete signal
    t_total = np.concatenate((t_fill, t_fill[-1] + t_steady, t_fill[-1] + t_steady[-1] + t_empty))
    waveform = np.concatenate((fill_wave, steady_wave, empty_wave))

    return zip(t_total, waveform)

    # Plot the resulting waveform
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title('Simulated Tank Level Process')
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Level [ft]')
    ax.grid(True)

    ax.axhline(y=high_range, color='red', linestyle='--', label='High Threshold')
    ax.fill_between(t_total, high_range, high_high_threshold, color='red', alpha=0.2, label='High High Band')
    ax.axhline(y=high_high_threshold, color='red', linestyle='--', label='High Threshold')
    ax.fill_between(t_total, high_high_threshold, high_threshold, color='yellow', alpha=0.2, label='High Band')
    ax.axhline(y=high_threshold, color='red', linestyle='--', label='High Threshold')
    ax.fill_between(t_total, high_threshold, low_threshold, color='green', alpha=0.2, label='Control Band')
    ax.plot(t_total, waveform, color='black', alpha=0.2)
    ax.axhline(y=low_threshold, color='red', linestyle='--', label='Low Threshold')
    ax.fill_between(t_total, low_threshold, low_low_threshold, color='yellow', alpha=0.2, label='Low Band')
    ax.axhline(y=low_low_threshold, color='red', linestyle='--', label='Low Threshold')
    ax.fill_between(t_total, low_low_threshold, low_range, color='red', alpha=0.2, label='Low Low Band')
    ax.axhline(y=low_range, color='red', linestyle='--', label='Low Threshold')

    # Initialize the line and circle to be updated
    line, = ax.plot([], [], label='Tank Level')
    # circle = patches.Circle((0, 0), radius=0.5, color='blue')
    #
    # # Add the circle to the axis
    # ax.add_patch(circle)
    #
    # # Initialize the plot
    # def init():
    #     line.set_data([], [])
    #     circle.set_center((0, 0))
    #     return line, circle
    #
    # # Animation function
    # def animate(i):
    #     line.set_data(t_total[:i], waveform[:i])
    #     circle.set_center((t_total[i], waveform[i]))
    #     return line, circle
    #
    # # Create the animation
    # ani = FuncAnimation(fig, animate, frames=len(t_total), init_func=init, blit=True, interval=1)

    plt.legend(loc='lower center', ncol=2)
    plt.show()


def compute_signals(filepath=None, plot_signals=True):
    """
    Procedurally generates simulated signals as specified in level_config.json, and optionally plots them.
    Returns a list of dicts of each signal, containing the total time and waveform for each signal.

    :param filepath: Optional String containing the file path to the level_config.json file. "level_config.json" by default.
    :param plot_signals: Optional Boolean that indicates whether to plot the signals in addition to computing.
    :return:

    Dependencies:
    level_config.json:       Core JSON file specifying the signals to be computed.  See the JSON for notation.
    matplotlib.pyplot:  Core library for plotting the computed signals.
    json:               Core library for managing JSON file content.
    numpy (as np):      Core library for linear space math.
    """
    # Open the level_config.json file and convert to python dict named "signals"
    with open(filepath, "r") as jsonfile:
        signals = json.load(jsonfile)

        # Initialize/Reset the return list
        output = []

        # Main computing block, loops through each signal key in the "signals" dict
        for signal in signals:
            # Assign signal metadata to variables for use in plotting the graph & wave functions
            signal_name = signal
            signal_unit = signals[signal]["unit"]
            high_threshold = signals[signal]["high_threshold"]
            high_high_threshold = signals[signal]["high_high_threshold"]
            low_threshold = signals[signal]["low_threshold"]
            low_low_threshold = signals[signal]["low_low_threshold"]
            high_limit = signals[signal]["high_limit"]
            low_limit = signals[signal]["low_limit"]
            sampling_rate = signals[signal]["sampling_rate"]

            # Reset the arrays between each signal computation:
            total_wave_array = []
            total_duration_array = []

            # Signal segment computing block
            for segment in signals[signal]["segments"]:
                if len(total_wave_array) == 0:
                    previous_wave_value = 0
                else:
                    previous_wave_value = total_wave_array[-1]

                # Compute duration array
                duration = segment["duration"]  # Every segment in the JSON should have the "duration" parameter
                segment_duration_array = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
                if len(total_duration_array) == 0:
                    total_duration_array = segment_duration_array
                else:
                    total_duration_array = np.concatenate((total_duration_array,
                                                           total_duration_array[-1] + segment_duration_array))
                # Compute waveform array
                segment_type = segment["type"]
                if segment_type == "ramp_up":
                    rate = segment["rate"]
                    segment_wave_array = (rate * (segment_duration_array / duration)) + previous_wave_value

                elif segment_type == "ramp_down":
                    rate = segment["rate"]
                    segment_wave_array = previous_wave_value - (rate * (segment_duration_array / duration))

                elif segment_type == "steady":
                    segment_wave_array = previous_wave_value * np.ones_like(segment_duration_array)

                elif segment_type == "oscillate":
                    amplitude = segment["amplitude"]
                    frequency = segment["frequency"]
                    segment_wave_array = previous_wave_value * np.ones_like(segment_duration_array)
                    segment_wave_array += pv_oscillation(amplitude=amplitude,
                                                         frequency=frequency,
                                                         duration=duration,
                                                         sampling_rate=sampling_rate)

                else:
                    raise TypeError("segment name not supported: ", segment)

                if len(total_wave_array) == 0:
                    total_wave_array = segment_wave_array
                else:
                    total_wave_array = np.concatenate((total_wave_array, segment_wave_array))

            # Construct the dictionary of computed arrays for the signal and append to the output
            computed_dict = {
                "signal_name": signal_name,
                "time_array": total_duration_array,
                "wave_array": total_wave_array
            }
            output.append(computed_dict)

            # Optional graph plotting block
            if plot_signals:
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.set_title(('Simulated Signal for ' + str(signal_name)))
                ax.set_xlabel('Time [s]')
                ax.set_ylabel(signal_unit)
                ax.grid(True)

                ax.axhline(y=high_limit,
                           color='red',
                           linestyle='--',
                           label='High Threshold')
                ax.fill_between(total_duration_array, high_limit, high_high_threshold,
                                color='red',
                                alpha=0.2,
                                label='High High Band')
                ax.axhline(y=high_high_threshold,
                           color='red',
                           linestyle='--',
                           label='High Threshold')
                ax.fill_between(total_duration_array, high_high_threshold, high_threshold,
                                color='yellow',
                                alpha=0.2,
                                label='High Band')
                ax.axhline(y=high_threshold,
                           color='red',
                           linestyle='--',
                           label='High Threshold')
                ax.fill_between(total_duration_array, high_threshold, low_threshold,
                                color='green',
                                alpha=0.2,
                                label='Control Band')
                ax.plot(total_duration_array, total_wave_array,
                        color='black',
                        alpha=0.8)
                ax.axhline(y=low_threshold,
                           color='red',
                           linestyle='--',
                           label='Low Threshold')
                ax.fill_between(total_duration_array, low_threshold, low_low_threshold,
                                color='yellow',
                                alpha=0.2,
                                label='Low Band')
                ax.axhline(y=low_low_threshold,
                           color='red',
                           linestyle='--',
                           label='Low Threshold')
                ax.fill_between(total_duration_array, low_low_threshold, low_limit,
                                color='red',
                                alpha=0.2,
                                label='Low Low Band')
                ax.axhline(y=low_limit,
                           color='red',
                           linestyle='--',
                           label='Low Threshold')

                plt.legend(loc='lower center', ncol=2)
                plt.show()

        # Return the list of computed signals
        return output


def compute_pv(filepath=None):
    # Load configuration from JSON file
    with open(filepath, 'r') as f:
        print(f"Opening json file: '{filepath}'")
        config = json.load(f)

    # Extract signal name, description, and unit
    name = config['name']
    description = config['description']
    unit = config['unit']

    # Extract segment parameters from JSON
    segments = config['segments']

    # Initialize lists to store time arrays and waveform segments
    time_arrays = []
    waveform_segments = []
    total_duration = 0

    # Generate time arrays and waveform segments dynamically
    for segment_name, params in segments.items():
        duration = params['duration']
        sampling_rate = params['sampling_rate']
        offset = params['offset']
        amplitude = params['amplitude']
        noise = params['noise']

        t = np.linspace(total_duration, total_duration + duration, int(sampling_rate * duration), endpoint=False)
        if "ramp" in segment_name:
            wave = offset + amplitude * (t - total_duration) / duration + noise * np.random.randn(len(t))
        elif "steady" in segment_name:
            wave = offset + amplitude * np.ones_like(t) + noise * np.random.randn(len(t))
        elif "sine" in segment_name:
            frequency = 2 * 1 / 60  # 2 cycles per minute
            wave = offset + amplitude * np.sin(2 * np.pi * frequency * t) + noise * np.random.randn(len(t))
        else:
            wave = offset + amplitude * np.ones_like(t) + noise * np.random.randn(len(t))

        total_duration += duration
        time_arrays.append(t)
        waveform_segments.append(wave)

    # Concatenate the segments to form the complete time array and waveform
    t_total = np.concatenate(time_arrays)
    waveform = np.concatenate(waveform_segments)

    return name, description, unit, zip(t_total, waveform)


def compute_pv_dict(filepath=None):
    # init data result
    data = {}

    # Load configuration from JSON file
    with open(filepath, 'r') as f:
        print(f"Opening json file: '{filepath}'")
        config = json.load(f)

    # Extract signal name, description, and unit
    data.update({'name': config['name']})
    data.update({'description': config['description']})
    data.update({'unit': config['unit']})

    # Extract segment parameters from JSON
    segments = config['segments']

    # Initialize lists to store time arrays and waveform segments
    time_arrays = []
    waveform_segments = []
    total_duration = 0

    # Generate time arrays and waveform segments dynamically
    for segment_name, params in segments.items():
        duration = params['duration']
        sampling_rate = params['sampling_rate']
        offset = params['offset']
        amplitude = params['amplitude']
        noise = params['noise']

        t = np.linspace(total_duration, total_duration + duration, int(sampling_rate * duration), endpoint=False)

        if "ramp" in segment_name:
            wave = offset + amplitude * (t - total_duration) / duration + noise * np.random.randn(len(t))
        elif "steady" in segment_name:
            wave = offset + amplitude * np.ones_like(t) + noise * np.random.randn(len(t))
        elif "sine" in segment_name:
            frequency = 1 / 60  # 1 cycles per minute
            wave = offset + amplitude * np.sin(2 * np.pi * frequency * t) + noise * np.random.randn(len(t))
        else:
            wave = offset + amplitude * np.ones_like(t) + noise * np.random.randn(len(t))

        total_duration += duration
        time_arrays.append(t)
        waveform_segments.append(wave)

    # Concatenate the segments to form the complete time array and waveform
    t_total = np.concatenate(time_arrays)
    data.update({'idx': t_total})
    waveform = np.concatenate(waveform_segments)
    data.update({'waveform': waveform})

    return data
