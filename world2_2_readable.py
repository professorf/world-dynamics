# SPDX-License-Identifier: MIT
"""
World2, readable names: the isomorph again, with every DYNAMO abbreviation spelled out.

Authors: Nick V. Flor (University of New Mexico, nickflor@unm.edu) and
         Claudia (Claude Interactive Assistant), i.e., Claude, an AI model by Anthropic.
License: MIT (see LICENSE). To cite this code, see CITE.md.
Model:   Jay W. Forrester's World2, from World Dynamics (1971; 2nd ed. 1973).

This is world2_1_isomorph.py line for line. The structure, the order of the
equations and the arithmetic are unchanged; only the names are different. Comparing
the two files side by side shows that nothing moved except the names.

Source: Jay W. Forrester, World Dynamics (2nd ed., 1973), Appendix B.
The DYNAMO listing is in source-code.dyn.

HOW THE NAMES WERE CHOSEN

Each name is the definition from definition-of-terms.md, written in snake_case:

    P     POPULATION                          ->  population
    MSL   MATERIAL STANDARD OF LIVING         ->  material_standard_of_living
    BRMMT BIRTH-RATE-FROM-MATERIAL-MULTIPLIER TABLE
                                              ->  birth_rate_from_material_multiplier_table

No new abbreviations were invented, so some names are long and a few lines wrap.
Every DYNAMO card is still shown as a comment above its line, so this file also
works as a lookup from DYNAMO names to readable ones.

HOW THE TIMING IS SHOWN

DYNAMO marked every value with its moment in time (J, K, L). Here:

    P.K, BR.KL    (now, and the rate for the coming interval)  ->  population, birth_rate
    P.J, BR.JK    (the previous moment, and the rate just used) ->  population_prev, birth_rate_prev

As in the isomorph, the auxiliaries inside the time loop are in computed order
rather than book order; each keeps its equation number.

Run:  python world2_2_readable.py
Uses only the Python standard library. If matplotlib is installed, the two PLOT
cards are drawn and saved as world2_2_readable_ORIG-A.png and world2_2_readable_ORIG-B.png.
"""

#       *       WORLD DYNAMICS W5


# ---------------------------------------------------------------------------
# DYNAMO functions used by the model (names kept, since the cards use them)
# ---------------------------------------------------------------------------

