
from tilingpuzzles.games import komino as _komio
from src.tilingpuzzles.solvers.kominoSolver import KominoSolverLimited
from tilingpuzzles.games.stone import Stone
from tilingpuzzles.games.komino import Komino

from logging import info



def test_KominoSolverLimited():
    Komino=_komio.Komino

    N=15

    for k in range(2,6):
        komino,stonesAllowed=Komino.generate(N,k)

        solver=KominoSolverLimited(komino,stonesAllowed)
        solution = solver.solve()
        info(f"{solution = }")
        assert solution

        res=set()
        for st in solver.solution:
            res |= st
        res = Stone(res)
        assert res == komino.T

def test_KominSolverUnlimited():

    DP_f={}

    def f(n,r):
        if n<0:
                return 0
        if (n,r) in DP_f:
            return DP_f[(n,r)]
        match r:
            case 0:
                if n==0:
                 return 1
                res = f(n-1,0)+ f(n-2,1)+ f(n-3,2)+ f(n-2,4)+f(n-2,6)
            case 1:
                res = f(n,0)
            case 2:
                res =f(n,3)+f(n,4)+f(n,5)
            case 3:
                res =f(n,0)
            case 4:
                res = f(n,0)+f(n-1,5)
            case 5:
                res = f(n,0)+f(n-1,6)
            case 6:
                res = f(n-1,4)
            case _:
                assert False,"Unreachable"

        DP_f[(n,r)]=res 
        return res


    def solution_count(n):
        s=("#"*n +"\n")*3
        U=Stone.from_string(s)
        komi=Komino(U,k=3)
        res=komi.count_solutions(progressLevel=0)
        return res 

    for i in range(20):
        dp_sol=f(i,0)
        prog_sol=solution_count(i)
        assert dp_sol==prog_sol,f"errror n={i} : {dp_sol = }, {prog_sol = } both Should agree"