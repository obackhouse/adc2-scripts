import unittest
import numpy as np
from pyscf import gto, scf
from adc import run, ip_radc2, utils


class KnownValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mol = gto.M(atom='O 0 0 0; H 0 0 1; H 0 1 0', basis='cc-pvdz', verbose=0)
        cls.mf = scf.RHF(mol)
        cls.mf.run(conv_tol=1e-12)

    @classmethod
    def tearDownClass(cls):
        del cls.mf

    def test_ip_radc2(self):
        e, v, convs, e_mp2 = run(self.mf, nroots=5, tol=1e-12, do_mp2=True)
        self.assertTrue(all(convs))
        self.assertAlmostEqual(e_mp2, -0.20905685, 7)
        self.assertAlmostEqual(e[0],   0.39840577, 7) 
        self.assertAlmostEqual(e[1],   0.51386759, 7) 
        self.assertAlmostEqual(e[2],   0.61060915, 7) 
        self.assertAlmostEqual(e[3],   1.15103064, 7) 
        self.assertAlmostEqual(e[4],   1.19289418, 7)

    def test_ip_radc2_moments(self):
        mol = gto.M(atom='Li 0 0 0; H 0 0 1.64', basis='cc-pvdz', verbose=0)
        mf = scf.RHF(mol)
        mf.run(conv_tol=1e-12)
        helper = ip_radc2.ADCHelper(mf)
        nmax = 6
        m = helper.get_dense_array()
        t = helper.get_moments(nmax)
        
        def matpow(x, n):
            if n == 0: return np.eye(x.shape[0], dtype=x.dtype)
            elif n == 1: return x
            else: return np.linalg.multi_dot([x,]*n)

        for n in range(nmax+1):
            t_ref = np.dot(np.dot(
                    m[:helper.nocc, helper.nocc:],
                    matpow(m[helper.nocc:, helper.nocc:], n)),
                    m[helper.nocc:, :helper.nocc],
            )
            self.assertAlmostEqual(np.max(np.absolute(t[n]-t_ref)), 0.0, 8)


if __name__ == '__main__':
    print('IP-RADC(2) tests')
    unittest.main()
