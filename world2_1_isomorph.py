# SPDX-License-Identifier: MIT
"""
World2 isomorph: Jay W. Forrester's World Dynamics model, card for card from DYNAMO.

Authors: Nick V. Flor (University of New Mexico, nickflor@unm.edu) and
         Claudia (Claude Interactive Assistant), i.e., Claude, an AI model by Anthropic.
License: MIT (see LICENSE). To cite this code, see CITE.md.
Model:   Jay W. Forrester's World2, from World Dynamics (1971; 2nd ed. 1973).

Source: Jay W. Forrester, World Dynamics (2nd ed., 1973), Appendix B,
"Equations of the World Model". The DYNAMO listing is in source-code.dyn,
and every name used here is defined in definition-of-terms.md.

HOW TO READ THIS FILE

Every DYNAMO card appears as a comment, with its Python translation right under it.
Variable names keep DYNAMO's time suffixes, so the timing of every value is visible:

    P.J   ->  P_J    value at the previous time step
    P.K   ->  P_K    value now
    BR.JK ->  BR_JK  a rate over the interval just finished (J to K)
    BR.KL ->  BR_KL  a rate over the interval about to start (K to L)

Card types (the letter after the equation number):

    L  level          N  initial value     R  rate
    A  auxiliary      S  supplementary     C  constant
    T  table          X  continuation of the card above

THE ONE LIBERTY TAKEN

DYNAMO did not run the listing top to bottom. The compiler read every equation
first, then sorted the auxiliaries so each one is computed after everything it
uses. The book's order is not an execution order: equation 3 uses MSL, which is
not defined until equation 4.

Python does run top to bottom, so inside the time loop the auxiliaries appear in
a sorted order. Each one still carries its book equation number, so you can find
it in source-code.dyn. Constants and tables do not depend on order, so they stay
in book order.

Run:  python world2_1_isomorph.py
Uses only the Python standard library. If matplotlib is installed, the two PLOT
cards are drawn and saved as world2_1_isomorph_ORIG-A.png and world2_1_isomorph_ORIG-B.png.
"""

#       *       WORLD DYNAMICS W5


# ---------------------------------------------------------------------------
# DYNAMO functions used by the model
# ---------------------------------------------------------------------------

def CLIP(A, B, X, Y):
    """DYNAMO CLIP: A if X >= Y, otherwise B.

    The model uses it as a time switch. CLIP(BRN, BRN1, SWT1, TIME.K) gives BRN
    while SWT1 >= TIME, that is, up to the switch time, and BRN1 after it.
    """
    if X >= Y:
        return A
    return B


def TABHL(TAB, X, XLOW, XHIGH, XINCR):
    """DYNAMO TABHL: table lookup with straight-line interpolation.

    TAB holds the table's values at X = XLOW, XLOW + XINCR, ..., XHIGH.
    Outside that range TABHL holds the end value flat (the HL suffix stands
    for horizontal limits).
    """
    if X <= XLOW:
        return TAB[0]
    if X >= XHIGH:
        return TAB[-1]
    i = int((X - XLOW) / XINCR)          # index of the table point just below X
    i = min(i, len(TAB) - 2)              # guard against floating-point round-up
    fraction = (X - (XLOW + i * XINCR)) / XINCR
    return TAB[i] + fraction * (TAB[i + 1] - TAB[i])


_table_warnings = set()

def TABLE(TAB, X, XLOW, XHIGH, XINCR):
    """DYNAMO TABLE: the same lookup as TABHL, for inputs expected to stay in range.

    DYNAMO reported an input outside XLOW..XHIGH as an error; TABHL is the
    variant that allows it. Here we print a warning (once per table) and then
    hold the end value, so the run can continue.
    """
    if (X < XLOW or X > XHIGH) and id(TAB) not in _table_warnings:
        _table_warnings.add(id(TAB))
        print(f"TABLE warning at TIME={TIME_K}: input {X:.4g} is outside {XLOW}..{XHIGH}")
    return TABHL(TAB, X, XLOW, XHIGH, XINCR)


# ---------------------------------------------------------------------------
# Constants (C) and tables (T), in book order
# ---------------------------------------------------------------------------

