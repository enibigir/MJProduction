import sys,os

process_name = "multijet"
if len(sys.argv)>1:
    process_name = sys.argv[1]

cards_dir="temp_cards"

default_process_card="""
import model RPVMSSM_UFO
define q =  u c d s u~ c~ d~ s~
define hg = n1 n2 x1+ x1-
define sq = ul ul~ dl dl~ ur ur~ dr dr~
generate p p > go go QED=0, (go > q q hg, (hg > q q q)) , (go > q q hg, (hg > q q q))
output {PROCESS} --nojpeg
""".format(PROCESS=process_name)

default_customizecards="""
set param_card mass   1000001     1.00000000E+05
set param_card mass   2000001     1.00000000E+05
set param_card mass   1000002     1.00000000E+05
set param_card mass   2000002     1.00000000E+05
set param_card mass   1000003     1.00000000E+05
set param_card mass   2000003     1.00000000E+05
set param_card mass   1000004     1.00000000E+05
set param_card mass   2000004     1.00000000E+05
set param_card mass   1000005     1.00000000E+05
set param_card mass   2000005     1.00000000E+05
set param_card mass   1000006     1.00000000E+05
set param_card mass   2000006     1.00000000E+05
set param_card mass   1000011     1.00000000E+05
set param_card mass   2000011     1.00000000E+05
set param_card mass   1000012     1.00000000E+05
set param_card mass   1000013     1.00000000E+05
set param_card mass   2000013     1.00000000E+05
set param_card mass   1000014     1.00000000E+05
set param_card mass   1000015     1.00000000E+05
set param_card mass   2000015     1.00000000E+05
set param_card mass   1000016     1.00000000E+05
set param_card mass   1000021     1000          
set param_card mass   1000022     300           
set param_card mass   1000023     300           
set param_card mass   1000025     1.00000000E+05
set param_card mass   1000035     1.00000000E+05
set param_card mass   1000024     300           
set param_card mass   1000037     1.00000000E+05
"""

default_run_card="""
tag_1     = run_tag ! name of the run 
10000 = nevents ! Number of unweighted events requested 
0   = iseed   ! rnd seed (0=assigned automatically=default))
1        = lpp1    ! beam 1 type 
1        = lpp2    ! beam 2 type
6800.0     = ebeam1  ! beam 1 total energy in GeV
6800.0     = ebeam2  ! beam 2 total energy in GeV
#
lhapdf    = pdlabel     ! PDF set                     
$DEFAULT_PDF_SETS    = lhaid     ! if pdlabel=lhapdf, this is the lhapdf number
#
False = fixed_ren_scale  ! if .true. use fixed ren scale
False        = fixed_fac_scale  ! if .true. use fixed fac scale
91.188  = scale            ! fixed ren scale
91.188  = dsqrt_q2fact1    ! fixed fact scale for pdf1
91.188  = dsqrt_q2fact2    ! fixed fact scale for pdf2
-1 = dynamical_scale_choice ! Choose one of the preselected dynamical choices
1.0  = scalefact        ! scale factor for event-by-event scales
#
 1    = ickkw            ! 0 no matching, 1 MLM, 2 CKKW matching
 1.0  = alpsfact         ! scale factor for QCD emission vx
 1    = ktscheme         ! for ickkw=1, 1 Durham kT, 2 Pythia pTE
 30   = xqcut            ! minimum kt jet measure between partons
 True = auto_ptj_mjj  ! Automatic setting of ptj and mjj
#
False     = gridpack  !True = setting up the grid pack
-1.0 = time_of_flight ! threshold (in mm) below which the invariant livetime is not written (-1 means not written)
average =  event_norm       ! average/sum. Normalization of the weight in the LHEF
#
0  = nhel          ! using helicities importance sampling or not.
                   ! 0: sum over helicity, 1: importance sampling
1  = sde_strategy  ! default integration strategy (hep-ph/2021.00773)
                   ! 1 is old strategy (using amp square)
                   ! 2 is new strategy (using only the denominator)
#
None = bias_module  ! Bias type of bias, [None, ptj_bias, -custom_folder-]
#
15.0  = bwcutoff      ! (M+/-bwcutoff*Gamma)
#
False  = cut_decays    ! Cut decay products 
#
10.0  = ptj       ! minimum pt for the jets 
-1.0  = ptjmax    ! maximum pt for the jets
 5.0  = etaj    ! max rap for the jets 
#
 0.4  = drjj    ! min distance between jets 
-1.0  = drjjmax ! max distance between jets
#
 0.0  = mmjj    ! min invariant mass of a jet pair 
-1.0  = mmjjmax ! max invariant mass of a jet pair
#
 0.0  = ptheavy   ! minimum pt for at least one heavy final state
 0.0  = xptj ! minimum pt for at least one jet  
#
 0.0   = ptj1min ! minimum pt for the leading jet in pt
 0.0   = ptj2min ! minimum pt for the second jet in pt
 0.0   = ptj3min ! minimum pt for the third jet in pt
 0.0   = ptj4min ! minimum pt for the fourth jet in pt
 -1.0  = ptj1max ! maximum pt for the leading jet in pt 
 -1.0  = ptj2max ! maximum pt for the second jet in pt
 -1.0  = ptj3max ! maximum pt for the third jet in pt
 -1.0  = ptj4max ! maximum pt for the fourth jet in pt
 0   = cutuse  ! reject event if fails any (0) / all (1) jet pt cuts
#
 0.0   = htjmin ! minimum jet HT=Sum(jet pt)
 -1.0  = htjmax ! maximum jet HT=Sum(jet pt)
 0.0   = ihtmin  !inclusive Ht for all partons (including b)
 -1.0  = ihtmax  !inclusive Ht for all partons (including b)
 0.0   = ht2min ! minimum Ht for the two leading jets
 0.0   = ht3min ! minimum Ht for the three leading jets
 0.0   = ht4min ! minimum Ht for the four leading jets
 -1.0  = ht2max ! maximum Ht for the two leading jets
 -1.0  = ht3max ! maximum Ht for the three leading jets
 -1.0  = ht4max ! maximum Ht for the four leading jets
#
 0.0   = xetamin ! minimum rapidity for two jets in the WBF case  
 0.0   = deltaeta ! minimum rapidity for two jets in the WBF case 
#
 4 = maxjetflavor    ! Maximum jet pdg code
#
   True  = use_syst      ! Enable systematics studies
#
systematics = systematics_program ! none, systematics [python], SysCalc [depreceted, C++]
['--mur=0.5,1,2', '--muf=0.5,1,2', '--pdf=errorset'] = systematics_arguments ! see: https://cp3.irmp.ucl.ac.be/projects/madgraph/wiki/Systematics#Systematicspythonmodule
# Syscalc is deprecated but to see the associate options type'update syscalc'
"""

def pprint(t=""):
    print(f'[MJ] {t}') if t else print()

if __name__=="__main__":
    pprint('Start')
    proc_dir = f'{cards_dir}/{process_name}'
    if not os.path.isdir(proc_dir):
        pprint(f'Creating directory: {proc_dir}')
        os.system(f'mkdir -p {proc_dir}')

    pprint(f'Writing all cards inside {proc_dir}')
    with open(f'{proc_dir}/{process_name}_proc_card.dat','w') as f:
        f.write(default_process_card)
    with open(f'{proc_dir}/{process_name}_customizecards.dat','w') as f:
        f.write(default_customizecards)
    with open(f'{proc_dir}/{process_name}_run_card.dat','w') as f:
        f.write(default_run_card)
    pprint('Done')