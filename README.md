# illumina_run_metrics
Use the Illumina 'interop' library to get sequencer run metrics.

## How to use
```shell
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```
```shell
python3 main.py -r MiSeqDemo -o MiSeqDemo.json
```
At the AGC, its probably more like:
```shell
python3 main.py -r /nfs/agc-buffer/Illumina/runs/240923_M06643_0567_000000000-DPWFW/ -o MiSeq-567_runinfo.json
```

## oddities
- I'm seeing `swig/python detected a memory leak of type 'std::vector< unsigned char,std::allocator< unsigned char > > *', no destructor found.`, which is weird, and I don't know why.
- the interop package from Illumina really wants numpy, but it doesn't like numpy 2, so I'm just going with pinned versions in the requirements.txt file.

## Credits
- University of Michigan, Advanced Genomics Core
- https://www.biostars.org/p/9552512/
- https://notebook.community/Illumina/interop/docs/src/Tutorial_01_Intro
- https://illumina.github.io/interop/index.html