# 1.2   C   PI=1.65E9
PI = 1.65e9
# 2.2   C   BRN=.04
BRN = .04
# 2.3   C   BRN1=.04
BRN1 = .04
# 2.4   C   SWT1=1970
SWT1 = 1970
# 3.1   T   BRMMT=1.2/1/.85/.75/.7/.7
BRMMT = [1.2, 1, .85, .75, .7, .7]
# 4.1   C   ECIRN=1
ECIRN = 1
# 6.1   T   NREMT=0/.15/.5/.85/1
NREMT = [0, .15, .5, .85, 1]
# 8.2   C   NRI=900E9
NRI = 900e9
# 9.1   C   NRUN=1
NRUN = 1
# 9.2   C   NRUN1=1
NRUN1 = 1
# 9.3   C   SWT2=1970
SWT2 = 1970
# 10.2  C   DRN=.028
DRN = .028
# 10.3  C   DRN1=.028
DRN1 = .028
# 10.4  C   SWT3=1970
SWT3 = 1970
# 11.1  T   DRMMT=3/1.8/1/.8/.7/.6/.53/.5/.5/.5/.5
DRMMT = [3, 1.8, 1, .8, .7, .6, .53, .5, .5, .5, .5]
# 12.1  T   DRPMT=.92/1.3/2/3.2/4.8/6.8/9.2
DRPMT = [.92, 1.3, 2, 3.2, 4.8, 6.8, 9.2]
# 13.1  T   DRFMT=30/3/2/1.4/1/.7/.6/.5/.5
DRFMT = [30, 3, 2, 1.4, 1, .7, .6, .5, .5]
# 14.1  T   DRCMT=.9/1/1.2/1.5/1.9/3
DRCMT = [.9, 1, 1.2, 1.5, 1.9, 3]
# 15.1  C   LA=135E6
LA = 135e6
# 15.2  C   PDN=26.5
PDN = 26.5
# 16.1  T   BRCMT=1.05/1/.9/.7/.6/.55
BRCMT = [1.05, 1, .9, .7, .6, .55]
# 17.1  T   BRFMT=0/1/1.6/1.9/2
BRFMT = [0, 1, 1.6, 1.9, 2]
# 18.1  T   BRPMT=1.02/.9/.7/.4/.25/.15/.1
BRPMT = [1.02, .9, .7, .4, .25, .15, .1]
# 19.1  C   FC=1
FC = 1
# 19.2  C   FC1=1
FC1 = 1
# 19.3  C   FN=1
FN = 1
# 19.4  C   SWT7=1970
SWT7 = 1970
# 20.1  T   FCMT=2.4/1/.6/.4/.3/.2
FCMT = [2.4, 1, .6, .4, .3, .2]
# 21.1  T   FPCIT=.5/1/1.4/1.7/1.9/2.05/2.2
FPCIT = [.5, 1, 1.4, 1.7, 1.9, 2.05, 2.2]
# 22.1  C   CIAFN=.3
CIAFN = .3
# 24.2  C   CII=.4E9
CII = .4e9
# 25.1  C   CIGN=.05
CIGN = .05
# 25.2  C   CIGN1=.05
CIGN1 = .05
# 25.3  C   SWT4=1970
SWT4 = 1970
# 26.1  T   CIMT=.1/1/1.8/2.4/2.8/3
CIMT = [.1, 1, 1.8, 2.4, 2.8, 3]
# 27.1  C   CIDN=.025
CIDN = .025
# 27.2  C   CIDN1=.025
CIDN1 = .025
# 27.3  C   SWT5=1970
SWT5 = 1970
# 28.1  T   FPMT=1.02/.9/.65/.35/.2/.1/.05
FPMT = [1.02, .9, .65, .35, .2, .1, .05]
# 29.1  C   POLS=3.6E9
POLS = 3.6e9
# 30.2  C   POLI=.2E9
POLI = .2e9
# 31.1  C   POLN=1
POLN = 1
# 31.2  C   POLN1=1
POLN1 = 1
# 31.3  C   SWT6=1970
SWT6 = 1970
# 32.1  T   POLCMT=.05/1/3/5.4/7.4/8
POLCMT = [.05, 1, 3, 5.4, 7.4, 8]
# 34.1  T   POLATT=.6/2.5/5/8/11.5/15.5/20
POLATT = [.6, 2.5, 5, 8, 11.5, 15.5, 20]
# 35.2  C   CIAFI=.2
CIAFI = .2
# 35.3  C   CIAFT=15
CIAFT = 15
# 36.1  T   CFIFRT=1/.6/.3/.15/.1
CFIFRT = [1, .6, .3, .15, .1]
# 37.1  C   QLS=1
QLS = 1
# 38.1  T   QLMT=.2/1/1.7/2.3/2.7/2.9
QLMT = [.2, 1, 1.7, 2.3, 2.7, 2.9]
# 39.1  T   QLCT=2/1.3/1/.75/.55/.45/.38/.3/.25/.22/.2
QLCT = [2, 1.3, 1, .75, .55, .45, .38, .3, .25, .22, .2]
# 40.1  T   QLFT=0/1/1.8/2.4/2.7
QLFT = [0, 1, 1.8, 2.4, 2.7]
# 41.1  T   QLPT=1.04/.85/.6/.3/.15/.05/.02
QLPT = [1.04, .85, .6, .3, .15, .05, .02]
# 42.1  T   NRMMT=0/1/1.8/2.4/2.9/3.3/3.6/3.8/3.9/3.95/4
NRMMT = [0, 1, 1.8, 2.4, 2.9, 3.3, 3.6, 3.8, 3.9, 3.95, 4]
# 43.1  T   CIQRT=.7/.8/1/1.5/2
CIQRT = [.7, .8, 1, 1.5, 2]

