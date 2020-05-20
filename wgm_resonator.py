"""
This file has all the code required for the simulation of counter-propagating
light in a whispering gallery mode resonator
"""
import os
import numpy as np
import matplotlib.pyplot as plt
#from txtsave import *
#from printProgressBar import *
import npm

class wgm_resonator:
    """
    This object defines the simulation object for a whispering gallery mode
    resontor, that includes the intensity dependent refractive index for
    counter-propagating light.
    """
    c = 3e8 # Speed of light
    def __init__(self,
                 material = 'fused-silica',
                 resonator_params = 'symm_break_paper'):
        # Load the material and resonator geometry properties
        self.material = _load_struct(material,data_type = 'material')
        self.resonator_params = _load_struct(resonator_params,
                                             data_type = 'resonator_params')
        self.update_resonator_params()
        # Initialise fields
        self.e1 = 0.0 + 0.0j
        self.e2 = 0.0 + 0.0j
        self.e1_tilda = 0.0 + 0.0j
        self.e2_tilda = 0.0 + 0.0j
        self.Delta1 = 0
        self.Delta2 = 0
        
    def update_resonator_params(self):
        # Set all structure values to floats
        for struct in [self.resonator_params, self.material]:
            for (key, value) in struct.items():
                struct[key] = float(value)
        # Change units 
        self.resonator_params['lambda'] = self.resonator_params['lambda']/10**9
        self.resonator_params['r'] = self.resonator_params['r']/10**6
        self.resonator_params['Aeff']= self.resonator_params['Aeff']/10**12
        self.material['n2'] = self.material['n2']/100**2
        df_fsr = (self.c/
                  (2*np.pi*self.resonator_params['r']*self.material['n0']))
        omega_res = self.c/self.resonator_params['lambda']
        gamma = omega_res/(2*self.resonator_params['Q'])
        F0 = 2*np.pi*df_fsr/gamma
        P0 = (np.pi*self.material['n0']*self.resonator_params['Aeff']/
              (self.resonator_params['Q']*F0*self.material['n2']))
        self.resonator_params['df_fsr'] = df_fsr
        self.resonator_params['omega_res'] = omega_res
        self.resonator_params['gamma'] = gamma
        self.resonator_params['F0'] = F0
        self.resonator_params['P0'] = P0
    
    def _getFieldDerivatives(self):
        e1_dot = self.e1_tilda - (1 + 0+1.0j*(abs(self.e1)**2 + 
                                              2*abs(self.e2)**2
                                          - self.Delta1))*self.e1
        e2_dot = self.e2_tilda - (1 + 0+1.0j*(abs(self.e2)**2 + 
                                              2*abs(self.e1)**2 
                                          - self.Delta2))*self.e2
        self.e1_dot, self.e2_dot = e1_dot, e2_dot
        
    def frequencyScan(self,Del0=-4,Del1=7,p1=1.4,p2=1.4,N=10,oscillation=False,
                      amp=None, freq=None, Noise=1e-9):
        if oscillation:
            # Make sure there is an amplitude and frequency given if the
            # simulation is oscillating
            assert all(type(x) is float or int for x in [amp,freq])
            amp1 = np.zeros(N)
            amp2 = np.zeros(N)
            phase1 = np.zeros(N)
            phase2 = np.zeros(N)
            
        self.e1_tilda = np.sqrt(p1)
        self.e2_tilda = np.sqrt(p2)    
        
        self.e1 = 1.0 + 1.0j
        self.e2 = 1.0 + 1.0j
        
        detunings = np.linspace(Del0, Del1, N)        
        pwr1 = np.zeros(N)
        pwr2 = np.zeros(N)
        M1 = np.zeros(N)
        M2 = np.zeros(N)
        dt = 0.01
        scanFig = plt.figure()
        scanAx = scanFig.add_subplot(111)
        
        printProgressBar(iteration=0,total=N,prefix = 'Scanning frequency',
                         length=50)
        for index, det in enumerate(detunings):            
            printProgressBar(iteration=index,total=N,
                             prefix = 'Scanning frequency',length=50)
            self.Delta1 = det
            self.Delta2 = det
            pwrOld = 0
            pwrNew = 10
            count = 0
            while abs(pwrNew-pwrOld)>Noise:
                self._getFieldDerivatives()
                self.e1 += dt*self.e1_dot + Noise*np.random.normal()
                self.e2 += dt*self.e2_dot + Noise*np.random.normal()
                pwrOld += dt*(pwrNew-pwrOld)
                pwrOld=pwrNew
                pwrNew = abs(self.e1)
                count+=1                
            pwr1[index] = abs(self.e1)
            pwr2[index] = abs(self.e2)
            p0 = abs(self.e1)
            
            if oscillation:
                oscFig = plt.figure()
                oscAx = oscFig.add_subplot(111)
                
                phase = 0
                dphase = dt*2*np.pi/freq
                maxPhase = 12*np.pi
                
                while phase < maxPhase:
                    self.e1_tilda = np.sqrt(p1*(1 + amp*np.cos(phase)))
                    self.e2_tilda = np.sqrt(p2)*(1 - 0.0*amp*np.sin(phase))
                    self._getFieldDerivatives()
                    self.e1 += dt*self.e1_dot + Noise*np.random.normal()
                    self.e2 += dt*self.e2_dot + Noise*np.random.normal()
                    
                    phase += dphase
                    
                    oscAx.plot(phase%(2*np.pi),abs(self.e1_tilda),'k.',alpha=0.1)
                    oscAx.plot(phase%(2*np.pi),abs(self.e1),'r.',alpha=0.1)
                    oscAx.plot(phase%(2*np.pi),abs(self.e2),'b.',alpha=0.1)
                    
                    if abs(phase-maxPhase)<2*np.pi:
                        oscAx.plot(phase%(2*np.pi),abs(self.e1),'k.',alpha=0.1)
                        oscAx.plot(phase%(2*np.pi),abs(self.e2),'k.',alpha=0.1)
                        
                        
                        
                oscAx.plot(np.nan,np.nan,'k.',label='input')
                oscAx.plot(np.nan,np.nan,'r.',label='Modulated cavity field')
                oscAx.plot(np.nan,np.nan,'b.',label='Counter-modulated cavity field')
                oscAx.set_xlabel('Phase of input oscillation')
                oscAx.set_ylabel('Power')
                oscAx.legend()
                
        plt.plot(detunings,pwr1,'r',alpha=0.5)
        plt.plot(detunings,pwr2,'b',alpha=0.5)
#        plt.plot(detunings,M1+M2,'k')
            
def _load_struct(name, data_type):
    """
    This function loads the data associated with the name and data type, 
    ensuring easier repeatability/reproducibility of simulations. If this name
    has yet to be defined, it will ask the user to define it in the command 
    window.
    """
    directory = 'params/wgm_resonator_sim/' + data_type + '/'
    filename = directory + name + '.txt'
    # Load file if it exists, if not, as user to create one
    if os.path.exists(filename):
        struct =  txt2struct(filename)
    else:
        data_keys = {'material':['n0','n2 (cm^2/W)'],
                     'resonator_params':['Q','lambda (nm)',
                                         'r (um)','Aeff (um^2)',]}
        keys = data_keys[data_type]
        struct = {}
        for key in keys:
            struct[key.split()[0]] = input("Enter the {} for {}:".format(key,
                   name))
        struct2txt(struct,filename)
    return struct

###############################################################################
        
if __name__ == '__main__':
    plt.close('all')
    sim = wgm_resonator()
    sim.frequencyScan(oscillation=False,amp=0.05,freq=5,Del0=-5,p1=2**2,p2=0.0,N=100)