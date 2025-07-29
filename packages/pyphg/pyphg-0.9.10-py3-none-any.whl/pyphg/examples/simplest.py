import pyphg as phg
import math
Cos, M_PI = math.cos, math.pi
a = 1.0
def func_u(input):
    x, y, z = input
    value = Cos(2. * M_PI * x) * Cos(2. * M_PI * y) * Cos(2. * M_PI * z)
    return [value]
def func_f(input):
    value, = func_u(input)
    value = 12. * M_PI * M_PI * value + a * value
    return [value]
mesh = phg.Grid("../test/cube4.dat")
mesh.refineAllElements(1)
order = 1
u_h = phg.Dof(mesh, "P", order)
u_h.setDataByValue(0)
f_h = phg.Dof(mesh, "P", order, udf=func_f)
solver = phg.Solver("pcg", u_h)
for e in mesh.getElementIterator():
    emat = e.quadGradBasDotGradBas(u_h, u_h)
    eload = e.quadDofTimesBas(f_h, u_h)
    gid = e.getGlobalIndex(solver)
    print(f'the element {e} matrix is {emat}, load is {eload}, global index {gid}')
    is_boundary, boundary_val = e.getDirichletBC(u_h, func_u)
    phg.utils.processBoundary(is_boundary, boundary_val, emat, eload)
    solver.addMatrixEntries(gid, gid, emat)
    solver.addRHSEntries(gid, eload)
solver.solve(u_h)
mesh.exportVTK("solution.vtk", u_h)
