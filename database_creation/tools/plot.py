import matplotlib.pyplot as plt
def plot_layout(title, xlabel, ylabel, ax):

    # FONT ################################
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "Arial",
        'font.size': 10})

    # LABELS ######################################

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # TICKS #######################
    ax.minorticks_on()
    ax.tick_params(axis='x', which='both', bottom=False)
    ax.tick_params(axis='y', which='both', bottom=False)

    # GRIDS ######################

    ax.grid(which='both', axis='y', linestyle='-', linewidth=0.5)
    ax.grid(which='both', axis='x', linestyle='-', linewidth=0.5)

    ax.set_title(title)