#       NOTE    CONTROL CARDS
# 43.5  C   DT=.2
DT = .2
# 43.6  C   LENGTH=2100
LENGTH = 2100
# 44.1  C   PRTP1=0
PRTP1 = 0
# 44.2  C   PRTP2=0
PRTP2 = 0
# 44.3  C   PRSWT=0
PRSWT = 0
# 45.1  C   PLTP1=4
PLTP1 = 4
# 45.2  C   PLTP2=4
PLTP2 = 4
# 45.3  C   PLSWT=0
PLSWT = 0


# ---------------------------------------------------------------------------
# Initial values (N): the levels and TIME at the first moment K
# ---------------------------------------------------------------------------

# 1.1   N   P=PI
P_K = PI
# 8.1   N   NR=NRI
NR_K = NRI
# 24.1  N   CI=CII
CI_K = CII
# 30.1  N   POL=POLI
POL_K = POLI
# 35.1  N   CIAF=CIAFI
CIAF_K = CIAFI
# 43.7  N   TIME=1900
TIME_K = 1900


# ---------------------------------------------------------------------------
# What we keep from the run (DYNAMO printed and plotted; we record)
# ---------------------------------------------------------------------------

results = {name: [] for name in [
    "TIME",
    # levels
    "P", "NR", "CI", "POL", "CIAF",
    # rates
    "BR", "DR", "NRUR", "CIG", "CID", "POLG", "POLA",
    # auxiliaries on the book's plots
    "POLR", "QL", "FR", "MSL", "QLC", "QLP",
]}


# ---------------------------------------------------------------------------
# The time loop. Each pass is one moment K:
#   1. auxiliaries at K, from the levels at K
#   2. rates for the coming interval K to L
#   3. record, and stop if TIME has reached LENGTH
#   4. time moves on: K becomes J, KL becomes JK
#   5. levels at the new K, from the old levels and the rates JK
# ---------------------------------------------------------------------------

