"""Interface modes used by reproduce.py; floating-point evaluation, not certification."""
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import pbdv, rgamma
W0=1/np.sqrt(2*np.pi)

def cylinder(a,x):
    """Raise from orders in [-2,0] to avoid high-order direct evaluations."""
    if a <= 0:
        return pbdv(a,x)[0]
    n=int(np.ceil(a)); b=a-n
    previous=pbdv(b-1,x)[0]; current=pbdv(b,x)[0]
    for j in range(n):
        previous,current=current,x*current-(b+j)*previous
    return current


def Dorigin(a):
    return (2**(a/2)*np.sqrt(np.pi)*rgamma((1-a)/2),
            -2**((a+1)/2)*np.sqrt(np.pi)*rgamma(-a/2))


def delta(mu,a):
    b=mu*a-(1-mu)/2
    return (np.sqrt(mu)*rgamma(-a/2)*rgamma((1-b)/2)
            +rgamma((1-a)/2)*rgamma(-b/2))


def roots(mu,n):
    """Sign-scan diagnostic, not a certified completeness computation."""
    if mu==1:
        return np.arange(n,dtype=float)
    grid=np.linspace(0,2*n+1,12001)
    values=delta(mu,grid)
    found=[]
    for j in range(len(grid)-1):
        if values[j]==0:
            z=grid[j]
        elif values[j]*values[j+1]<0:
            z=brentq(lambda a:delta(mu,a),grid[j],grid[j+1],xtol=1e-13)
        else:
            continue
        if not found or abs(z-found[-1])>1e-8:
            found.append(float(z))
        if len(found)==n:
            break
    if len(found)!=n:
        raise RuntimeError("Not enough roots found.")
    return np.array(found)


class Mode:
    def __init__(self,mu,a,cutoff=24.):
        self.cutoff=cutoff
        self.mu,self.a=mu,a
        self.b=mu*a-(1-mu)/2
        da,dpa=Dorigin(a)
        db,dpb=Dorigin(self.b)
        matrix=np.array([[da,-db],[dpa,dpb/np.sqrt(mu)]])
        row=matrix[np.argmax(np.linalg.norm(matrix,axis=1))]
        A,B=row[1],-row[0]
        # Arbitrary common scaling before normalisation.
        scale=max(abs(A),abs(B))
        A,B=A/scale,B/scale
        intR=quad(lambda x:(A*cylinder(a,x))**2,0,self.cutoff,epsabs=1e-10,epsrel=2e-9,limit=160)[0]
        intL=quad(lambda z:(B*cylinder(self.b,z))**2,0,self.cutoff,epsabs=1e-10,epsrel=2e-9,limit=160)[0]
        norm=np.sqrt(W0*(intR+np.sqrt(mu)*intL))
        self.A,self.B=A/norm,B/norm
        if self.A*da<0:
            self.A,self.B=-self.A,-self.B
        self.value0=self.A*da
        self.slope0=self.A*dpa
        self.match=float(np.linalg.norm(matrix@np.array([self.A,self.B]))/
                         (np.linalg.norm(matrix)*np.hypot(self.A,self.B)))
    def product_integral(self,other,right=True):
        if right:
            integrand=lambda x:W0*self.A*cylinder(self.a,x)*other.A*cylinder(other.a,x)
        else:
            integrand=lambda z:W0*np.sqrt(self.mu)*self.B*cylinder(self.b,z)*other.B*cylinder(other.b,z)
        return quad(integrand,0,self.cutoff,epsabs=2e-10,epsrel=2e-9,limit=160)[0]
