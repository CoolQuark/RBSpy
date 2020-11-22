
import matplotlib.pyplot as plt
import numpy as np

from RBSpy import rbsSpectra
import RBSpy.rbsAux as raux


class multi_rbs():
    def __init__(self, file_path_array, type_file = 'exp', offset = 90, **kwarg):
        self.file_path_array = file_path_array
        self.type_file = type_file
        self.offset = offset
        self.rbs_files = load_multiple(file_path_array, type_file, offset)
        self.shape = len(self.rbs_files)

    def create_fig(self, xlim = [200, 1650], ylim=[-0.1, 2.5], title = '', fig_size=[6, 4]):
        self.fig, self.ax = raux.create_figure (xlim, ylim, title, fig_size)
        return self.fig, self.ax

    def plot(self, ax = None, rbs =None, line_style = '-', normal_id = 1, normal = 1, reset_color = False, x_offset = 0, colors = None,params_rand={}, **kwargs):
        if ax is None:
            ax = self.ax
        else:
            self.ax = ax
        if rbs is None:
            plot_multiple(ax, self.rbs_files,  line_style=line_style, normal_id=normal_id, normal=normal, reset_color=reset_color, x_offset=x_offset, colors = colors, params_rand=params_rand,**kwargs)
        else:
            plot_multiple(ax, rbs.rbs_files,  line_style=line_style, normal_id=normal_id, normal=normal, reset_color=reset_color, x_offset=x_offset, colors = colors, params_rand=params_rand,**kwargs)

    def add_label(self, ax=None, label='Simulations', line_style='', marker='', markersize=1.5, color=(0.3,0.3,0.3), ncol=2): 
        if ax is None:
            ax = self.ax
        else:
            self.ax = ax     

        line_add = ax.plot([],[], linestyle=line_style, marker=marker, markersize=markersize, color=color, label=label)[0]
          

    def modify_simulation_delay(self, rand, align, line):
        self.modify_data(rand/align, line)
        print('Scalling factor: %0.3f'%(rand/align))
    def modify_data(self, factor, line): 
        rbsSims = self.rbs_files
        print(rbsSims[line].name)
        energy = rbsSims[line].get_spectra_normalized().Energy
        counts = rbsSims[line].get_spectra_normalized().Counts
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
            spectra.append(self.rbs_files[i].get_spectra_normalized())
            
        
        average_counts = spectra[0]
        average_counts.Counts *= weights[0]
        for w,s in zip(weights[1:], spectra[1:]):
            average_counts.Counts += s.Counts * w
        average_counts.Counts/=sum(weights)
        
        return average_counts



def load_multiple (file_path_array, type_file = 'exp', offset = 90):
    rbs = []
    for p in file_path_array:
        rbs.append(rbsSpectra(p[0], type_file=type_file))
        rbs[-1].set_name(p[2])
        rbs[-1].add_random(rbsSpectra(p[1], type_file=type_file))
        if 'exp' in type_file:
            rbs[-1].calibrate_from_file()
        rbs[-1].renormalization(offset = offset)
    return rbs

   

def plot_multiple (ax, rbs, normal_id = 1, normal = 1, x_offset = 0, line_style = '-', reset_color = False, colors = None, params_rand={}, **kwargs):
    #should remove line_style since now it can come in kwargs via linestyle

    if reset_color: ax.set_prop_cycle(None)
    if colors is not None:
        color_cycle = iter(colors)

    for i,rb in enumerate(rbs):
        if colors is None:
            color=next(ax._get_lines.prop_cycler)['color']
        else:
            color = next(color_cycle)


        sp = rb.get_spectra_normalized()
        spR = rb.get_spectra_random()
        #spName = rb.path.split('/')[6].split('_')[-1]

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



# Averages
def average(si, do):
    situation = [si, do, 1 - si - do]
    print('ndo : %.2f' %situation[2])
    counts = 0
    
    for r,n in zip(rbsSims, situation):
        energy = r.get_spectra_normalized().Energy
        counts += n * r.get_spectra_normalized().Counts
        
    return energy, counts

def plot_average(ax, energy, counts):
    ax.plot(energy, counts, '-.', color = '0.3', label = 'average')
    ax.legend()
    
def ave_interact(si, do):
    situation = [si, do, aux * (1 - si - do)]
    print('ndo : %.2f' %situation[2])
    
    counts = 0
    for r,n in zip(rbsSims, situation):
        energy = r.get_spectra_normalized().Energy
        counts += n * r.get_spectra_normalized().Counts
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

