import matplotlib.pyplot as plt
import numpy as np

import sys
import os
#sys.path.insert(0, '/home/msequeira/Software/python/rbsSpectra')
from rbsSpectra import rbsSpectra
#import pandas as pd


class multi_rbs():
    def __init__(self, filePathArray, type_file = 'sim', offset = 300, **kwarg):
        self.filePathArray = filePathArray
        self.type_file = type_file
        self.offset = offset
        self.rbs_files = loadMultiple(filePathArray, type_file, offset)
        self.shape = len(self.rbs_files)

    def create_fig(self, xlim = [200, 1650], ylim=[-0.1, 2.5], title = '', fig_size=[10, 7]):
        self.fig, self.ax = createFigure (xlim, ylim, title, fig_size)
        return self.fig, self.ax

    def plot(self, ax = None, rbs =None, line_style = '-', normal_id = 1, normal = 1, reset_color = False, x_offset = 0, colors = None,params_rand={}, **kwargs):
        if ax is None:
            ax = self.ax
        else:
            self.ax = ax
        if rbs is None:
            printMultile(ax, self.rbs_files,  line_style=line_style, normal_id=normal_id, normal=normal, reset_color=reset_color, x_offset=x_offset, colors = colors, params_rand=params_rand,**kwargs)
        else:
            printMultile(ax, rbs.rbs_files,  line_style=line_style, normal_id=normal_id, normal=normal, reset_color=reset_color, x_offset=x_offset, colors = colors, params_rand=params_rand,**kwargs)

    def add_label(self, ax=None, label='Simulations', line_style='', marker='', markersize=1.5, color=(0.3,0.3,0.3), ncol=2): 
        if ax is None:
            ax = self.ax
        else:
            self.ax = ax     

        line_add = ax.plot([],[], linestyle=line_style, marker=marker, markersize=markersize, color=color, label=label)[0]
          
        # handles, labels = ax.get_legend_handles_labels()
        # handles.append(plt.plot([],[], linestyle = line_style, marker=marker, color=color)[0])
        # labels.append(label)
        # ax.legend(ncol=ncol, markerscale=markerscale, frameon=frameon)

    def modify_simulation_delay(self, rand, align, line):
        self.modify_data(rand/align, line)
    def modify_data(self, factor, line): 
        rbsSims = self.rbs_files
        print(rbsSims[line].name)
        energy = rbsSims[line].getSpectraNormalized().Energy
        counts = rbsSims[line].getSpectraNormalized().Counts
        new = counts*factor

        for i, t in enumerate(self.ax.legend_.texts):
            if t.get_text() in self.rbs_files[line].name:
                line_ax = i
                break
        self.ax.lines[line_ax*2].set_data(energy, new)
        print(line)

    def plot_average(self, ax=None, indexes = None, weights=None, **kwargs):
        average_counts = self.average(indexes, weights=weights)
        
        if ax is None:
            ax = plt.gca()    
        ax.plot(average_counts.Energy, average_counts.Counts, **kwargs)
        
        return average_counts

    def save_average(self, path, indexes = None, weights=None, **kwargs):
        average_counts = self.average(indexes, weights=weights)
        np.save_average(path, average_counts)
        print('File Saved')
        

    def average(self, indexes = None,  weights=None):
        if indexes is None:
            indexes = range(0, len(self.rbs_files))
        if weights is None:
            weights = [1]*len(indexes)
        spectra = []
        for i in indexes:
            spectra.append(self.rbs_files[i].getSpectraNormalized())
            
        
        average_counts = spectra[0]
        average_counts.Counts *= weights[0]
        for w,s in zip(weights[1:], spectra[1:]):
            average_counts.Counts += s.Counts * w
        average_counts.Counts/=sum(weights)
        
        return average_counts



def loadMultiple (filePathArray, type_file = 'sim', offset = 300):
    rbs = []
    for p in filePathArray:
        rbs.append(rbsSpectra(p[0], type_file=type_file))
        rbs[-1].setName(p[2])
        rbs[-1].addRandom(rbsSpectra(p[1], type_file=type_file))
        if 'exp' in type_file:
            rbs[-1].calibrate_from_file()
        rbs[-1].renormalization(offset = offset)
    return rbs

def createFigure (xlim = [200, 1650], ylim=[-0.1, 2.5], title = '', fig_size=[10, 7]):
    fig, ax = plt.subplots()
    fig.set_size_inches(*fig_size)#(10,5.7)
    fig.subplots_adjust(top = 0.85, bottom = 0.10)
    ax.set_title(title, y=1.12)

    
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_ylim(ylim[0], ylim[1])

    #ax.legend()#bbox_to_anchor=(1.1, 1.05) 
    ax.set_xlabel('Energy (keV)')
    ax.set_ylabel('Yield (arb. units)')

    
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
    

def printMultile (ax, rbs, normal_id = 1, normal = 1, x_offset = 0, line_style = '-', reset_color = False, colors = None, params_rand={}, **kwargs):
    #should remove line_style since now it can come in kwargs via linestyle

    if reset_color: ax.set_prop_cycle(None)
    if colors is not None:
        color_cycle = iter(colors)

    for i,rb in enumerate(rbs):
        if colors is None:
            color=next(ax._get_lines.prop_cycler)['color']
        else:
            color = next(color_cycle)


        sp = rb.getSpectraNormalized()
        spR = rb.getSpectraRandom()
        spName = rb.path.split('/')[6].split('_')[-1]

        if normal_id != 1: normal = sp.Counts[normal_id]  

        ax.plot(sp.Energy + x_offset, sp.Counts/normal, line_style, color=color, label = rb.name, **kwargs)

        if 'random_id' in params_rand.keys():
            random_id = params_rand.get('random_id', None)
            line_style_rand = params_rand.get('marker', line_style)
            color_rand = params_rand.get('color', color)
            label_rand = params_rand.get('label', '_nolegend_')

            if i == random_id:
                ax.plot(spR.Energy + x_offset, spR.Counts, line_style_rand,  color=color_rand, label = label_rand, **kwargs)
        else:
            ax.plot(spR.Energy + x_offset, spR.Counts, line_style,  color=color, label = '_nolegend_', **kwargs)

        ax.legend()
    return ax

