import dolfin_navier_scipy.stokes_navier_utils as snu
import dolfin_navier_scipy.problem_setups as dnsps

# dolfin.parameters.linear_algebra_backend = 'uBLAS'

# krylovdict = dict(krylov='Gmres', krpslvprms={'tol': 1e-2,
#                                              'convstatsl': [],
#                                              'maxiter': 200})
krylovdict = {}


def testit(problem='drivencavity', N=None, nu=None, Re=None, Nts=1e3,
           ParaviewOutput=False, nsects=1, addfullsweep=False,
           tE=1.0, scheme=None):

    nnewtsteps = 9  # n nwtn stps for vel comp
    vel_nwtn_tol = 1e-14
    tips = dict(t0=0.0, tE=tE, Nts=Nts)

    femp, stokesmatsc, rhsd = dnsps.\
        get_sysmats(problem=problem, Re=Re, nu=nu, scheme=scheme,
                    meshparams=dict(refinement_level=N), mergerhs=True)
    proutdir = 'results/'
    ddir = 'data/'
    data_prfx = problem + '_N{0}_Re{1}_Nts{2}_tE{3}'.\
        format(N, femp['Re'], Nts, tE)

    soldict = stokesmatsc  # containing A, J, JT
    soldict.update(femp)  # adding V, Q, invinds, diribcs
    soldict.update(tips)  # adding time integration params
    soldict.update(rhsd)
    soldict.update(N=N, nu=nu,
                   vel_nwtn_stps=nnewtsteps,
                   vel_nwtn_tol=vel_nwtn_tol,
                   nsects=nsects, addfullsweep=addfullsweep,
                   start_ssstokes=True,
                   get_datastring=None,
                   data_prfx=ddir+data_prfx,
                   paraviewoutput=ParaviewOutput,
                   vel_pcrd_stps=1,
                   clearprvdata=True,
                   vfileprfx=proutdir+'vel_{0}_'.format(scheme),
                   pfileprfx=proutdir+'p_{0}_'.format(scheme))

    soldict.update(krylovdict)  # if we wanna use an iterative solver

    snu.solve_nse(**soldict)
    # print krylovdict['krpslvprms']['convstatsl']


if __name__ == '__main__':
    # scme = 0
    # schemel = ['CR', 'TH']
    # scheme = schemel[scme]
    # testit(problem='cylinderwake', N=2, Re=40, Nts=25, tE=.1)
    # testit(problem='cylinderwake', N=2, Re=30, Nts=24, tE=.1)
    # testit(problem='cylinderwake', N=2, Re=70, Nts=56, tE=.2, nsects=5,
    #        ParaviewOutput=True, scheme='TH')
    testit(problem='cylinderwake', N=2, Re=100, tE=2., Nts=512,
           scheme='TH', nsects=10, addfullsweep=True, ParaviewOutput=True)
    # testit(problem='cylinderwake', N=4, Re=80, Nts=1000, tE=1.,
    #        ParaviewOutput=True, scheme='CR')
