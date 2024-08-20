import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random


class RealTimePlot:
    def __init__(self, no_of_lines=9):
        self.x_data = []
        self.y_data = [[] for _ in range(no_of_lines)]  # List of 9 lists for 9 lines
        self.fig, self.axs = plt.subplots(no_of_lines, 1)
        self.lines = []

        # Initialize each line in the corresponding subplot
        for i, ax in enumerate(self.axs.flat):
            line, = ax.plot([], [], label=f'Variable {i + 1}')
            ax.set_xlabel('Time')
            # ax.set_ylabel('Values')
            ax.legend()
            self.lines.append(line)

    def init_plot(self):
        for ax in self.axs.flat:
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 100)
        for line in self.lines:
            line.set_data([], [])
        return self.lines

    def update_plot(self, frame,x,y):
        new_time = x
        self.x_data.append(new_time)

        # Generate new data points and update each line
        for i in range(9):
            # new_y = random.randint(0, 100)
            self.y_data[i].append(y[i])
            self.lines[i].set_data(self.x_data, self.y_data[i])
            self.axs.flat[i].set_xlim(0, max(10, new_time))
            self.axs.flat[i].set_ylim(0, max(100, max(self.y_data[i])))

        return self.lines

    def animate(self, x,y):
        ani = FuncAnimation(self.fig, self.update_plot, init_func=self.init_plot, fargs=(x,y), interval=1000,
                            blit=True, cache_frame_data=False)
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    plotter = RealTimePlot()
    plotter.animate()
