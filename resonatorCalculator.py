# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 14:04:27 2020

@author: nmorone
"""
import sys
import numpy as np
from PyQt5 import QtCore,QtWidgets,QtGui,uic
from PyQt5.QtCore import Qt

class FSR_Calculator:
    """
    This object gives a calculator for some typical resonator parameters.
    """
    c = 3e8 # Speed of light in vacuum (m/s)
    def __init__(self,
                 n0 = 1.444,
                 n2 = 2.7e-16,
                 Q = 1e6,
                 Q0 = 2e8,
                 lam = 1.550,
                 eta = 0.8,
                 diam = 5750,
                 A = 120,
                 de_lam = 0.52):
        self.n0 = n0 # Refractive index
        self.n2 = n2 # Nonlinear refractive index (um^2/W)
        self.Q = Q # Q-factor
        self.Q0 = Q0 # Intrinsic Q-factor
        self.lam = lam # Wavelength (um)
        self.eta = eta # Coupling efficiency
        self.diam = diam # Resonator diameter (um)
        self.A = A # Mode area (um^2)
        self.de_lam = de_lam # Not sure what this parameter is...
        
        self.calculate()
        
    def updateParams(self,**kwargs):
        allowed_keys = self.__dict__.keys() # Only update existing class
                                            # properties
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in 
                             allowed_keys)
    
    def calculate(self):
        # Threshold power (mW)
        self.p_th = ((1.54*np.pi**2*self.n0**2*self.A*self.diam)/
                     (self.n2*self.Q*self.Q0*self.lam*self.eta))*1e-5
        # Frequency (Hz)
        self.freq = self.c/self.lam * 1e6
        # Tau ring (ns)
        self.tau0 = self.Q0/(np.pi*self.freq)*1e9
        self.tau = self.Q/(np.pi*self.freq)*1e9
        # Energy (eV)
        self.energy = self.freq*4.135667516e-15
        # Free spectral range (FSR, GHz)
        self.fsr = self.c/(np.pi*self.n0*self.diam)*1e6/1e9
        # Finesse
        self.finesse = self.Q0 * self.fsr * 1e9 / self.freq
        self.de_nu = self.de_lam * self.freq**2/ (self.c *1e18)
        
class Q_calculator:
    """
    This object gives a calculator that calculates the Q-factor from
    the FWHM measurements.
    """
    c = 3e8
    
    def __init__(self,
                 lam = 1.55,
                 scanScale = 6,
                 FWHM = 0.23,
                 gamma = 0.7
                 ):
        self.lam = lam # Wavelength (um)
        self.scanScale = scanScale # Scale of frequency sweep (MHz/mV) NB - use
                                  # 1 for a FWHM measured in MHz
        self.FWHM = FWHM # Measured linewidth (mV) NB this is in MHz if 
                         # scanScale = 1
        self.gamma = gamma # Also not sure what this parameter is...
        
        self.calculate()
        
    def updateParams(self,**kwargs):
        allowed_keys = self.__dict__.keys() # Only update existing class
                                            # properties
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in 
                             allowed_keys)
        
    def calculate(self):
        # Frequency (Hz)
        self.freq = self.c/self.lam * 1e3
        # Half width at half maximum (MHz)
        self.HWHM = self.scanScale*self.FWHM/2
        self.Q =(self.freq/1e6)/(2*self.HWHM)
        self.Q_gamma = self.freq/(1000000*self.gamma*2)
        
class lifetimeCalculator:
    """
    This object gives a calculator for the resonator lifetime.
    """
    def __init__(self,
                 lam = 1.55,
                 Q = 5e5):
        self.lam = lam
        self.Q = Q
        self.calculate()
        
    def updateParams(self,**kwargs):
        allowed_keys = self.__dict__.keys() # Only update existing class
                                            # properties
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in 
                             allowed_keys)
        
    def calculate(self):
        self.freq = 3e8/(self.lam*1e-6)
        self.lifetime = self.Q/(2*np.pi*self.freq) * 1e9
        self.bitrate = 1/(2*np.pi*self.lifetime)
        
class ratioCalculator:
    """
    This object converts between ratio and decibel
    """
    def __init__(self,
                 ratio = 0.5):
        self.updateRatio(ratio)
        
    def updateRatio(self,ratio):
        self.ratio = ratio
        self.db = 10*np.log10(self.ratio)
    
    def updateDb(self,db):
        self.db = db
        self.ratio = 10**(self.db/10)
        
class MyInputBox(QtWidgets.QGroupBox):
    """
    This is a custom Qt Widget that allows for giving a name, description and
    value to a variable that is named to be able to be used in other parts of
    the code.
    """
    def __init__(self,
                 parent,
                 varName = 'abc',
                 title = 'def',
                 desc = 'ghi',
                 val = 0.5
                 ):
        super(MyInputBox,self).__init__()
        self.varName = varName
        self.vbox = QtWidgets.QVBoxLayout()
        self.title = QtWidgets.QLabel()
        self.title.setText(title)
        bf = QtGui.QFont()
        bf.setBold(True)
        self.title.setFont(bf)
        
        self.desc = QtWidgets.QLabel()
        self.desc.setText(desc)
        
        self.display = QtWidgets.QLineEdit()
        self.display.setText('{}'.format(val))
        
        self.display.returnPressed.connect(parent.widgetUpdate)
        
        self.vbox.addWidget(self.title)
        self.vbox.addWidget(self.desc)
        self.vbox.addWidget(self.display)
        
        self.setLayout(self.vbox)
        
class MyDisplayBox(QtWidgets.QGroupBox):
    """
    This is a custom Qt Widget that allows for giving a name, description and
    display to a variable.
    """
    def __init__(self,
                 varName = 'abc',
                 title = 'def',
                 desc = 'ghi',
                 val = 0.5
                 ):
        super(MyDisplayBox,self).__init__()
        self.varName = varName
        self.vbox = QtWidgets.QVBoxLayout()
        self.title = QtWidgets.QLabel()
        self.title.setText(title)
        bf = QtGui.QFont()
        bf.setBold(True)
        self.title.setFont(bf)
        
        self.desc = QtWidgets.QLabel()
        self.desc.setText(desc)
        
        self.display = QtWidgets.QLabel()
        self.display.setText('{0:.2f}'.format(val))
        self.display.setFont(bf)
        
        self.vbox.addWidget(self.title)
        self.vbox.addWidget(self.desc)
        self.vbox.addWidget(self.display)
        
        self.setLayout(self.vbox)
    
class calcWidget(QtWidgets.QWidget):
    """
    This gives a QT GUI for the calculator
    """
    def __init__(self, *args, **kwargs):
        super(calcWidget, self).__init__(*args, **kwargs)
        # Initialise calculators
        self.FSR_Calculator = FSR_Calculator()
        self.Q_calculator = Q_calculator()
        self.lifetimeCalculator = lifetimeCalculator()
        self.ratioCalculator = ratioCalculator()
        # Setup Layouts
        layoutMAIN = QtWidgets.QVBoxLayout()
        mySpacer = QtWidgets.QSpacerItem(100, 0, 
                                         QtWidgets.QSizePolicy.MinimumExpanding
                                         , QtWidgets.QSizePolicy.Minimum)
        
        myVSpacer = QtWidgets.QSpacerItem(0, 100, 
                                         QtWidgets.QSizePolicy.Minimum,
                                         QtWidgets.QSizePolicy.MinimumExpanding
                                         )
        layoutTOP = QtWidgets.QHBoxLayout()
        self.lambdaWidget = MyInputBox(self,
                                       varName = 'lam',
                                       title = 'Wavelength (um)',
                                       desc = 'Input light wavelength (in vacuum).\n \nValue:',
                                       val = self.FSR_Calculator.lam)
        
        self.freqWidget = MyDisplayBox(varName = 'freq',
                                     title = 'Frequency (THz)',
                                     desc = 'Input light frequency.\n \nValue:',
                                     val = self.FSR_Calculator.freq/1e12)
        layoutTOP.addWidget(self.lambdaWidget)
        layoutTOP.addSpacerItem(mySpacer)
        layoutTOP.addWidget(self.freqWidget)
        layoutTOP.addSpacerItem(mySpacer)
        
        mainWIDGET = QtWidgets.QTabWidget()
        
        FSRWidget = QtWidgets.QGroupBox()
        FSRLayout = QtWidgets.QHBoxLayout()
        FSR_1 = QtWidgets.QVBoxLayout()
        FSR_2 = QtWidgets.QVBoxLayout()
        FSR_3 = QtWidgets.QVBoxLayout()
        FSR_4 = QtWidgets.QVBoxLayout()
        self.n0Widget =  MyInputBox(self,
                                    varName = 'n0',
                                    title = 'Refractive index',
                                    desc = 'Value:',
                                    val = self.FSR_Calculator.n0)
        self.n2Widget =  MyInputBox(self,
                                    varName = 'n2',
                                    title = 'Nonlinear refractive index',
                                    desc = '3rd Order material refractive index (um^2/W)\n \nValue:',
                                    val = self.FSR_Calculator.n2)
        self.QWidget =  MyInputBox(self,
                                   varName = 'Q',
                                   title = 'Q-Factor',
                                   desc = 'Value:',
                                   val = self.FSR_Calculator.Q)
        self.Q0Widget =  MyInputBox(self,
                                    varName = 'Q0',
                                   title = 'Intrinsic Q-Factor',
                                   desc = 'Value:',
                                   val = self.FSR_Calculator.Q0)
        self.etaWidget =  MyInputBox(self,
                                     varName = 'eta',
                                     title = 'Coupling efficiency',
                                     desc = 'Value:',
                                     val = self.FSR_Calculator.eta)
        self.diamWidget =  MyInputBox(self,
                                      varName = 'diam',
                                      title = 'Resonator Diameter (um)',
                                      desc = 'Value:',
                                      val = self.FSR_Calculator.diam)
        self.AWidget =  MyInputBox(self,
                                   varName = 'A',
                                   title = 'Modal area (um^2)',
                                   desc = 'Value:',
                                   val = self.FSR_Calculator.A)
        self.de_lamWidget =  MyInputBox(self,
                                        varName = 'de_lam',
                                        title = 'de_lam ??',
                                        desc = 'Value:',
                                        val = self.FSR_Calculator.de_lam)
        self.FSRWidget = MyDisplayBox(varName = 'fsr',
                                      title = 'FSR',
                                      desc = 'Calculated Value:',
                                      val = self.FSR_Calculator.fsr)
        
        self.finesseWidget = MyDisplayBox(varName = 'finesse',
                                      title = 'Finesse',
                                      desc = 'Calculated Value:',
                                      val = self.FSR_Calculator.finesse)
        self.energyWidget = MyDisplayBox(varName = 'energy',
                                         title = 'Photon energy (eV)',
                                         desc = 'Calculated Value:',
                                         val = self.FSR_Calculator.energy)
        self.tauWidget = MyDisplayBox(varName = 'tau',
                                      title = 'Cavity lifetime',
                                      desc = 'Calculated Value:',
                                      val = self.FSR_Calculator.tau)
        self.tau0Widget = MyDisplayBox(varName = 'tau0',
                                      title = 'Intrinsic cavity lifetime',
                                      desc = 'Calculated Value:',
                                      val = self.FSR_Calculator.tau0)
        self.de_nuWidget = MyDisplayBox(varName = 'de_nu',
                                        title = 'de_nu ??',
                                        desc = 'Calculated Value:',
                                        val = self.FSR_Calculator.de_nu)
        
        FSR_inputs = [self.n0Widget,
                      self.n2Widget,
                      self.QWidget,
                      self.Q0Widget,
                      self.etaWidget,
                      self.diamWidget,
                      self.AWidget,
                      self.de_lamWidget]
        FSR_outputs = [self.FSRWidget,
                       self.finesseWidget,
                       self.energyWidget,
                       self.tauWidget,
                       self.tau0Widget,
                       self.de_nuWidget]
        
        fsrinput = [FSR_1,FSR_2]
        fsroutput = [FSR_3,FSR_4]
        for index, i in enumerate(FSR_inputs): fsrinput[index%2].addWidget(i)
        for index, i in enumerate(FSR_outputs): fsroutput[index%2].addWidget(i)
        FSRLayout.addLayout(FSR_1)
        FSRLayout.addLayout(FSR_2)        
        
        FSRLayout.addSpacerItem(mySpacer)
        FSRLayout.addLayout(FSR_3)        
        FSRLayout.addLayout(FSR_4)        
        FSRWidget.setLayout(FSRLayout)
        
        
        QWidget = QtWidgets.QGroupBox()
        QLayout = QtWidgets.QHBoxLayout()
        Q_inputs = QtWidgets.QVBoxLayout()
        Q_outputs = QtWidgets.QVBoxLayout()
        
        self.scanWidget = MyInputBox(self,
                                     varName='scanScale',
                                    title='Scan scale (MHz/mV)',
                                    desc = 'This is the scale of the frequency'
                                    ' scan. Set to 1 if FWHM measured in MHz.'
                                    '\nValue:',
                                    val = self.Q_calculator.scanScale
                                    )
        self.fwhmWidget = MyInputBox(self,
                                     varName='FWHM',
                                     title='FWHM (mV)',
                                     desc = 'Value:',
                                     val = self.Q_calculator.FWHM
                                    )
        self.gammaWidget = MyInputBox(self,
                                      varName='gamma',
                                     title='Gamma (??)',
                                     desc = 'Value:',
                                     val = self.Q_calculator.gamma
                                    )
        self.hwhmWidget = MyDisplayBox(varName='HWHM',
                                     title='HWHM (MHz)',
                                     desc = 'Value:',
                                     val = self.Q_calculator.HWHM
                                    )
        self.qOutWidget = MyDisplayBox(varName='Q',
                                     title='Q-factor',
                                     desc = 'Q-factor based on FWHM'
                                     'measurement.\nValue:',
                                     val = self.Q_calculator.Q
                                    )
        self.qOutGamWidget = MyDisplayBox(varName='Q_gamma',
                                          title='Q-factor',
                                          desc = 'Q-factor based on gamma '
                                        'measurement.\nValue:',
                                        val = self.Q_calculator.Q_gamma
                                        )
        
        Q_input_list = [self.scanWidget, self.fwhmWidget, self.gammaWidget]
        Q_output_list = [self.hwhmWidget, self.qOutWidget]
        Q_inputs.addWidget(self.scanWidget)
        Q_inputs.addWidget(self.fwhmWidget)
        Q_inputs.addSpacerItem(myVSpacer)
        Q_inputs.addWidget(self.gammaWidget)
        
        Q_outputs.addWidget(self.hwhmWidget)
        Q_outputs.addWidget(self.qOutWidget)
        Q_outputs.addSpacerItem(myVSpacer)
        Q_outputs.addWidget(self.qOutGamWidget)
        QLayout.addLayout(Q_inputs)
        QLayout.addSpacerItem(mySpacer)
        QLayout.addLayout(Q_outputs)
        QLayout.addSpacerItem(mySpacer)
        QWidget.setLayout(QLayout)
        
        
        lifetimeWidget = QtWidgets.QGroupBox()
        lifetimeLayout = QtWidgets.QHBoxLayout()
        
        self.qLifetimeWidget = MyInputBox(self,
                                          varName='Q_life',
                                          title='Q-factor',
                                          desc = 'Value:',
                                          val = self.lifetimeCalculator.Q
                                          )
        self.lifetimeWidget = MyDisplayBox(varName='lifetime',
                                           title = 'Lifetime (ns)',
                                           desc = 'Photon lifetime in cavity',
                                           val = self.lifetimeCalculator.lifetime)
        
        self.bitrateWidget = MyDisplayBox(varName='bitrate',
                                          title = 'Bitrate (Gbps)',
                                          desc = 'Maximum bitrate of cavity',
                                          val = self.lifetimeCalculator.bitrate)
        
        w1 = QtWidgets.QVBoxLayout()
        w1.addWidget(self.qLifetimeWidget)
        w1.addSpacerItem(myVSpacer)
        w2 = QtWidgets.QVBoxLayout()
        w2.addWidget(self.lifetimeWidget)
        w2.addSpacerItem(myVSpacer)
        w3 = QtWidgets.QVBoxLayout()
        w3.addWidget(self.bitrateWidget)
        w3.addSpacerItem(myVSpacer)
        lifetimeLayout.addLayout(w1)
        lifetimeLayout.addSpacerItem(mySpacer)
        lifetimeLayout.addLayout(w2)
        lifetimeLayout.addLayout(w3)
        lifetimeWidget.setLayout(lifetimeLayout)
        
        ratioWidget = QtWidgets.QGroupBox()
        ratioLayout = QtWidgets.QHBoxLayout()
        
        
        self.ratioWidget = MyInputBox(self,
                                      varName='ratio',
                                      title='Ratio',
                                      desc = '',
                                      val = self.ratioCalculator.ratio
                                      )
        self.dbWidget = MyInputBox(self,
                                   varName='db',
                                  title='Decibels',
                                  desc = '',
                                  val = self.ratioCalculator.db
                                  )
        w1 = QtWidgets.QVBoxLayout()
        w1.addWidget(self.ratioWidget)
        w1.addSpacerItem(myVSpacer)
        w2 = QtWidgets.QVBoxLayout()
        w2.addWidget(self.dbWidget)
        w2.addSpacerItem(myVSpacer)
        ratioLayout.addSpacerItem(mySpacer)
        ratioLayout.addLayout(w1)
        ratioLayout.addSpacerItem(mySpacer)
        ratioLayout.addLayout(w2)
        ratioLayout.addSpacerItem(mySpacer)
        ratioWidget.setLayout(ratioLayout)
        # Put widgets in tabs
        mainWIDGET.addTab(FSRWidget,'FSR Calculator')
        mainWIDGET.addTab(QWidget, 'Q-factor Calculator')
        mainWIDGET.addTab(lifetimeWidget, 'Lifetime Calculator')
        mainWIDGET.addTab(ratioWidget, 'Ratio-to-Decibel Converter')
        
        layoutMAIN.addLayout(layoutTOP)
        layoutMAIN.addWidget(mainWIDGET)
        self.setLayout(layoutMAIN)
        
        self.ratioWidget.display.returnPressed.connect(self.ratioUpdate)
        self.dbWidget.display.returnPressed.connect(self.dbUpdate)
        
        self.widgetMap = {'de_lam':self.FSR_Calculator,
                          'Q0':self.FSR_Calculator,
                          'diam':self.FSR_Calculator,
                          'n2':self.FSR_Calculator,
                          'n0':self.FSR_Calculator,
                          'Q':self.FSR_Calculator,
                          'eta':self.FSR_Calculator,
                          'A':self.FSR_Calculator,
                          'lam':self.FSR_Calculator,
                          'scanScale':self.Q_calculator,
                          'FWHM':self.Q_calculator,
                          'gamma':self.Q_calculator,
                          'Q_life':self.lifetimeCalculator,
                          'lam':None}
        
    def ratioUpdate(self):
        try:
            self.ratioCalculator.updateRatio(float(self.ratioWidget.display.text()))
            self.dbWidget.display.setText('{0:.2f}'.format(self.ratioCalculator.db))
        except ValueError:
            self.ratioWidget.display.setText('Input must be a number')
    def dbUpdate(self):
        try:
            self.ratioCalculator.updateDb(float(self.dbWidget.display.text()))
            self.ratioWidget.display.setText('{0:.2f}'.format(self.ratioCalculator.ratio))
        except ValueError:
            self.dbWidget.display.setText('Input must be a number')
    
    def widgetUpdate(self):
        try:
            value = float(self.sender().text())
            updatedBox = self.sender().parentWidget().varName
            if updatedBox not in ['ratio','db']:
                updatedCalculator = self.widgetMap[updatedBox]
                if updatedCalculator == None:
                    self.FSR_Calculator.updateParams(**{'lam':value})
                    self.FSR_Calculator.calculate()
                    self.Q_calculator.updateParams(**{'lam':value})
                    self.Q_calculator.calculate()
                    self.lifetimeCalculator.updateParams(**{'lam':value})
                    self.lifetimeCalculator.calculate()       
                    
                    
                    self.freqWidget.display.setText('{0:.2f}'.format(
                            self.FSR_Calculator.freq/10**12))
                    self.finesseWidget.display.setText('{0:.2f}'.format(
                            self.FSR_Calculator.finesse))
                    self.energyWidget.display.setText('{0:.2f}'.format(
                            self.FSR_Calculator.energy))
                    self.tauWidget.display.setText('{0:.2f}'.format(
                            self.FSR_Calculator.tau))
                    self.tau0Widget.display.setText('{0:.2f}'.format(
                            self.FSR_Calculator.tau0))
                    self.de_nuWidget.display.setText('{0:.2f}'.format(
                            self.FSR_Calculator.de_nu))
                    self.hwhmWidget.display.setText('{0:.2f}'.format(
                            self.Q_calculator.HWHM))
                    self.qOutWidget.display.setText('{0:.2f}'.format(
                            self.Q_calculator.Q))
                    self.qOutGamWidget.display.setText('{0:.2f}'.format(
                            self.Q_calculator.Q_gamma))
                    self.lifetimeWidget.display.setText('{0:.2f}'.format(
                            self.lifetimeCalculator.lifetime))
                    self.bitrateWidget.display.setText('{0:.2f}'.format(
                            self.lifetimeCalculator.bitrate))
                
                else:
                    updatedCalculator.updateParams(**{'Q':value})
                    updatedCalculator.calculate()
                    if updatedCalculator == self.FSR_Calculator:
                        self.finesseWidget.display.setText('{0:.2f}'.format(
                                updatedCalculator.finesse))
                        self.energyWidget.display.setText('{0:.2f}'.format(
                                updatedCalculator.energy))
                        self.tauWidget.display.setText('{0:.2f}'.format(
                                updatedCalculator.tau))
                        self.tau0Widget.display.setText('{0:.2f}'.format(
                                updatedCalculator.tau0))
                        self.de_nuWidget.display.setText('{0:.2f}'.format(
                                updatedCalculator.de_nu))
                        
                    elif updatedCalculator == self.Q_calculator:
                        self.hwhmWidget.display.setText('{0:.2f}'.format(
                                updatedCalculator.HWHM))
                        self.qOutWidget.display.setText('{0:.2f}'.format(
                                updatedCalculator.Q))
                        self.qOutGamWidget.display.setText('{0:.2f}'.format(
                                updatedCalculator.Q_gamma))
                    else:
                        
                        self.lifetimeWidget.display.setText('{0:.2f}'.format(
                                updatedCalculator.lifetime))
                        self.bitrateWidget.display.setText('{0:.2f}'.format(
                                updatedCalculator.bitrate))
                
        except ValueError:
            self.sender().setText('Input must be a number')
                
            
            
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = calcWidget()
    main.show()
    sys.exit(app.exec_())
        