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
These things are only happening on my mac, not in our deployment environment! I think they are fixed in interop==1.3.2, but there isn't an intel mac package for that version!

- I'm seeing `swig/python detected a memory leak of type 'std::vector< unsigned char,std::allocator< unsigned char > > *', no destructor found.`, but it seems to work OK.
- the interop package that will install for my intel-based MacBook is 1.3.1, which won't run with numpy 2.  So, on my mac, I force the `pip install interop==1.3.1` and `pip install numpy=1.26`.  If you have an apple silicon mac or a linux box, you can probably just use `pip install interop` and you're fine.

## Credits
- University of Michigan, Advanced Genomics Core
- https://www.biostars.org/p/9552512/
- https://notebook.community/Illumina/interop/docs/src/Tutorial_01_Intro
- https://illumina.github.io/interop/index.html
