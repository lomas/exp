::cluster number K is a global parameter across all modules
@setlocal enableDelayedExpansion

@set K=1024
@set modelpath=models\model.pkl
@set rulepath=rules.txt

@set siftdir=sift\
@set clusterdir=cluster\
@set transcdir=transcdir\

mkdir sift
mkdir cluster
mkdir transc

python siftfeat.py motor\pos\ !siftdir! pos
python siftfeat.py motor\neg\ !siftdir! neg
python clustersift.py !siftdir! !K! 20 !modelpath! !clusterdir!
python create_transaction.py !clusterdir! !K! !transcdir!
python tapriori.py !transcdir! 0.002 0.8 !rulepath!
python detectwithrule.py d:\tmp\mot\h2.jpg !K! 0.7 !modelpath! !rulepath! d:\tmp\mot\out.jpg

@endlocal