def CLIP(A, B, X, Y):
    """DYNAMO CLIP: A if X >= Y, otherwise B.

    The model uses it as a time switch. CLIP(birth_rate_normal,
    birth_rate_normal_1, switch_time_1, time) gives birth_rate_normal up to the
    switch time, and birth_rate_normal_1 after it.
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
        print(f"TABLE warning at time={time}: input {X:.4g} is outside {XLOW}..{XHIGH}")
    return TABHL(TAB, X, XLOW, XHIGH, XINCR)


# ---------------------------------------------------------------------------
# Constants (C) and tables (T), in book order
# ---------------------------------------------------------------------------

# 1.2   C   PI=1.65E9
population_initial = 1.65e9
# 2.2   C   BRN=.04
birth_rate_normal = .04
# 2.3   C   BRN1=.04
birth_rate_normal_1 = .04
# 2.4   C   SWT1=1970
switch_time_1 = 1970
# 3.1   T   BRMMT=1.2/1/.85/.75/.7/.7
birth_rate_from_material_multiplier_table = [1.2, 1, .85, .75, .7, .7]
# 4.1   C   ECIRN=1
effective_capital_investment_ratio_normal = 1
# 6.1   T   NREMT=0/.15/.5/.85/1
natural_resource_extraction_multiplier_table = [0, .15, .5, .85, 1]
# 8.2   C   NRI=900E9
natural_resources_initial = 900e9
# 9.1   C   NRUN=1
natural_resource_usage_normal = 1
# 9.2   C   NRUN1=1
natural_resource_usage_normal_1 = 1
# 9.3   C   SWT2=1970
switch_time_2 = 1970
# 10.2  C   DRN=.028
death_rate_normal = .028
# 10.3  C   DRN1=.028
death_rate_normal_1 = .028
# 10.4  C   SWT3=1970
switch_time_3 = 1970
# 11.1  T   DRMMT=3/1.8/1/.8/.7/.6/.53/.5/.5/.5/.5
death_rate_from_material_multiplier_table = [3, 1.8, 1, .8, .7, .6, .53, .5, .5, .5, .5]
# 12.1  T   DRPMT=.92/1.3/2/3.2/4.8/6.8/9.2
death_rate_from_pollution_multiplier_table = [.92, 1.3, 2, 3.2, 4.8, 6.8, 9.2]
# 13.1  T   DRFMT=30/3/2/1.4/1/.7/.6/.5/.5
death_rate_from_food_multiplier_table = [30, 3, 2, 1.4, 1, .7, .6, .5, .5]
# 14.1  T   DRCMT=.9/1/1.2/1.5/1.9/3
death_rate_from_crowding_multiplier_table = [.9, 1, 1.2, 1.5, 1.9, 3]
# 15.1  C   LA=135E6
land_area = 135e6
# 15.2  C   PDN=26.5
population_density_normal = 26.5
# 16.1  T   BRCMT=1.05/1/.9/.7/.6/.55
birth_rate_from_crowding_multiplier_table = [1.05, 1, .9, .7, .6, .55]
# 17.1  T   BRFMT=0/1/1.6/1.9/2
birth_rate_from_food_multiplier_table = [0, 1, 1.6, 1.9, 2]
# 18.1  T   BRPMT=1.02/.9/.7/.4/.25/.15/.1
birth_rate_from_pollution_multiplier_table = [1.02, .9, .7, .4, .25, .15, .1]
# 19.1  C   FC=1
food_coefficient = 1
# 19.2  C   FC1=1
food_coefficient_1 = 1
# 19.3  C   FN=1
food_normal = 1
# 19.4  C   SWT7=1970
switch_time_7 = 1970
# 20.1  T   FCMT=2.4/1/.6/.4/.3/.2
food_from_crowding_multiplier_table = [2.4, 1, .6, .4, .3, .2]
# 21.1  T   FPCIT=.5/1/1.4/1.7/1.9/2.05/2.2
food_potential_from_capital_investment_table = [.5, 1, 1.4, 1.7, 1.9, 2.05, 2.2]
# 22.1  C   CIAFN=.3
capital_investment_in_agriculture_fraction_normal = .3
# 24.2  C   CII=.4E9
capital_investment_initial = .4e9
# 25.1  C   CIGN=.05
capital_investment_generation_normal = .05
# 25.2  C   CIGN1=.05
capital_investment_generation_normal_1 = .05
# 25.3  C   SWT4=1970
switch_time_4 = 1970
# 26.1  T   CIMT=.1/1/1.8/2.4/2.8/3
capital_investment_multiplier_table = [.1, 1, 1.8, 2.4, 2.8, 3]
# 27.1  C   CIDN=.025
capital_investment_discard_normal = .025
# 27.2  C   CIDN1=.025
capital_investment_discard_normal_1 = .025
# 27.3  C   SWT5=1970
switch_time_5 = 1970
# 28.1  T   FPMT=1.02/.9/.65/.35/.2/.1/.05
food_from_pollution_multiplier_table = [1.02, .9, .65, .35, .2, .1, .05]
# 29.1  C   POLS=3.6E9
pollution_standard = 3.6e9
# 30.2  C   POLI=.2E9
pollution_initial = .2e9
# 31.1  C   POLN=1
pollution_normal = 1
# 31.2  C   POLN1=1
pollution_normal_1 = 1
# 31.3  C   SWT6=1970
switch_time_6 = 1970
# 32.1  T   POLCMT=.05/1/3/5.4/7.4/8
pollution_from_capital_multiplier_table = [.05, 1, 3, 5.4, 7.4, 8]
# 34.1  T   POLATT=.6/2.5/5/8/11.5/15.5/20
pollution_absorption_time_table = [.6, 2.5, 5, 8, 11.5, 15.5, 20]
# 35.2  C   CIAFI=.2
capital_investment_in_agriculture_fraction_initial = .2
# 35.3  C   CIAFT=15
capital_investment_in_agriculture_fraction_adjustment_time = 15
# 36.1  T   CFIFRT=1/.6/.3/.15/.1
capital_fraction_indicated_by_food_ratio_table = [1, .6, .3, .15, .1]
# 37.1  C   QLS=1
quality_of_life_standard = 1
# 38.1  T   QLMT=.2/1/1.7/2.3/2.7/2.9
quality_of_life_from_material_table = [.2, 1, 1.7, 2.3, 2.7, 2.9]
# 39.1  T   QLCT=2/1.3/1/.75/.55/.45/.38/.3/.25/.22/.2
quality_of_life_from_crowding_table = [2, 1.3, 1, .75, .55, .45, .38, .3, .25, .22, .2]
# 40.1  T   QLFT=0/1/1.8/2.4/2.7
quality_of_life_from_food_table = [0, 1, 1.8, 2.4, 2.7]
# 41.1  T   QLPT=1.04/.85/.6/.3/.15/.05/.02
quality_of_life_from_pollution_table = [1.04, .85, .6, .3, .15, .05, .02]
# 42.1  T   NRMMT=0/1/1.8/2.4/2.9/3.3/3.6/3.8/3.9/3.95/4
natural_resource_from_material_multiplier_table = [0, 1, 1.8, 2.4, 2.9, 3.3, 3.6, 3.8, 3.9, 3.95, 4]
# 43.1  T   CIQRT=.7/.8/1/1.5/2
capital_investment_from_quality_ratio_table = [.7, .8, 1, 1.5, 2]

#       NOTE    CONTROL CARDS
# 43.5  C   DT=.2
dt = .2                     # the time step, in years
# 43.6  C   LENGTH=2100
final_time = 2100           # the run stops when time reaches this year
# 44.1  C   PRTP1=0
print_period_1 = 0
# 44.2  C   PRTP2=0
print_period_2 = 0
# 44.3  C   PRSWT=0
print_switch_time = 0
# 45.1  C   PLTP1=4
plot_period_1 = 4
# 45.2  C   PLTP2=4
plot_period_2 = 4
# 45.3  C   PLSWT=0
plot_switch_time = 0


# ---------------------------------------------------------------------------
# Initial values (N): the levels and time at the first moment
# ---------------------------------------------------------------------------

# 1.1   N   P=PI
population = population_initial
# 8.1   N   NR=NRI
natural_resources = natural_resources_initial
# 24.1  N   CI=CII
capital_investment = capital_investment_initial
# 30.1  N   POL=POLI
pollution = pollution_initial
# 35.1  N   CIAF=CIAFI
capital_investment_in_agriculture_fraction = capital_investment_in_agriculture_fraction_initial
# 43.7  N   TIME=1900
time = 1900


# ---------------------------------------------------------------------------
# What we keep from the run (DYNAMO printed and plotted; we record)
# ---------------------------------------------------------------------------

results = {name: [] for name in [
    "time",
    # levels
    "population", "natural_resources", "capital_investment", "pollution",
    "capital_investment_in_agriculture_fraction",
    # rates
    "birth_rate", "death_rate", "natural_resource_usage_rate",
    "capital_investment_generation", "capital_investment_discard",
    "pollution_generation", "pollution_absorption",
    # auxiliaries on the book's plots
    "pollution_ratio", "quality_of_life", "food_ratio", "material_standard_of_living",
    "quality_of_life_from_crowding", "quality_of_life_from_pollution",
]}


# ---------------------------------------------------------------------------
# The time loop. Each pass is one moment in time:
#   1. auxiliaries now, from the levels now
#   2. rates for the coming interval
#   3. record, and stop if time has reached final_time
#   4. time moves on: current values become the _prev values
#   5. levels at the new time, from the previous levels and rates
# ---------------------------------------------------------------------------

while True:

    # ======== 1. Auxiliaries now (in computed order) ========

    # 7     A   NRFR.K=NR.K/NRI
    natural_resource_fraction_remaining = natural_resources / natural_resources_initial
    # 6     A   NREM.K=TABLE(NREMT,NRFR.K,0,1,.25)
    natural_resource_extraction_multiplier = TABLE(
        natural_resource_extraction_multiplier_table,
        natural_resource_fraction_remaining, 0, 1, .25)
    # 23    A   CIR.K=CI.K/P.K
    capital_investment_ratio = capital_investment / population
    # 5     A   ECIR.K=(CIR.K)(1-CIAF.K)(NREM.K)/(1-CIAFN)
    effective_capital_investment_ratio = (
        capital_investment_ratio
        * (1 - capital_investment_in_agriculture_fraction)
        * natural_resource_extraction_multiplier
        / (1 - capital_investment_in_agriculture_fraction_normal))
    # 4     A   MSL.K=ECIR.K/(ECIRN)
    material_standard_of_living = (effective_capital_investment_ratio
                                   / effective_capital_investment_ratio_normal)

    # 3     A   BRMM.K=TABHL(BRMMT,MSL.K,0,5,1)
    birth_rate_from_material_multiplier = TABHL(
        birth_rate_from_material_multiplier_table,
        material_standard_of_living, 0, 5, 1)
    # 11    A   DRMM.K=TABHL(DRMMT,MSL.K,0,5,.5)
    death_rate_from_material_multiplier = TABHL(
        death_rate_from_material_multiplier_table,
        material_standard_of_living, 0, 5, .5)
    # 26    A   CIM.K=TABHL(CIMT,MSL.K,0,5,1)
    capital_investment_multiplier = TABHL(
        capital_investment_multiplier_table,
        material_standard_of_living, 0, 5, 1)
    #       NOTE    EQUATION 42 CONNECTS HERE FROM EQ. 4 TO EQ. 9
    # 42    A   NRMM.K=TABHL(NRMMT,MSL.K,0,10,1)
    natural_resource_from_material_multiplier = TABHL(
        natural_resource_from_material_multiplier_table,
        material_standard_of_living, 0, 10, 1)
    # 38    A   QLM.K=TABHL(QLMT,MSL.K,0,5,1)
    quality_of_life_from_material = TABHL(
        quality_of_life_from_material_table,
        material_standard_of_living, 0, 5, 1)

    # 15    A   CR.K=(P.K)/(LA*PDN)
    crowding_ratio = population / (land_area * population_density_normal)
    # 16    A   BRCM.K=TABLE(BRCMT,CR.K,0,5,1)
    birth_rate_from_crowding_multiplier = TABLE(
        birth_rate_from_crowding_multiplier_table, crowding_ratio, 0, 5, 1)
    # 14    A   DRCM.K=TABLE(DRCMT,CR.K,0,5,1)
    death_rate_from_crowding_multiplier = TABLE(
        death_rate_from_crowding_multiplier_table, crowding_ratio, 0, 5, 1)
    # 20    A   FCM.K=TABLE(FCMT,CR.K,0,5,1)
    food_from_crowding_multiplier = TABLE(
        food_from_crowding_multiplier_table, crowding_ratio, 0, 5, 1)
    # 39    A   QLC.K=TABLE(QLCT,CR.K,0,5,.5)
    quality_of_life_from_crowding = TABLE(
        quality_of_life_from_crowding_table, crowding_ratio, 0, 5, .5)

    # 29    A   POLR.K=POL.K/POLS
    pollution_ratio = pollution / pollution_standard
    # 18    A   BRPM.K=TABLE(BRPMT,POLR.K,0,60,10)
    birth_rate_from_pollution_multiplier = TABLE(
        birth_rate_from_pollution_multiplier_table, pollution_ratio, 0, 60, 10)
    # 12    A   DRPM.K=TABLE(DRPMT,POLR.K,0,60,10)
    death_rate_from_pollution_multiplier = TABLE(
        death_rate_from_pollution_multiplier_table, pollution_ratio, 0, 60, 10)
    # 28    A   FPM.K=TABLE(FPMT,POLR.K,0,60,10)
    food_from_pollution_multiplier = TABLE(
        food_from_pollution_multiplier_table, pollution_ratio, 0, 60, 10)
    # 34    A   POLAT.K=TABLE(POLATT,POLR.K,0,60,10)
    pollution_absorption_time = TABLE(
        pollution_absorption_time_table, pollution_ratio, 0, 60, 10)
    # 32    A   POLCM.K=TABHL(POLCMT,CIR.K,0,5,1)
    pollution_from_capital_multiplier = TABHL(
        pollution_from_capital_multiplier_table, capital_investment_ratio, 0, 5, 1)
    # 41    A   QLP.K=TABLE(QLPT,POLR.K,0,60,10)
    quality_of_life_from_pollution = TABLE(
        quality_of_life_from_pollution_table, pollution_ratio, 0, 60, 10)

    # 22    A   CIRA.K=(CIR.K)(CIAF.K)/CIAFN
    capital_investment_ratio_in_agriculture = (
        capital_investment_ratio
        * capital_investment_in_agriculture_fraction
        / capital_investment_in_agriculture_fraction_normal)
    # 21    A   FPCI.K=TABHL(FPCIT,CIRA.K,0,6,1)
    food_potential_from_capital_investment = TABHL(
        food_potential_from_capital_investment_table,
        capital_investment_ratio_in_agriculture, 0, 6, 1)
    # 19    A   FR.K=(FPCI.K)(FCM.K)(FPM.K)(CLIP(FC,FC1,SWT7,TIME.K))/FN
    food_ratio = (food_potential_from_capital_investment
                  * food_from_crowding_multiplier
                  * food_from_pollution_multiplier
                  * CLIP(food_coefficient, food_coefficient_1, switch_time_7, time)
                  / food_normal)
    # 17    A   BRFM.K=TABHL(BRFMT,FR.K,0,4,1)
    birth_rate_from_food_multiplier = TABHL(
        birth_rate_from_food_multiplier_table, food_ratio, 0, 4, 1)
    # 13    A   DRFM.K=TABHL(DRFMT,FR.K,0,2,.25)
    death_rate_from_food_multiplier = TABHL(
        death_rate_from_food_multiplier_table, food_ratio, 0, 2, .25)
    # 36    A   CFIFR.K=TABHL(CFIFRT,FR.K,0,2,.5)
    capital_fraction_indicated_by_food_ratio = TABHL(
        capital_fraction_indicated_by_food_ratio_table, food_ratio, 0, 2, .5)
    # 40    A   QLF.K=TABHL(QLFT,FR.K,0,4,1)
    quality_of_life_from_food = TABHL(
        quality_of_life_from_food_table, food_ratio, 0, 4, 1)

    #       NOTE    INPUT FROM EQN. 38 AND 40 TO EQN. 35
    # 43    A   CIQR.K=TABHL(CIQRT,QLM.K/QLF.K,0,2,.5)
    capital_investment_from_quality_ratio = TABHL(
        capital_investment_from_quality_ratio_table,
        quality_of_life_from_material / quality_of_life_from_food, 0, 2, .5)
    # 37    S   QL.K=(QLS)(QLM.K)(QLC.K)(QLF.K)(QLP.K)
    quality_of_life = (quality_of_life_standard
                       * quality_of_life_from_material
                       * quality_of_life_from_crowding
                       * quality_of_life_from_food
                       * quality_of_life_from_pollution)

    # ======== 2. Rates for the coming interval ========

    # 2     R   BR.KL=(P.K)(CLIP(BRN,BRN1,SWT1,TIME.K))(BRFM.K)(BRMM.K)(BRCM.K)(BR
    #       X   PM.K)
    birth_rate = (population
                  * CLIP(birth_rate_normal, birth_rate_normal_1, switch_time_1, time)
                  * birth_rate_from_food_multiplier
                  * birth_rate_from_material_multiplier
                  * birth_rate_from_crowding_multiplier
                  * birth_rate_from_pollution_multiplier)
    # 10    R   DR.KL=(P.K)(CLIP(DRN,DRN1,SWT3,TIME.K))(DRMM.K)(DRPM.K)(DRFM.K)(DR
    #       X   CM.K)
    death_rate = (population
                  * CLIP(death_rate_normal, death_rate_normal_1, switch_time_3, time)
                  * death_rate_from_material_multiplier
                  * death_rate_from_pollution_multiplier
                  * death_rate_from_food_multiplier
                  * death_rate_from_crowding_multiplier)
    # 9     R   NRUR.KL=(P.K)(CLIP(NRUN,NRUN1,SWT2,TIME.K))(NRMM.K)
    natural_resource_usage_rate = (
        population
        * CLIP(natural_resource_usage_normal, natural_resource_usage_normal_1,
               switch_time_2, time)
        * natural_resource_from_material_multiplier)
    # 25    R   CIG.KL=(P.K)(CIM.K)(CLIP(CIGN,CIGN1,SWT4,TIME.K))
    capital_investment_generation = (
        population
        * capital_investment_multiplier
        * CLIP(capital_investment_generation_normal,
               capital_investment_generation_normal_1, switch_time_4, time))
    # 27    R   CID.KL=(CI.K)(CLIP(CIDN,CIDN1,SWT5,TIME.K))
    capital_investment_discard = (
        capital_investment
        * CLIP(capital_investment_discard_normal,
               capital_investment_discard_normal_1, switch_time_5, time))
    # 31    R   POLG.KL=(P.K)(CLIP(POLN,POLN1,SWT6,TIME.K))(POLCM.K)
    pollution_generation = (population
                            * CLIP(pollution_normal, pollution_normal_1, switch_time_6, time)
                            * pollution_from_capital_multiplier)
    # 33    R   POLA.KL=POL.K/POLAT.K
    pollution_absorption = pollution / pollution_absorption_time

    # Print and plot periods (DYNAMO output control)
    # 44    A   PRTPER.K=CLIP(PRTP1,PRTP2,PRSWT,TIME.K)
    print_period = CLIP(print_period_1, print_period_2, print_switch_time, time)
    # 45    A   PLTPER.K=CLIP(PLTP1,PLTP2,PLSWT,TIME.K)
    plot_period = CLIP(plot_period_1, plot_period_2, plot_switch_time, time)

    # ======== 3. Record this moment, and stop at the end of the run ========

    results["time"].append(time)
    results["population"].append(population)
    results["natural_resources"].append(natural_resources)
    results["capital_investment"].append(capital_investment)
    results["pollution"].append(pollution)
    results["capital_investment_in_agriculture_fraction"].append(
        capital_investment_in_agriculture_fraction)
    results["birth_rate"].append(birth_rate)
    results["death_rate"].append(death_rate)
    results["natural_resource_usage_rate"].append(natural_resource_usage_rate)
    results["capital_investment_generation"].append(capital_investment_generation)
    results["capital_investment_discard"].append(capital_investment_discard)
    results["pollution_generation"].append(pollution_generation)
    results["pollution_absorption"].append(pollution_absorption)
    results["pollution_ratio"].append(pollution_ratio)
    results["quality_of_life"].append(quality_of_life)
    results["food_ratio"].append(food_ratio)
    results["material_standard_of_living"].append(material_standard_of_living)
    results["quality_of_life_from_crowding"].append(quality_of_life_from_crowding)
    results["quality_of_life_from_pollution"].append(quality_of_life_from_pollution)

    if time >= final_time:
        break

    # ======== 4. Time moves on: current values become the _prev values ========

    time_prev = time
    population_prev = population
    natural_resources_prev = natural_resources
    capital_investment_prev = capital_investment
    pollution_prev = pollution
    capital_investment_in_agriculture_fraction_prev = capital_investment_in_agriculture_fraction
    # equation 35 uses these two auxiliaries at the previous moment
    capital_fraction_indicated_by_food_ratio_prev = capital_fraction_indicated_by_food_ratio
    capital_investment_from_quality_ratio_prev = capital_investment_from_quality_ratio
    birth_rate_prev = birth_rate
    death_rate_prev = death_rate
    natural_resource_usage_rate_prev = natural_resource_usage_rate
    capital_investment_generation_prev = capital_investment_generation
    capital_investment_discard_prev = capital_investment_discard
    pollution_generation_prev = pollution_generation
    pollution_absorption_prev = pollution_absorption

    # ======== 5. Levels at the new time (book order) ========

    # Adding 0.2 over and over drifts in binary floating point (1900 + 0.2 + 0.2 ...
    # never lands exactly on 1970), so time is rounded. Without it, the 1970
    # switches and the stop at final_time could fire one step early or late.
    time = round(time_prev + dt, 6)

    # 1     L   P.K=P.J+(DT)(BR.JK-DR.JK)
    population = population_prev + dt * (birth_rate_prev - death_rate_prev)
    # 8     L   NR.K=NR.J+(DT)(-NRUR.JK)
    natural_resources = natural_resources_prev + dt * (-natural_resource_usage_rate_prev)
    # 24    L   CI.K=CI.J+(DT)(CIG.JK-CID.JK)
    capital_investment = capital_investment_prev + dt * (
        capital_investment_generation_prev - capital_investment_discard_prev)
    # 30    L   POL.K=POL.J+(DT)(POLG.JK-POLA.JK)
    pollution = pollution_prev + dt * (pollution_generation_prev - pollution_absorption_prev)
    # 35    L   CIAF.K=CIAF.J+(DT/CIAFT)(CFIFR.J*CIQR.J-CIAF.J)
    capital_investment_in_agriculture_fraction = (
        capital_investment_in_agriculture_fraction_prev
        + (dt / capital_investment_in_agriculture_fraction_adjustment_time)
        * (capital_fraction_indicated_by_food_ratio_prev
           * capital_investment_from_quality_ratio_prev
           - capital_investment_in_agriculture_fraction_prev))


print(f"RUN ORIG finished: time {results['time'][0]} to {results['time'][-1]}, "
      f"dt={dt}, {len(results['time']) - 1} steps")


# ---------------------------------------------------------------------------
# PLOT cards
#
#   PLOT  P=P(0,8E9)/POLR=2(0,40)/CI=C(0,20E9)/QL=Q(0,2)/NR=N(0,1000E9)
#   PLOT  FR=F,MSL=M,QLC=4,QLP=5(0,2)/CIAF=A(.2,.6)
#
# Each card is one graph. "P=P(0,8E9)" means: plot population with the symbol P
# on a scale from 0 to 8E9. Variables separated by commas share one scale, and
# slashes separate scales. All scales share the same vertical axis, so each
# curve is drawn as a fraction of its own scale (0 at the bottom, the scale's
# maximum at the top). The plot symbol is marked on each curve once every
# plot_period years, as on the book's printer plots.
# ---------------------------------------------------------------------------

def dynamo_plot(name, curves, filename):
    """curves: list of (variable, symbol, scale_low, scale_high)."""
    import matplotlib.pyplot as plt
    times = results["time"]
    every = round(plot_period / dt)       # one plot symbol per plot_period years
    fig, ax = plt.subplots(figsize=(10, 6.5))
    for var, symbol, low, high in curves:
        fraction = [(v - low) / (high - low) for v in results[var]]
        ax.plot(times, fraction, color="black", linewidth=1,
                marker=f"${symbol}$", markevery=every, markersize=8,
                label=f"{var} = {symbol}   scale {low:g} to {high:g}")
    ax.set_xlim(times[0], times[-1])
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
        ("population",         "P", 0, 8e9),
        ("pollution_ratio",    "2", 0, 40),
        ("capital_investment", "C", 0, 20e9),
        ("quality_of_life",    "Q", 0, 2),
        ("natural_resources",  "N", 0, 1000e9),
    ], "world2_2_readable_ORIG-A.png")

    #       PLOT    FR=F,MSL=M,QLC=4,QLP=5(0,2)/CIAF=A(.2,.6)
    dynamo_plot("ORIG-B", [
        ("food_ratio",                                 "F", 0, 2),
        ("material_standard_of_living",                "M", 0, 2),
        ("quality_of_life_from_crowding",              "4", 0, 2),
        ("quality_of_life_from_pollution",             "5", 0, 2),
        ("capital_investment_in_agriculture_fraction", "A", .2, .6),
    ], "world2_2_readable_ORIG-B.png")

    print("Plots saved to world2_2_readable_ORIG-A.png and world2_2_readable_ORIG-B.png")
    plt.show()

#       RUN     ORIG
