import os
import numpy as np
import pandas as pd

class rbsSpectra():
    def __init__(self, file_path, type_file='experimental', load_input=False, **kwarg):
        self.path = file_path
        self.type_file = type_file
        self.m = kwarg.get('m', 0)
        self.b = kwarg.get('b', 0)

        self.random = kwarg.get('random', None)
        if self.random != None:
            self.add_random(random)
        
        self.load_file()
        self.set_name()
        if load_input:
            self.get_input()
        
    def load_file(self):
        if self.type_file in 'simulation':
            dataArray = np.loadtxt(self.path)
            self.spectra = pd.DataFrame(data=dataArray, columns=['Energy', 'Counts'])
        elif self.type_file in 'experimental':
            if '.odf' in self.path:
                dataArray = np.loadtxt(self.path)
                self.spectra = pd.DataFrame(data=dataArray, columns=['Channel', 'Counts'])
            elif '.dat' in self.path:
                self.spectra = pd.read_csv(self.path, sep = ",", header=None)
            else:
                print('File not supported')
                return         


            if self.m != 0 or self.b != 0:
                #spectra.columns=['Channel', 'Counts']
                self.set_calibration(m = self.m, b = self.b)
            #else:
                #spectra.columns=['Channel', 'Counts']            
        
        
        
    def get_spectra(self):
        return self.spectra
    
    def set_name(self, name = None):
        if name==None:
            if self.type_file in 'simulation':
                self.name = self.path.split('/')[-3]
            else:
                self.name = self.path.split('/')[-1].split('.')[0]
        else:
            self.name = name
            
    
    def set_calibration(self, m = 2.15, b = 86, **kwarg):
        self.m = m
        if 'spkview' in kwarg.get('spkview', 'None'):
            self.b = -m*b
        else:
            self.b = b
        self.spectra['Energy'] = calibrate(self.m, self.b, self.spectra.Channel)
    

    def get_calibration_file(self, look_subdir = False):
        for root, dirs, files in os.walk(self.get_folder()):
            for file in files:
                if file.endswith(".cal"):
                    self.calibration_file_path = os.path.join(root, file)
                    return self.calibration_file_path
            
            if look_subdir:
                for d in dirs:
                    for file in os.listdir(self.get_folder()+'/'+d):
                        if file.endswith(".cal"):
                            self.calibration_file_path = os.path.join(root,d, file)
                            return self.calibration_file_path
            else:
                break
        return 'No file found'
                    
    def calibrate_from_file(self):
        a = self.get_calibration_file()

        if a == None:
            print('No calibration found for %s' %self.path)
            self.set_calibration()
        else:
            calib = pd.read_csv(a, delimiter= '=', index_col=0, header=None)
            calib[0:2] = calib[0:2].astype(float)
            self.set_calibration(m=calib.loc['m', 1], b=calib.loc['b', 1], spkview=calib.loc['style', 1])
        if self.random != None:
            self.random.calibrate_from_file()

    
    def barrier(self, threshold = 1000, offset = 15):
        ds = self.spectra.loc[self.spectra.Energy>threshold]
        minD = np.gradient(ds.Counts).argmin()
        xValue = ds.iloc[minD, 0] - offset
        closest_in_df = (ds.iloc[:, 0] - xValue).abs().argsort().iloc[0]
        return ds.iloc[closest_in_df]
    
    def add_random(self, random):
        #random is of rbsSpectra type
        self.random = random
        
    def renormalization(self, **kwarg):
        self.renorm = self.random.barrier(**kwarg).Counts
        self.random.renorm = self.renorm
        return self.renorm
    
    def get_spectra_random(self, **kwarg):
        if self.random == None:
            print('No random spectrum added')
        else:
            spectraNormal = self.random.get_spectra().copy()
            spectraNormal.Counts /=self.renorm
            return spectraNormal

    def get_spectra_normalized(self, **kwarg):
        if self.random == None:
            print('No random spectrum added')
        else:
            try:
                renorm = self.renorm
            except:
                renorm = self.renormalization(**kwarg)
            spectraNormal = self.get_spectra().copy()
            spectraNormal.Counts = spectraNormal.Counts/renorm
            return spectraNormal
        
    def get_folder(self):
        if self.type_file in 'simulation':
            self.path_folder = self.path.split('/out/')[0] + '/'
            return self.path_folder
        else:
            self.path_folder = '/'.join(self.path.split('/')[0:-1])
            return self.path_folder
    
    def get_file_name(self):
        self.file_name = self.path.split('/')[-1]
        return self.file_name

    def get_input_path(self):
        if self.type_file in 'simulation':
            self.inputFile = self.get_folder() + 'in/input.dat'
            return self.inputFile
        else:
            print('%s is not a simulation' %self.name)

    def parse_input_file(self, **kwarg):
        data = {}
        if self.type_file in 'simulation':
            path = self.get_input_path()

            for l in open(path):
                if '*' not in l:
                    if l.strip() != '':
                        l = l.strip()
                        prop_name, prop_value = l.split('=')
                        prop_name = prop_name.strip()
                        prop_value = prop_value.strip().split()[0]
                        data[prop_name] = prop_value
            self.data = data
            return data
        else:
            if kwarg.get('ExpOut', False):
                print('%s : no input loaded' %self.name)
    
    def get_input(self):
        self.input_parameters = self.parse_input_file()
        return self.input_parameters



def calibrate(m, b, channel, **kwarg):
    # E = m * c + b
    #m= 2.50071
    #b= -40
    #return m * channel - 2*b
    return m * channel + b