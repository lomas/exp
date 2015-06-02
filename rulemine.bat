::cluster number K is a global parameter across all modules
@setlocal enableDelayedExpansion

@set K=1000
@set modelpath=models\model.pkl
@set rulepath=rules.txt

@set siftdir=sift\
@set clusterdir=cluster\
@set transcdir=transc\

mkdir !siftdir!
mkdir !clusterdir!
mkdir !transcdir!

::python siftfeat.py motor\pos\ !siftdir! pos
::python siftfeat.py motor\neg\ !siftdir! neg
::python clustersift.py !siftdir! !K! 50 !modelpath! !clusterdir!
::python create_transaction.py !clusterdir!\h\ !K! !transcdir!
::python tapriori.py !transcdir! 0.008 0.8 !rulepath!
python detectwithrule.py d:\tmp\mot\h3.jpg !K! 0.6 !modelpath! !rulepath! d:\tmp\mot\out.jpg

@endlocal
