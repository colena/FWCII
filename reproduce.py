"""Reproduce the collective threshold clock comparison, report and figure.

Run: python reproduce.py (or use the full path from another directory)
Requires NumPy, SciPy and Matplotlib. All calculations use floating-point
arithmetic. Analytical remainder estimates are evaluated with approximate
spectra and coefficients; they are not certified numerical enclosures.
"""
from pathlib import Path
import json
import platform
import warnings
import numpy as np
import scipy
from scipy.integrate import quad, IntegrationWarning
from scipy.special import erfcx, gammaln
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from interface_modes import Mode, roots, W0

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT/'outputs'
FIGURES=OUTPUT/'figures'


def gaussian_weights(N):
    k=np.arange(1,N+1); w=np.zeros(N); n=(k[k%2==1]-1)//2
    w[k%2==1]=np.exp(gammaln(2*n+1)-2*gammaln(n+1)-n*np.log(4)-np.log(2*n+1))/(2*np.pi)
    return w


def spectral_data(mu,N=32,cutoff=24.):
    """Compute N positive modes plus the ground and first omitted modes.

    The Gram diagnostic checks up to the first nine available modes.
    """
    a=roots(mu,N+2); modes=[Mode(mu,v,cutoff=cutoff) for v in a]
    e0=modes[0]; p=e0.product_integral(e0)
    coeff=np.array([W0*(e0.value0*e.slope0-e0.slope0*e.value0)/(e.a-e0.a) for e in modes[1:N+1]])
    # Normalised Gram integrands avoid unnecessarily stringent relative
    # quadrature tolerances on large, mutually cancelling cylinder functions.
    gram=np.array([[e.product_integral(f)+e.product_integral(f,False) for f in modes[:9]] for e in modes[:9]])
    direct=np.array([e0.product_integral(e) for e in modes[1:N+1]])
    return dict(mu=mu,p=p,alpha=a.tolist(),gaps=(a[1:]-a[0]).tolist(),
                coefficients=coeff.tolist(),weights=(coeff**2).tolist(),
                max_matching_residual=max(e.match for e in modes),
                max_first_nine_gram_error=float(np.max(abs(gram-np.eye(gram.shape[0])))),
                max_coefficient_quadrature_discrepancy=float(np.max(abs(direct-coeff))))


def covariances(data,t,N=32):
    w=np.array(data['weights'][:N]); lam=np.array(data['gaps'][:N]); p=data['p']; variance=p*(1-p)
    time=np.atleast_1d(t); shared=[]; independent=[]; sh_bound=[]; ind_bound=[]
    for tt in time:
        one=float(w@erfcx(lam*np.sqrt(tt)/2))
        shared.append(float(w@erfcx((lam[:,None]+lam[None,:])*np.sqrt(tt)/2)@w))
        independent.append(one**2)
        mass=variance-float(w.sum())
        if mass < -1e-10:
            raise ArithmeticError('Negative residual coefficient mass beyond numerical tolerance')
        mass=max(mass,0.)
        sh_bound.append(float(erfcx((data['gaps'][N]+lam[0])*np.sqrt(tt)/2)*(variance**2-w.sum()**2)))
        ind_bound.append(float(2*variance*erfcx(lam[0]*np.sqrt(tt)/2)*erfcx(data['gaps'][N]*np.sqrt(tt)/2)*mass))
    return tuple(np.array(v) for v in [shared,independent,sh_bound,ind_bound])


def amplitudes(data,N=32):
    w=np.array(data['weights'][:N]); lam=np.array(data['gaps'][:N]); variance=data['p']*(1-data['p'])
    shared=float(2/np.sqrt(np.pi)*(w@(1/(lam[:,None]+lam[None,:]))@w))
    one=float(2/np.sqrt(np.pi)*np.sum(w/lam))
    sh_tail=float(2/np.sqrt(np.pi)/(data['gaps'][N]+lam[0])*(variance**2-w.sum()**2))
    one_tail=float(2/np.sqrt(np.pi)/data['gaps'][N]*(variance-w.sum()))
    return dict(shared_partial=shared,shared_remainder_estimate=sh_tail,
                independent_partial=one**2,independent_remainder_estimate=(one+one_tail)**2-one**2)


