import dolfin
import os

import dolfin_navier_scipy.dolfin_to_sparrays as dts
import dolfin_navier_scipy.stokes_navier_utils as snu
import dolfin_navier_scipy.problem_setups as dnsps

dolfin.parameters.linear_algebra_backend = 'uBLAS'


def testit(problem='drivencavity', N=None, nu=1e-2):

    problemdict = dict(drivencavity=dnsps.drivcav_fems,
                       cylinderwake=dnsps.cyl_fems)
    problemfem = problemdict[problem]
    femp = problemfem(N)

    dolfin.plot(femp['V'].mesh())

    # setting some parameters
    nu = nu  # this is so to say 1/Re
    nnewtsteps = 9  # n nwtn stps for vel comp
    vel_nwtn_tol = 1e-14
    # prefix for data files
    data_prfx = problem
    # dir to store data
    ddir = 'data/'
    # paraview output
    ParaviewOutput = True
    proutdir = 'results/'
    tips = dict(t0=0.0, tE=1.0, Nts=100)

    try:
        os.chdir(ddir)
    except OSError:
        raise Warning('need "' + ddir + '" subdir for storing the data')
    os.chdir('..')

    if ParaviewOutput:
        curwd = os.getcwd()
        try:
            os.chdir(proutdir)
            # for fname in glob.glob(data_prfx + '*'):
            #     os.remove(fname)
            os.chdir(curwd)
        except OSError:
            raise Warning('the ' + proutdir + ' subdir for storing the' +
                          ' output does not exist. Make it yourself' +
                          ' or set paraviewoutput=False')

    stokesmats = dts.get_stokessysmats(femp['V'], femp['Q'], nu)

    rhsd_vf = dts.setget_rhs(femp['V'], femp['Q'],
                             femp['fv'], femp['fp'], t=0)

    # remove the freedom in the pressure
    stokesmats['J'] = stokesmats['J'][:-1, :][:, :]
    stokesmats['JT'] = stokesmats['JT'][:, :-1][:, :]
    rhsd_vf['fp'] = rhsd_vf['fp'][:-1, :]

    # reduce the matrices by resolving the BCs
    (stokesmatsc,
     rhsd_stbc,
     invinds,
     bcinds,
     bcvals) = dts.condense_sysmatsbybcs(stokesmats,
                                         femp['diribcs'])

    # pressure freedom and dirichlet reduced rhs
    rhsd_vfrc = dict(fpr=rhsd_vf['fp'], fvc=rhsd_vf['fv'][invinds, ])

    # add the info on boundary and inner nodes
    bcdata = {'bcinds': bcinds,
              'bcvals': bcvals,
              'invinds': invinds}
    femp.update(bcdata)

    # casting some parameters
    NV, INVINDS = len(femp['invinds']), femp['invinds']

    soldict = stokesmatsc  # containing A, J, JT
    soldict.update(femp)  # adding V, Q, invinds, diribcs
    soldict.update(rhsd_vfrc)  # adding fvc, fpr
    soldict.update(tips)  # adding time integration params
    soldict.update(fv_stbc=rhsd_stbc['fv'], fp_stbc=rhsd_stbc['fp'],
                   N=N, nu=nu,
                   nnewtsteps=nnewtsteps,
                   vel_nwtn_tol=vel_nwtn_tol,
                   ddir=ddir, get_datastring=None,
                   data_prfx=data_prfx,
                   paraviewoutput=ParaviewOutput, prfdir=proutdir,
                   vfileprfx=proutdir+'vel_',
                   pfileprfx=proutdir+'p_')

#
# compute the uncontrolled steady state Navier-Stokes solution
#
    # v_ss_nse, list_norm_nwtnupd = snu.solve_steadystate_nse(**soldict)
    snu.solve_nse(**soldict)


if __name__ == '__main__':
    testit(N=25, nu=3e-4)
    # testit(problem='cylinderwake', N=3, nu=3e-3)
