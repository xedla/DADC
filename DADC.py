'''
THE DESCENT-ASCENT ALGORITHM FOR DC PROGRAMMING
P. D’ALESSANDRO, M. GAUDIOSO, G. GIALLOMBARDO , AND G. MIGLIONICO
'''
import numpy as np
from enum import Enum, auto
from numpy.linalg import norm
from algormeter.tools import counter, dbx
from bundle import Bundle


Par_GAMMAMAX = 1.5 # 1/gamma Max proximity 
Par_GAMMAMIN = .0005 # 1/gamma Min proximity
Par_PROXINC = .8 # Proximity tuning
Par_MU = .1  # Descent ratio
Par_ETA = 1.E-4 #   Stopping tolerance
Par_ATOL = 1.E-3 # tollerance isclose e allclose
RHO = 1.
Par_AGG_GRA = False # enable gradiente aggregato


def DADC(p,**kwargs):

    class BEK(Enum): # Bundle Element Kind
        base = auto()
        f2 = auto()
        aggregate = auto()
        worst = auto()

    class Status(Enum):
        NullStep = auto()
        SeriousStep = auto()
        Stop = auto()
        StartUp = auto()
        StationaryDA = auto()

    def calcRho(status: Status, oldRho: float) -> float:
        match status:
            case Status.SeriousStep:
                dd = (p.gf1(p.Xk + d) - p.gf1(p.Xk)) @ d
                if dd > 1E-10:
                    rho = norm(d)**2/dd
                else:
                    rho = oldRho
                # dbx.print('rho SeriousStep calcolato:', rho, 'v:',v)
                if rho < 1/Par_GAMMAMAX:
                    rho = 1/Par_GAMMAMAX
                    counter.up('min', cls='rho') 
                if rho > 1/Par_GAMMAMIN:
                    rho = 1/Par_GAMMAMIN
                    counter.up('max',cls='rho') 
                return rho
            case Status.NullStep:
                rho = oldRho/Par_PROXINC
                rho = min(1/Par_GAMMAMIN, rho)
                return rho
        return oldRho

    def stepSize(d0: np.ndarray, v: float, mainWay: bool) ->  tuple [np.ndarray, Status]:
        d = d0
        status = Status.NullStep

        if isMainWay and (p.f1(p.Xk + d) < p.f1Xk + Par_MU*v) or not isMainWay and (p.f1(p.Xk + d) < p.f1Xk + Par_MU*v + p.gf2Xk @ d):
            return d, Status.SeriousStep
        return d, status

    def buildAltBundle():
        ef2  = bundle.getFirstOfKind([BEK.f2]) 
        if ef2 is None:
            return

        bundle.deleteByKind([BEK.f2])
        for e in bundle.elems:
            e.alpha += ef2.alpha

    def calcAggreg(d, main, rho) -> None: # crea gradiente aggregato
        if not Par_AGG_GRA:
            bundle.elems.clear()
            return 

        bundle.deleteByKind([BEK.aggregate,BEK.f2])

        if not main:
            for e in bundle.elems:
                e.alpha += p.gf2Xk
            pass

        gg, bb = bundle.solve(rho,[BEK.base])
        b = bb + p.f1(p.Xk + d) - p.f1Xk - d @ gg 
        bundle.elems.clear()
        bundle.append(gg,b,BEK.aggregate)
        return

    p.randomSet(center=0,size=1.5) # set for acad
    global RHO
    rho = RHO
    p.stop = None 
    p.absTol = Par_ATOL
    if str(p) in ('JB04', 'JB10'):
        Par_GAMMAMAX = 2 # 1/gamma Max proximity 
        Par_PROXINC = .2 # Proximity tuning
        RHO = 2.
    else:
        Par_GAMMAMAX = 1.5 # 1/gamma Max proximity 
        Par_PROXINC = .8 # Proximity tuning
        RHO = 1.

    isMainWay = True
    status = Status.StartUp
    bundle = Bundle()

    for k in p.loop():
        dbx.print('status:', status.name, 'isMainWay:', isMainWay, 'rho:',rho) 

        if isMainWay:
            if status in (Status.SeriousStep, Status.StartUp) :
                bundle.append(p.gf1Xk,0.,BEK.base)
                bundle.append(-p.gf2Xk,0.,BEK.f2)

        gg, bb = bundle.solve(rho,[BEK.aggregate,BEK.base,BEK.f2])
        d0 = -rho*gg 
        bbb = bb[0].astype(float) if isinstance(bb,np.ndarray) else float(bb)

        v = float(-rho*norm(gg)**2 - bbb)
        dbx.print('d:',d0, 'v:',v,'gg:',gg, 'bb:', bb) 
        
        if v > -Par_ETA: #  stationary DA point
            if isMainWay: 
                status = Status.StationaryDA
                isMainWay = False # start alt way until a SeriuosStep
                counter.up('alt', cls='way')
                buildAltBundle()
                continue
            else:
                dbx.print('stop v:',v)
                status = Status.Stop
                # counter.log('v','stop')
                break 

        d, status = stepSize(d0, v, isMainWay)
        if status == Status.SeriousStep:
            counter.up('Serious', cls='Step')
            p.Xkp1 = p.Xk + d
            rho = calcRho(status, rho)
            calcAggreg(d,isMainWay, rho)
            isMainWay = True # reset to MainWay
        elif Status.NullStep:
            counter.up('Null', cls='Step')
            nX = p.Xk + d
            nf1 = p.f1(nX)
            ngf1 = p.gf1(nX)
            b = p.f1Xk - (nf1 - ngf1.T @  d)
            
            if isMainWay:
                rho = calcRho(status,rho) 
                bundle.append(ngf1,b,BEK.base)
            else:
                rho = RHO
                bundle.append(ngf1 - p.gf2Xk,b,BEK.base)
    
    bundle.stat()