def depth2energy(y):
    return (y*1e-3 - 1.80561932)/-0.00112370

def energy2depth(x):
    return (-0.00112370 * x + 1.80561932)*1e3


# Averages
def average(si, do):
    situation = [si, do, 1 - si - do]
    print('ndo : %.2f' %situation[2])
    counts = 0
    
    for r,n in zip(rbsSims, situation):
        energy = r.getSpectraNormalized().Energy
        counts += n * r.getSpectraNormalized().Counts
        
    return energy, counts

def plot_average(ax, energy, counts):
    ax.plot(energy, counts, '-.', color = '0.3', label = 'average')
    ax.legend()
    
def ave_interact(si, do):
    situation = [si, do, aux * (1 - si - do)]
    print('ndo : %.2f' %situation[2])
    
    counts = 0
    for r,n in zip(rbsSims, situation):
        energy = r.getSpectraNormalized().Energy
        counts += n * r.getSpectraNormalized().Counts
    ax.lines[-1].set_data(energy, counts)
    
def remove_virgin(rbs, ni):
    as_grown_path = [['/home/msequeira/Software/RBSADEC/ShuoSimulation/AsGrown/out/rbsspectra.dat',
        '/home/msequeira/Software/RBSADEC/ShuoSimulation/AsGrown/random/out/rbsspectra.dat',
    'Sim As Grown']]
    
    as_grown = loadMultiple (as_grown_path, offset=200)

    energy = rbs.getSpectraNormalized().Energy
    counts = (rbs.getSpectraNormalized().Counts - ni * as_grown[0].getSpectraNormalized().Counts)/(1-ni)
    situation = [1 - ni, ni]
    ax.lines[-1].set_data(energy, counts)
    
    
def side_len(fluence, n_ions):
    lx = np.sqrt(n_ions/fluence)
    return lx * 1e8
    
def percent_as_grown(fluence1, fluence2):
    n = 1

    area1 = side_len(fluence1, n)**2
    area2 = side_len(fluence2, n)**2

    p1 = area1/area2
    p_asgrown = 1 - p1
    return p_asgrown

def add_virgin(rbs, ni, type_file = 'sim', ax = None, label = None, **kwargs):
    if 'sim' in type_file:
        as_grown_path = [['/home/msequeira/Software/RBSADEC/ShuoSimulation/AsGrown/out/rbsspectra.dat',
            '/home/msequeira/Software/RBSADEC/ShuoSimulation/AsGrown/random/out/rbsspectra.dat',
        'Sim As Grown']]
    else:
        as_grown_path = [['/media/msequeira/HDD/Dropbox/CTN/QWs SHI/RBS/AussieAu Samples/GaN A/RBS1_cGAN_AuAu_AsGrown_Align.odf',
         '/media/msequeira/HDD/Dropbox/CTN/QWs SHI/RBS/AussieAu Samples/GaN A/RBS1_cGAN_AuAu_AsGrown_Random.odf',
         'Exp As Grown']]
    
    as_grown = loadMultiple (as_grown_path,type_file=type_file, offset=200)

    energy = rbs.getSpectraNormalized().Energy
    counts = rbs.getSpectraNormalized().Counts*(1-ni) + ni * as_grown[0].getSpectraNormalized().Counts
    #situation = [1 - ni, ni]
    if label is None:
        label = '%s + as grown' %rbs.name
    if ax is not None:
        if 'linestyle' not in kwargs.keys():
            kwargs['linestyle'] = '-.'
        ax.plot(energy, counts, label = label, **kwargs)
        ax.legend()
        
    return energy, counts


# def modify_simulation_delay(rand, align, line):
#     modify_data(rand/align, line)
# def modify_data(factor, line):    
#     print(rbsSims[line].name)
#     energy = rbsSims[line].getSpectraNormalized().Energy
#     counts = rbsSims[line].getSpectraNormalized().Counts
#     new = counts*factor
#     ax.lines[line*2].set_data(energy, new)
#     print(line)


def update_plot_lines(**kwargs):
    ax = plt.gcf().axes[0]
    list_lines = []
    for l in ax.legend().texts:
        list_lines.append(kwargs[l.get_text()])
        list_lines.append(kwargs[l.get_text() + ' random'])
    
    print(list_lines)
    hide_line(ax, list_lines)
    
def hide_line(ax,list_lines):
    for l, i in zip(ax.lines, list_lines):
        l.set_visible(i)

def hide_line_interact():
    lines_names = []
    for l in ax.legend().texts:
        text = l.get_text()
        lines_names.append(text + ' random')
        lines_names.append(text)

    chk1 = [Checkbox(description=a, value=True) for a in lines_names]
    dic = {c.description: c.value for c in chk1}

    interact(update_plot_lines,  **dic);


def combine_multiple_sims(rbsSims, percentage):
    energy = rbsSims[0].getSpectraNormalized().Energy
    counts = np.zeros(energy.shape)
    for p,r in zip(percentage, rbsSims):
        counts += p * r.getSpectraNormalized().Counts 

    return energy, counts
