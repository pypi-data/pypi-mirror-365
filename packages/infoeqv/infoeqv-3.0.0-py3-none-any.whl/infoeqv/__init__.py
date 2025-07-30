import numpy as np

def info_eqv_design(x, f):
    import numpy as np
    import math
    x
    f
    N=sum(f)
    d=np.zeros(len(x))
    xbar=np.mean(x)
    for i in range (len(x)):
        d[i]=(x[i]-xbar)/(np.max(x)-xbar)
        dsqr=d**2
        M=sum(f*d)
        mu_1=np.divide(M,N)
        P=sum(f*dsqr)
        mu_2=np.divide(P,N)
        mu_22=mu_2-(mu_1**2)
        Y=N*mu_22
        Z=((1+mu_1)**2)+mu_22
        L=np.divide(Y,Z)
        Y1=(N*((1-mu_1)**2))
        Z1=((1-mu_1)**2)+(mu_22)
        U=np.divide(Y1,Z1)
        S=math.ceil(L)
        T=math.floor(U)
    for a in range (S+1,T+2):
        if (U-L)>1:
            a
        else:
            print("Alternative two_point information equivalent design doesn't exist")
    def createList(S, T):
        return [item for item in range(S, T+1)]
    R=createList(S, T)  #range of S & T
    R1=np.asarray(R)   #array of R
    b=N-R1
    Z3=(T-S+1)
    matrixz1=np.zeros(4*Z3)
    mdat=matrixz1.reshape(Z3,4)
    for i in range(Z3):
        mdat[i,0]=R1[i]
        mdat[i,1]=b[i]
        mdat[i,2]=mu_1-np.sqrt(np.divide(mdat[i,1],mdat[i,0])*mu_22)
        mdat[i,3]=mu_1+np.sqrt(np.divide(mdat[i,0],mdat[i,1])*mu_22)
    print(mdat)
    return
