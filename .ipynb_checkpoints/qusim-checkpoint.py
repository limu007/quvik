from math import pi
import numpy as np

from uncertainties import ufloat
import uncertainties.umath as um
gtrack=0 #printed output level
ggrid=0 #using real QE table for spectral response
clight=2.99792e8

class optical():
    foclength=1850
    diameter=300 #mm
    shade=ufloat(0.14,0.02)
    mirror=0.8
    corrector=0.95
    beamsplitter=0.95#reflectivity
    shortpass=0.85
    longpass=0.7#BMS/other filter transmissivity

    stray=ufloat(0.00011,0.00002)
    external={}
    
    def __init__(self):
        self.external['zodiac']=3
        
    def effective(self,full=0):
        if full==1: return self.effective(0)*self.reflectivity()
        return self.diameter**2*pi/4*(1-self.shade)*1e-6 #in m^2
    
    def reflectivity(self, band=1):
        '''should make wavelength dependant later'''
        if band==2: return self.mirror*self.corrector*self.longpass #through beamsplitter
        if band==1: return self.mirror*self.corrector*self.beamsplitter #reflected on beamsplitter
        return self.mirror*self.corrector # no filter
    def __repr__(self):
        out=f'{self.diameter}mm diam.\teff.surf:\n'
        for i in range(3):
            surf=self.reflectivity(i) * self.effective() *1e4
            out+=f'\tband {i+1}: {surf} cm2\n'
        return out


    
class detector():
    tele=None
    exposure=1
    readout=3 #readout noise
    def __init__(self,pixsize,npix,tele,sens=[]):
        self.pixsize=pixsize
        self.npix=npix
        #self.psfpix=psfpix
        if len(sens)>0:
            self.sensitivity=sens
        else:
            self.sensitivity=[0.8]
        self.tele=tele
        self.bandlims=[[200,400]]
        
    def __repr__(self):
        out=f'pix.size {self.pixsize:.2f} um\n'
        out+=f'field {self.npix} x {self.npix} pix\n'
        out+=f'exp. {self.exposure} s vs. RO noise {self.readout}'
        return out
    
    def angsize(self):
        return self.pixsize*1e-3/self.tele.foclength/pi*180*60*60 #u.arcsec
    
    def get_sens(self,band=None):
        '''so far source spectra not considered'''
        if not np.iterable(self.sensitivity): return self.sensitivity
        if not np.iterable(self.sensitivity[0]):
            if band==None: return self.sensitivity[0]
            else: return self.sensitivity[band]
        if band!=None and band>0 and band<len(self.bandlims): blow,bhig=self.bandlims[band]
        else: blow,bhig=self.bandlims[0]
        l,qe=self.sensitivity
        sel=(l>=blow)*(l<=bhig)
        return qe[sel].mean()
        
    def elecrate(self,source,band=None,grid=0,surf=None):
        if band!=None and band>0 and band<len(self.bandlims): blow,bhig=self.bandlims[band]
        else: blow,bhig=self.bandlims[0]
        
        if surf==None: surf=self.tele.effective()*self.tele.reflectivity(band)
        if grid>0:
            nlims=self.sensitivity[0][::grid]
            dlim2=(nlims[1]-nlims[0])/2
            nlims=nlims[(nlims>=blow-dlim2)*(nlims<=bhig+dlim2)]
            nsens=self.sensitivity[1][:(len(nlims)-1)*grid].reshape(len(nlims)-1,grid).mean(1)
            vals=[source.set_band(nlims[i:i+2]).photrate(surf)*nsens[i] for i in range(len(nlims)-1)]
            return sum(vals)
        if band!=None: source.set_band([blow,bhig])
        return source.photrate(surf)*self.get_sens(band)
    
    def elecount(self,source,band=None,surf=None):
        '''nb. photons in psf pixels
        '''
        #nbpix=(self.tele.psf/self.angsize())**2*pi/4 #not relevant for point sources?
        return self.elecrate(source,band=band,surf=surf)*self.exposure

    def pixnoise(self,sources=[],band=None):
        '''bkg. level in 1 pixel
           NOToutput in photons or electrons
        '''
        #if out=='e':
            #from numpy import sqrt
        #    bkgelec=self.pixnoise(out='phot',sources=sources)*self.get_sens(band) #should model spectrum (later)
        #    return um.sqrt(self.readout**2+bkgelec)
        rate=0
        if hasattr(self,'normsurf'): efsurface=self.normsurf
        else: efsurface=self.tele.effective()*self.tele.reflectivity(band)
        grid=ggrid
        for sr in sources:
            if sr.off: #straylight sources
                rate+=self.elecrate(sr,band=band,surf=efsurface,grid=grid)*self.tele.stray#sr.photrate(efsurface)
            elif hasattr(sr,'radius'): #extended
                rate+=self.elecrate(sr,band=band,surf=efsurface,grid=grid)*self.angsize()**2#sr.photrate(efsurface,self.angsize()**2)
            else:
                rate+=self.elecrate(sr,band=band,surf=efsurface,grid=grid)
                
        if gtrack>1: print(f'{rate} photelectrons, {self.darkrate} dark, {self.readout} from readout')
        rate+=self.darkrate
        if 'zodiac' in self.tele.external: rate+=self.tele.external['zodiac'] #zodiac
        return rate*self.exposure
        
    def psfnoise(self,bgsources=[],band=None,accum=1,src=None):
        '''noise in some rounded number of pixels within PSF
        calculated as a square root of background level
        '''
        nbpix=(self.tele.psf/self.angsize())**2*pi/4
        nbpix=int(nbpix+0.5)
        if gtrack>1: print(f'{nbpix} pixels')
        bkgelec=nbpix*self.pixnoise(sources=bgsources,band=band)#sensitivity[0] 
        if src!=None:bkgelec+=self.elecrate(src,band=band)*self.exposure#target in FoV
        return um.sqrt(self.readout**2*nbpix*accum+bkgelec*accum)
    
    def expose(self,band,src,bkg,integ=0,accum=1):
        '''calculate signal/noise'''
        if integ>0: self.exposure=integ
        sig=self.elecrate(src,band,grid=ggrid)*self.exposure*accum
        noi=self.psfnoise(bkg,band,accum,src=src)
        return sig/noi

    
