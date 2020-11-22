import matplotlib.pyplot as plt
import numpy as np

def create_figure (xlim = [200, 1650], ylim=[-0.1, 2.5], title = '', fig_size=[6, 4], depth_scale = True):
    fig, ax = plt.subplots()
    fig.set_size_inches(*fig_size)#(10,5.7)
    fig.subplots_adjust(top = 0.85, bottom = 0.10)
    ax.set_title(title, y=1.12)

    
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_ylim(ylim[0], ylim[1])

    #ax.legend()#bbox_to_anchor=(1.1, 1.05) 
    ax.set_xlabel('Energy (keV)')
    ax.set_ylabel('Yield (arb. units)')

    
    if depth_scale:
        energy_range = np.array(xlim)
        depth_range = energy2depth(energy_range)[::-1]
        depth_values=np.round(np.arange(0, depth_range[1],200), 0)
        depth_text = ['%d'%d for d in depth_values]

        axt = ax.twiny()
        axt.set_xlim(energy_range)
        tick_loc = depth2energy(depth_values)
        axt.set_xticks(tick_loc)
        axt.set_xticklabels(depth_text)
        axt.set_xlabel('Depth (nm)')
        fig.tight_layout()

    return fig, ax


# corrected only for GaN
def depth2energy(y):
    return (y*1e-3 - 1.80561932)/-0.00112370

def energy2depth(x):
    return (-0.00112370 * x + 1.80561932)*1e3