while True:

    # ======== 1. Auxiliaries at time K (in computed order) ========

    # 7     A   NRFR.K=NR.K/NRI
    NRFR_K = NR_K / NRI
    # 6     A   NREM.K=TABLE(NREMT,NRFR.K,0,1,.25)
    NREM_K = TABLE(NREMT, NRFR_K, 0, 1, .25)
    # 23    A   CIR.K=CI.K/P.K
    CIR_K = CI_K / P_K
    # 5     A   ECIR.K=(CIR.K)(1-CIAF.K)(NREM.K)/(1-CIAFN)
    ECIR_K = CIR_K * (1 - CIAF_K) * NREM_K / (1 - CIAFN)
    # 4     A   MSL.K=ECIR.K/(ECIRN)
    MSL_K = ECIR_K / ECIRN

    # 3     A   BRMM.K=TABHL(BRMMT,MSL.K,0,5,1)
    BRMM_K = TABHL(BRMMT, MSL_K, 0, 5, 1)
    # 11    A   DRMM.K=TABHL(DRMMT,MSL.K,0,5,.5)
    DRMM_K = TABHL(DRMMT, MSL_K, 0, 5, .5)
    # 26    A   CIM.K=TABHL(CIMT,MSL.K,0,5,1)
    CIM_K = TABHL(CIMT, MSL_K, 0, 5, 1)
    #       NOTE    EQUATION 42 CONNECTS HERE FROM EQ. 4 TO EQ. 9
    # 42    A   NRMM.K=TABHL(NRMMT,MSL.K,0,10,1)
    NRMM_K = TABHL(NRMMT, MSL_K, 0, 10, 1)
    # 38    A   QLM.K=TABHL(QLMT,MSL.K,0,5,1)
    QLM_K = TABHL(QLMT, MSL_K, 0, 5, 1)

    # 15    A   CR.K=(P.K)/(LA*PDN)
    CR_K = P_K / (LA * PDN)
    # 16    A   BRCM.K=TABLE(BRCMT,CR.K,0,5,1)
    BRCM_K = TABLE(BRCMT, CR_K, 0, 5, 1)
    # 14    A   DRCM.K=TABLE(DRCMT,CR.K,0,5,1)
    DRCM_K = TABLE(DRCMT, CR_K, 0, 5, 1)
    # 20    A   FCM.K=TABLE(FCMT,CR.K,0,5,1)
    FCM_K = TABLE(FCMT, CR_K, 0, 5, 1)
    # 39    A   QLC.K=TABLE(QLCT,CR.K,0,5,.5)
    QLC_K = TABLE(QLCT, CR_K, 0, 5, .5)

    # 29    A   POLR.K=POL.K/POLS
    POLR_K = POL_K / POLS
    # 18    A   BRPM.K=TABLE(BRPMT,POLR.K,0,60,10)
    BRPM_K = TABLE(BRPMT, POLR_K, 0, 60, 10)
    # 12    A   DRPM.K=TABLE(DRPMT,POLR.K,0,60,10)
    DRPM_K = TABLE(DRPMT, POLR_K, 0, 60, 10)
    # 28    A   FPM.K=TABLE(FPMT,POLR.K,0,60,10)
    FPM_K = TABLE(FPMT, POLR_K, 0, 60, 10)
    # 34    A   POLAT.K=TABLE(POLATT,POLR.K,0,60,10)
    POLAT_K = TABLE(POLATT, POLR_K, 0, 60, 10)
    # 32    A   POLCM.K=TABHL(POLCMT,CIR.K,0,5,1)
    POLCM_K = TABHL(POLCMT, CIR_K, 0, 5, 1)
    # 41    A   QLP.K=TABLE(QLPT,POLR.K,0,60,10)
    QLP_K = TABLE(QLPT, POLR_K, 0, 60, 10)

    # 22    A   CIRA.K=(CIR.K)(CIAF.K)/CIAFN
    CIRA_K = CIR_K * CIAF_K / CIAFN
    # 21    A   FPCI.K=TABHL(FPCIT,CIRA.K,0,6,1)
    FPCI_K = TABHL(FPCIT, CIRA_K, 0, 6, 1)
    # 19    A   FR.K=(FPCI.K)(FCM.K)(FPM.K)(CLIP(FC,FC1,SWT7,TIME.K))/FN
    FR_K = FPCI_K * FCM_K * FPM_K * CLIP(FC, FC1, SWT7, TIME_K) / FN
    # 17    A   BRFM.K=TABHL(BRFMT,FR.K,0,4,1)
    BRFM_K = TABHL(BRFMT, FR_K, 0, 4, 1)
    # 13    A   DRFM.K=TABHL(DRFMT,FR.K,0,2,.25)
    DRFM_K = TABHL(DRFMT, FR_K, 0, 2, .25)
    # 36    A   CFIFR.K=TABHL(CFIFRT,FR.K,0,2,.5)
    CFIFR_K = TABHL(CFIFRT, FR_K, 0, 2, .5)
    # 40    A   QLF.K=TABHL(QLFT,FR.K,0,4,1)
    QLF_K = TABHL(QLFT, FR_K, 0, 4, 1)

    #       NOTE    INPUT FROM EQN. 38 AND 40 TO EQN. 35
    # 43    A   CIQR.K=TABHL(CIQRT,QLM.K/QLF.K,0,2,.5)
    CIQR_K = TABHL(CIQRT, QLM_K / QLF_K, 0, 2, .5)
    # 37    S   QL.K=(QLS)(QLM.K)(QLC.K)(QLF.K)(QLP.K)
    QL_K = QLS * QLM_K * QLC_K * QLF_K * QLP_K

    # ======== 2. Rates for the coming interval K to L ========

    # 2     R   BR.KL=(P.K)(CLIP(BRN,BRN1,SWT1,TIME.K))(BRFM.K)(BRMM.K)(BRCM.K)(BR
    #       X   PM.K)
    BR_KL = P_K * CLIP(BRN, BRN1, SWT1, TIME_K) * BRFM_K * BRMM_K * BRCM_K * BRPM_K
    # 10    R   DR.KL=(P.K)(CLIP(DRN,DRN1,SWT3,TIME.K))(DRMM.K)(DRPM.K)(DRFM.K)(DR
    #       X   CM.K)
    DR_KL = P_K * CLIP(DRN, DRN1, SWT3, TIME_K) * DRMM_K * DRPM_K * DRFM_K * DRCM_K
    # 9     R   NRUR.KL=(P.K)(CLIP(NRUN,NRUN1,SWT2,TIME.K))(NRMM.K)
    NRUR_KL = P_K * CLIP(NRUN, NRUN1, SWT2, TIME_K) * NRMM_K
    # 25    R   CIG.KL=(P.K)(CIM.K)(CLIP(CIGN,CIGN1,SWT4,TIME.K))
    CIG_KL = P_K * CIM_K * CLIP(CIGN, CIGN1, SWT4, TIME_K)
    # 27    R   CID.KL=(CI.K)(CLIP(CIDN,CIDN1,SWT5,TIME.K))
    CID_KL = CI_K * CLIP(CIDN, CIDN1, SWT5, TIME_K)
    # 31    R   POLG.KL=(P.K)(CLIP(POLN,POLN1,SWT6,TIME.K))(POLCM.K)
    POLG_KL = P_K * CLIP(POLN, POLN1, SWT6, TIME_K) * POLCM_K
    # 33    R   POLA.KL=POL.K/POLAT.K
    POLA_KL = POL_K / POLAT_K

    # Print and plot periods (DYNAMO output control)
    # 44    A   PRTPER.K=CLIP(PRTP1,PRTP2,PRSWT,TIME.K)
    PRTPER_K = CLIP(PRTP1, PRTP2, PRSWT, TIME_K)
    # 45    A   PLTPER.K=CLIP(PLTP1,PLTP2,PLSWT,TIME.K)
    PLTPER_K = CLIP(PLTP1, PLTP2, PLSWT, TIME_K)

    # ======== 3. Record this moment, and stop at the end of the run ========

    results["TIME"].append(TIME_K)
    results["P"].append(P_K)
    results["NR"].append(NR_K)
    results["CI"].append(CI_K)
    results["POL"].append(POL_K)
    results["CIAF"].append(CIAF_K)
    results["BR"].append(BR_KL)
    results["DR"].append(DR_KL)
    results["NRUR"].append(NRUR_KL)
    results["CIG"].append(CIG_KL)
    results["CID"].append(CID_KL)
    results["POLG"].append(POLG_KL)
    results["POLA"].append(POLA_KL)
    results["POLR"].append(POLR_K)
    results["QL"].append(QL_K)
    results["FR"].append(FR_K)
    results["MSL"].append(MSL_K)
    results["QLC"].append(QLC_K)
    results["QLP"].append(QLP_K)

    if TIME_K >= LENGTH:
        break

    # ======== 4. Time moves on: K becomes J, and KL becomes JK ========

    TIME_J = TIME_K
    P_J, NR_J, CI_J, POL_J, CIAF_J = P_K, NR_K, CI_K, POL_K, CIAF_K
    CFIFR_J, CIQR_J = CFIFR_K, CIQR_K        # equation 35 uses these at J
    BR_JK, DR_JK = BR_KL, DR_KL
    NRUR_JK = NRUR_KL
    CIG_JK, CID_JK = CIG_KL, CID_KL
    POLG_JK, POLA_JK = POLG_KL, POLA_KL

    # ======== 5. Levels at the new time K (book order) ========

    # Adding 0.2 over and over drifts in binary floating point (1900 + 0.2 + 0.2 ...
    # never lands exactly on 1970), so TIME is rounded. Without it, the CLIP
    # switches at 1970 and the stop at LENGTH could fire one step early or late.
    TIME_K = round(TIME_J + DT, 6)

    # 1     L   P.K=P.J+(DT)(BR.JK-DR.JK)
    P_K = P_J + DT * (BR_JK - DR_JK)
    # 8     L   NR.K=NR.J+(DT)(-NRUR.JK)
    NR_K = NR_J + DT * (-NRUR_JK)
    # 24    L   CI.K=CI.J+(DT)(CIG.JK-CID.JK)
    CI_K = CI_J + DT * (CIG_JK - CID_JK)
    # 30    L   POL.K=POL.J+(DT)(POLG.JK-POLA.JK)
    POL_K = POL_J + DT * (POLG_JK - POLA_JK)
    # 35    L   CIAF.K=CIAF.J+(DT/CIAFT)(CFIFR.J*CIQR.J-CIAF.J)
    CIAF_K = CIAF_J + (DT / CIAFT) * (CFIFR_J * CIQR_J - CIAF_J)