class source():
    jansky=1e-26 #W/m^2/Hz
    evolt=1.602e-19
    planck=6.626e-34
    zeromag=8.9 #AB magnitude
    def __init__(self,mag,freq=1.3e15,delta_freq=3.45e14,off=False):
        self.mag=mag
        self.freq=freq #Hz
        self.delta_freq=delta_freq
        self.off=off #outside FoV
    def __repr__(self):
        return f'src. {self.mag:.2f} mag'
    def set_band(self,lims,unit='nm'):
        if unit=='nm':
            freqlim=[clight/f*1e9 for f in lims[::-1]]
        elif unit=='eV':
            freqlim=[clight*f/1240*1e9 for f in lims]
        else:
            freqlim=lims
        self.freq=(freqlim[0]+freqlim[1])/2
        self.delta_freq=(freqlim[1]-freqlim[0])
        return self
    def energy(self): #eV
        return self.freq*self.planck/self.evolt
    def flux(self,band=None): #W/m^2
        return 10**(-0.4*(self.mag-self.zeromag))*(self.jansky/self.evolt)*self.delta_freq
    def photrate(self,surface):
        return self.flux()*surface/self.energy()
    def invert(self,rate,surface,nsigma=0):
        '''get magnitude from photrate
        if nsigma>0: rate is bkgrate, compute signal for nsigma significance'''
        if nsigma>0:
            rate=sqrt(rate)*nsigma
        eflux=rate/surface*self.energy()
        eflux/=(self.jansky/self.evolt)*self.delta_freq
        return -np.log10(eflux)/0.4+self.refmag

class specsource(source):
    '''source with defined spectral profile'''
    def __init__(self,mag,freq=1.3e15,delta_freq=3.45e14,off=False,spec=[]):
        super().__init__(mag,freq,delta_freq)
        self.espec=spec
    def flux(self,band=None):
        rep=0
        for i in range(len(self.espec[0])-1):
            self.set_band(self.espec[0][i:i+2])
            rep+=super().flux(self,band)*self.espec[1][i]
        return rep
    
class extsource(source):
    '''for extended sources
    using surface density (in magnitude)
    '''
    radius=10
    def __init__(self,mag,freq=1.3e15,delta_freq=3.45e14,off=False):
        super().__init__(mag,freq,delta_freq)
        
    def __repr__(self):
        return f'field src. {self.mag:.2f} mag/sq."'
    
    def photrate(self,surface,angsize=None):
        if angsize==None: #total magnitude?
                return self.flux()*surface/self.energy()
        return self.flux()*surface/self.energy()*angsize

tele=optical()

try:
    gsens_csv="/home/limu/Documents/Space/QUVIK/Science/hware/QEsensitivity.csv"
    gsens_tab=np.loadtxt(gsens_csv,delimiter=",").T
    gsense_4040=detector(9,4096,tele=tele,sens=gsens_tab) # 2 bands
except:
    gsense_4040=detector(9,4096,tele=tele)

gsense_4040.darkrate=0.04 #e/pix/s @ -40 oC
gsense_4040.readout=3.9 #rms in e
gsense_4040.bandlims=[[200,260],[260,400]]

