echo "Running:"
echo "$0"
echo "$1"
echo "$2"

echo "/store/user/jrotter/EMTF_BDT_Train_Mode15_$2_eta1.25to2.4_isRun2_Selection0xf41f11ff_20211109_170445/PtRegressionOutput.root"

echo "Mode 15:"
python3 $1 --emtf-mode=15 --pt-cuts="[5, 11, 22, 30]" --eta-mins="[1.25]" --verbose=True --eta-maxs="[2.4]" $2 eff_mode15.pdf "/store/user/jrotter/EMTF_BDT_Train_Mode15_$2_eta1.25to2.4_isRun2_Selection0xf41f11ff_20211110_110123/PtRegressionOutput.root"
echo "Done, moving to next mode..."

echo "Mode 14:"
python3 $1 --emtf-mode=14 --pt-cuts="[5, 11, 22, 30]" --eta-mins="[1.25]" --eta-maxs="[2.4]" $2 eff_mode14.pdf "/store/user/jrotter/EMTF_BDT_Train_Mode14_$2_eta1.25to2.4_isRun2_Selection0x7200132f_20211110_110342/PtRegressionOutput.root"
echo "Done, moving to next mode..."

echo "Mode 13:"
python3 $1 --emtf-mode=13 --pt-cuts="[5, 11, 22, 30]" --eta-mins="[1.25]" --eta-maxs="[2.4]" $2 eff_mode13.pdf "/store/user/jrotter/EMTF_BDT_Train_Mode13_$2_eta1.25to2.4_isRun2_Selection0xb40013c7_20211111_140907/PtRegressionOutput.root"

echo "Mode 12:"
python3 $1 --emtf-mode=12 --pt-cuts="[5, 11, 22, 30]" --eta-mins="[1.25]" --eta-maxs="[2.4]" $2 eff_mode12.pdf "/store/user/jrotter/EMTF_BDT_Train_Mode12_$2_eta1.25to2.4_isRun2_Selection0x30403307_20211111_141103/PtRegressionOutput.root"
echo "Done, moving to next mode..."

echo "Mode 11:"
python3 $1 --emtf-mode=11 --pt-cuts="[5, 11, 22, 30]" --eta-mins="[1.25]" --eta-maxs="[2.4]" $2 eff_mode11.pdf "/store/user/jrotter/EMTF_BDT_Train_Mode11_$2_eta1.25to2.4_isRun2_Selection0xd4001573_20211111_141243/PtRegressionOutput.root"
echo "Done, moving to next mode..."

echo "Mode 10:"
python3 $1 --emtf-mode=10 --pt-cuts="[5, 11, 22, 30]" --eta-mins="[1.25]" --eta-maxs="[2.4]" $2 eff_mode10.pdf "/store/user/jrotter/EMTF_BDT_Train_Mode10_$2_eta1.25to2.4_isRun2_Selection0x52005523_20211111_141407/PtRegressionOutput.root"
echo "Done, moving to next mode..."

echo "Mode 9:"
python3 $1 --emtf-mode=9 --pt-cuts="[5, 11, 22, 30]" --eta-mins="[1.25]" --eta-maxs="[2.4]" $2 eff_mode9.pdf "/store/user/jrotter/EMTF_BDT_Train_Mode9_$2_eta1.25to2.4_isRun2_Selection0x94009943_20211111_144137/PtRegressionOutput.root"
echo "Done, moving to next mode..."

echo "Mode 7:"
python3 $1 --emtf-mode=7 --pt-cuts="[5, 11, 22, 30]" --eta-mins="[1.25]" --eta-maxs="[2.4]" $2 eff_mode7.pdf "/store/user/jrotter/EMTF_BDT_Train_Mode7_$2_eta1.25to2.4_isRun2_Selection0xe8002299_20211111_144703/PtRegressionOutput.root"
echo "Done, moving to next mode..."

echo "Mode 6:"
python3 $1 --emtf-mode=6 --pt-cuts="[5, 11, 22, 30]" --eta-mins="[1.25]" --eta-maxs="[2.4]" $2 eff_mode6.pdf "/store/user/jrotter/EMTF_BDT_Train_Mode6_$2_eta1.25to2.4_isRun2_Selection0x60806609_20211111_145226/PtRegressionOutput.root"
echo "Done, moving to next mode..."

echo "Mode 5:"
python3 $1 --emtf-mode=5 --pt-cuts="[5, 11, 22, 30]" --eta-mins="[1.25]" --eta-maxs="[2.4]" $2 eff_mode5.pdf "/store/user/jrotter/EMTF_BDT_Train_Mode5_$2_eta1.25to2.4_isRun2_Selection0xa800aa81_20211111_145543/PtRegressionOutput.root"
echo "Done, moving to next mode..."

echo "Mode 3:"
python3 $1 --emtf-mode=3 --pt-cuts="[5, 11, 22, 30]" --eta-mins="[1.25]" --eta-maxs="[2.4]" $2 eff_mode3.pdf "/store/user/jrotter/EMTF_BDT_Train_Mode3_$2_eta1.25to2.4_isRun2_Selection0xc100cc11_20211111_155351/PtRegressionOutput.root"

echo "Complete."