print(f"RUN ORIG finished: TIME {results['TIME'][0]} to {results['TIME'][-1]}, "
      f"DT={DT}, {len(results['TIME']) - 1} steps")


# ---------------------------------------------------------------------------
# PLOT cards
#
#   PLOT  P=P(0,8E9)/POLR=2(0,40)/CI=C(0,20E9)/QL=Q(0,2)/NR=N(0,1000E9)
#   PLOT  FR=F,MSL=M,QLC=4,QLP=5(0,2)/CIAF=A(.2,.6)
#
# Each card is one graph. "P=P(0,8E9)" means: plot P with the symbol P on a
# scale from 0 to 8E9. Variables separated by commas share one scale, and
# slashes separate scales. All scales share the same vertical axis, so each
# curve is drawn as a fraction of its own scale (0 at the bottom, the scale's
# maximum at the top). The plot symbol is marked on each curve once every
# PLTPER years, as on the book's printer plots.
# ---------------------------------------------------------------------------

def dynamo_plot(name, curves, filename):
    """curves: list of (variable, symbol, scale_low, scale_high)."""
    import matplotlib.pyplot as plt
    time = results["TIME"]
    every = round(PLTPER_K / DT)          # one plot symbol per PLTPER years
    fig, ax = plt.subplots(figsize=(10, 6.5))
    for var, symbol, low, high in curves:
        fraction = [(v - low) / (high - low) for v in results[var]]
        ax.plot(time, fraction, color="black", linewidth=1,
                marker=f"${symbol}$", markevery=every, markersize=8,
                label=f"{var} = {symbol}   scale {low:g} to {high:g}")
    ax.set_xlim(time[0], time[-1])
    ax.set_ylim(0, 1)
    ax.set_xticks(range(1900, 2101, 40))
    ax.set_yticks([0, .25, .5, .75, 1])
    ax.set_yticklabels(["0", "1/4", "1/2", "3/4", "full"])
    ax.set_ylabel("fraction of each variable's scale")
    ax.set_xlabel("Years")
    ax.grid(True, linestyle=":", color="gray")
    ax.set_title(name)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.9)
    fig.tight_layout()
    fig.savefig(filename, dpi=120)
    return fig


