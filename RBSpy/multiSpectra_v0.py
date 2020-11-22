class multiSpectra():
    def __init__ (self, path = '.', detector = 'RBS1'):
        self.paths = !ls {path}/*/{detector}*.odf
        self.path = path
        self.detector = detector
        
        self.load_paths()
        self.load_spectra()
        self.calibrate_spectra()
        self.normalize_spectra()
        
    def load_paths(self):
        randPaths = []
        alignPaths= []
        for p in self.paths:
            if 'ALIGN' in p.upper():
                alignPaths.append(p)
            elif 'RANDOM' in p.upper():
                randPaths.append(p)
              
        self.randPaths = randPaths
        self.alignPaths= alignPaths
        
     
    def load_spectra(self):
        align = []
        rand = []

        for r in self.randPaths:
            rand.append(rbsSpectra(r, 'experimental'))
        for r in self.alignPaths:
            align.append(rbsSpectra(r, 'experimental'))
    
        self.align = align
        self.rand = rand
   
    def calibrate_spectra(self):
        for a in self.align:
            a.calibrate_from_file()
        for r in self.rand:
            r.calibrate_from_file()
            
    def normalize_spectra(self):
        for a, r, in zip(self.align, self.rand):
            r.addRandom(r)
            r.renormalization(offset = 100)

            if a.getFolder() in r.getFolder():
                a.addRandom(r)
                a.renormalization(offset = 100)
            else:
                print('Random file not found in %s' %a.getFolder())
                print(a.name.split('ALIGN'))
                print(r.name.split('RANDOM'))