def gaussian_benchmark(t,power):
    # Use s=sqrt(t)*z for t<=1 to resolve the narrow clock density.
    # For larger t the OU covariance localises the integral in operational s.
    if t<=1:
        fun=lambda z:(np.arcsin(np.exp(-np.sqrt(t)*z/2))/(2*np.pi))**power*np.exp(-z*z/4)/np.sqrt(np.pi)
    else:
        fun=lambda s:(np.arcsin(np.exp(-s/2))/(2*np.pi))**power*np.exp(-s*s/(4*t))/np.sqrt(np.pi*t)
    return quad(fun,0,np.inf,epsabs=2e-13,epsrel=2e-11,limit=200)[0]


def write_reports(report):
    """Write a standalone Markdown report from computed numerical results."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    lines = [
        '# Collective threshold relaxation — numerical report',
        '',
        'Two coordinates; inverse-clock order 1/2; 32 retained positive modes.',
        '',
        'Theory, proof, and truncation bounds: [README application](../README.md#collective-threshold-correlations).',
        '',
        '![Shared and independent clock correlations](figures/collective_clocks.png)',
        '',
        'Both covariances are divided by [p_mu * (1 - p_mu)]^2 in the figure.',
        'Bands estimate spectral truncation only; they do not enclose all numerical errors.',
        '',
        '## Gaussian benchmark at t = 1',
        '',
        '| N | Shared error | Shared bound | Independent error | Independent bound |',
        '| --- | --- | --- | --- | --- |',
    ]
    for row in report['truncation']:
        values = ' | '.join(f"{row[key]:.8e}" for key in (
            'shared_error', 'shared_bound', 'independent_error', 'independent_bound'))
        lines.append(f"| {row['N']} | {values} |")
    lines.extend([
        '', '## Mode diagnostics', '',
        '| mu | Threshold probability | Gram error | Matching residual | Coefficient discrepancy |',
        '| --- | --- | --- | --- | --- |',
    ])
    for row in report['spectral']:
        values = ' | '.join(f"{row[key]:.8e}" for key in (
            'max_first_nine_gram_error', 'max_matching_residual',
            'max_coefficient_quadrature_discrepancy'))
        lines.append(f"| {row['mu']:.8g} | {row['p']:.12g} | {values} |")
    lines.extend([
        '', '## Long-time amplitudes', '',
        'Shared covariances decay as t^(-1/2); independent covariances decay as t^(-1).',
        '',
        '| mu | Shared partial | Shared remainder estimate | Independent partial | Independent remainder estimate |',
        '| --- | --- | --- | --- | --- |',
    ])
    for row in report['long_time']:
        values = ' | '.join(f"{row['amplitudes'][key]:.8e}" for key in (
            'shared_partial', 'shared_remainder_estimate',
            'independent_partial', 'independent_remainder_estimate'))
        lines.append(f"| {row['mu']:.8g} | {values} |")
    lines.extend([
        '', '## Run details', '',
        f"Recorded quadrature warnings: {len(report['quadrature_warnings'])}.",
        '',
        'Versions: ' + ', '.join(f"{key} {value}" for key, value in report['versions'].items()) + '.',
        '',
        'See [results.json](results.json) for full spectra, cutoff sensitivity, nodal checks,',
        'Gaussian reference amplitudes, and scaled covariances through t = 1,000,000.',
        '',
    ])
    (OUTPUT/'numerical_report.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always',IntegrationWarning)
        data=[spectral_data(mu) for mu in [1.,.5,3/7]]
        cutoff_data=spectral_data(.5,cutoff=18.)
    report={'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__},
            'interpretation':'Floating-point diagnostics and estimated analytical remainders; no interval certification.',
            'parameters':{'m':2,'tau':.5,'N':32,'cutoff':24.,'root_scan_points':12001},
            'quadrature_warnings':[str(w.message) for w in caught], 'spectral':data}
    report['cutoff_18_vs_24']={'mu':.5,'max_coefficient_change':float(np.max(abs(np.array(data[1]['coefficients'])-cutoff_data['coefficients']))),
                            'threshold_probability_change':abs(data[1]['p']-cutoff_data['p'])}
    report['gaussian_coefficient_formula_error']=float(np.max(abs(np.array(data[0]['weights'])-gaussian_weights(32))))
    report['nodal_case']={'mu':3/7,'alpha_nearest_3':min(data[2]['alpha'],key=lambda a:abs(a-3))}
    # The covariance benchmark is independent of the cylinder function code.
    exact_sh=gaussian_benchmark(1.,2); exact_ind=gaussian_benchmark(1.,1)**2
    report['gaussian_benchmark_at_t1']={'shared':exact_sh,'independent':exact_ind}
    report['truncation']=[]
    for N in [4,8,16,32]:
        sh,ind,bs,bi=[float(x[0]) for x in covariances(data[0],1.,N)]
        report['truncation'].append(dict(N=N,shared_error=exact_sh-sh,shared_bound=bs,independent_error=exact_ind-ind,independent_bound=bi))
    report['long_time']=[]
    for row in data:
        amps=amplitudes(row); sh,ind,_,_=covariances(row,[1.,100.,1e4,1e6])
        report['long_time'].append(dict(mu=row['mu'],p=row['p'],amplitudes=amps,
            times=[1.,100.,1e4,1e6],scaled_shared=(sh*np.sqrt([1.,100.,1e4,1e6])).tolist(),
            scaled_independent=(ind*np.array([1.,100.,1e4,1e6])).tolist()))
    exact_ind_amp=np.log(2)**2/(4*np.pi)
    exact_sh_amp=quad(lambda s:(np.arcsin(np.exp(-s/2))/(2*np.pi))**2,0,np.inf,epsabs=2e-13,epsrel=2e-11)[0]/np.sqrt(np.pi)
    report['gaussian_exact_amplitudes']={'shared_by_quadrature':exact_sh_amp,'independent':exact_ind_amp}
    FIGURES.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,2,figsize=(6.5,3.05),sharex=True,sharey=True,layout='constrained')
    times=np.logspace(0,5,180)
    for ax,row,title in zip(axes,data[:2],[r'$\mu=1$: Gaussian endpoint',r'$\mu=1/2$: deformed law']):
        sh,ind,bs,bi=covariances(row,times); scale=(row['p']*(1-row['p']))**2
        ax.loglog(times,sh/scale,color='#145c9e',label='Shared clock')
        ax.loglog(times,ind/scale,color='#a84312',ls='--',label='Independent clocks')
        ax.fill_between(times,sh/scale,(sh+bs)/scale,color='#145c9e',alpha=.18)
        ax.fill_between(times,ind/scale,(ind+bi)/scale,color='#a84312',alpha=.18)
        ax.set(title=title,xlabel=r'Physical time $t$',xlim=(1,1e5),ylim=(1e-6,1))
        ax.grid(True,which='major',lw=.4,alpha=.25)
        ax.set_xticks([1,1e2,1e4])
    bt=np.array([1.,10.,100.,1000.,10000.])
    axes[0].plot(bt,[gaussian_benchmark(t,2)*16 for t in bt],'o',ms=3.5,mfc='white',mec='#145c9e',label='Gaussian quadrature')
    axes[0].plot(bt,[gaussian_benchmark(t,1)**2*16 for t in bt],'o',ms=3.5,mfc='white',mec='#a84312')
    axes[0].set_ylabel('Correlation with the initial state')
    axes[0].legend(loc='lower left',fontsize=7.5,frameon=False)
    axes[1].text(800,.006,r'$t^{-1/2}$',color='#145c9e',fontsize=10)
    axes[1].text(350,.0001,r'$t^{-1}$',color='#a84312',fontsize=10)
    fig.savefig(FIGURES/'collective_clocks.pdf'); fig.savefig(FIGURES/'collective_clocks.png',dpi=200); plt.close(fig)
    report['figure']={'time_range':[1.,1e5],'normalisation':'Both covariances are divided by [p_mu*(1-p_mu)]^2.','bands':'partial sum to partial sum plus analytical remainder evaluated with floating-point inputs'}
    (OUTPUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['Collective fractional relaxation: numerical reproduction',json.dumps(report['versions']),
           f'Quadrature warnings: {len(caught)}','Gaussian benchmark at t=1: '+str(report['gaussian_benchmark_at_t1']),
           'N, shared error, shared estimate, independent error, independent estimate']
    for r in report['truncation']:
        lines.append(', '.join(str(r[k]) for k in ['N','shared_error','shared_bound','independent_error','independent_bound']))
    for row,amp in zip(data,report['long_time']):
        lines.extend([f"mu={row['mu']}, p={row['p']}",str(amp['amplitudes']),
                      'Gram, matching, coefficient discrepancies: '+str([row['max_first_nine_gram_error'],row['max_matching_residual'],row['max_coefficient_quadrature_discrepancy']])])
    lines.append('Cutoff sensitivity: '+str(report['cutoff_18_vs_24']))
    (OUTPUT/'results.txt').write_text('\n'.join(lines)+'\n')
    write_reports(report)
    print('\n'.join(lines))

if __name__=='__main__':
    main()