try:
    import matplotlib.pyplot as plt
except ImportError:
    print("matplotlib is not installed, so the PLOT cards are skipped "
          "(pip install matplotlib to see them).")
else:
    #       PLOT    P=P(0,8E9)/POLR=2(0,40)/CI=C(0,20E9)/QL=Q(0,2)/NR=N(0,1000E9)
    dynamo_plot("ORIG-A", [
        ("P",    "P", 0, 8e9),
        ("POLR", "2", 0, 40),
        ("CI",   "C", 0, 20e9),
        ("QL",   "Q", 0, 2),
        ("NR",   "N", 0, 1000e9),
    ], "world2_1_isomorph_ORIG-A.png")

    #       PLOT    FR=F,MSL=M,QLC=4,QLP=5(0,2)/CIAF=A(.2,.6)
    dynamo_plot("ORIG-B", [
        ("FR",   "F", 0, 2),
        ("MSL",  "M", 0, 2),
        ("QLC",  "4", 0, 2),
        ("QLP",  "5", 0, 2),
        ("CIAF", "A", .2, .6),
    ], "world2_1_isomorph_ORIG-B.png")

    print("Plots saved to world2_1_isomorph_ORIG-A.png and world2_1_isomorph_ORIG-B.png")
    plt.show()

#       RUN     ORIG
