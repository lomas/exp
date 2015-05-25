::cluster number K is a global parameter across all modules
mkdir sift
mkdir cluster
mkdir transc

::python siftfeat.py motor\pos\ sift\ pos
::python siftfeat.py motor\neg\ sift\ neg
python clustersift.py sift\ 1024 20 models\model.pkl cluster\
::python clustersift.py sift\ 102 200 models\model.pkl cluster\
pause
python create_transaction.py cluster\ 1024 transc\
python tapriori.py
python detctwithrule.py src.jpg out.jpg
