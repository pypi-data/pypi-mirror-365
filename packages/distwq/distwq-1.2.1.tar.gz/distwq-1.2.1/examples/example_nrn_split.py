# Example of using distributed work queue distwq
# PYTHONPATH must include the directories in which distwq and this file are located.

import sys
from neuron import h
import os

os.environ["DISTWQ_CONTROLLER_RANK"] = "-1"
import distwq

h("""objref cvode""")
h.cvode = h.CVode()

subworld_size = 3

use_coreneuron = True
if use_coreneuron:
    from neuron import coreneuron

    coreneuron.enable = True
    coreneuron.verbose = 1


def do_work(i):
    pc = h.ParallelContext()
    rank = int(pc.id())
    nhost = int(pc.nhost())
    soma = h.Section(name="soma")
    soma.L = 20
    soma.diam = 20
    soma.insert("hh")
    iclamp = h.IClamp(soma(0.5))
    iclamp.delay = 2
    iclamp.dur = 0.1
    iclamp.amp = 0.9
    rec_v = h.Vector()
    rec_t = h.Vector()
    rec_v.record(soma(0.5)._ref_v)  # Membrane potential vector
    rec_t.record(h._ref_t)
    # h.fadvance()
    # h.continuerun(250)
    syn = h.ExpSyn(soma(0.5))
    spike_detector = h.NetCon(soma(0.5)._ref_v, None, sec=soma)
    netstim = h.NetStim()
    netstim.number = 1
    netstim.start = 0
    nc = h.NetCon(netstim, syn)
    gid = pc.id()
    pc.set_gid2node(gid, pc.id())
    pc.cell(gid, spike_detector)
    h.cvode.cache_efficient(1)
    h.finitialize(-65)
    pc.set_maxstep(10)
    pc.psolve(250.0)
    return rec_v.max()


def main_controller(controller):
    h.nrnmpi_init()
    pc = h.ParallelContext()
    pc.subworlds(subworld_size)
    if use_coreneuron:
        h.cvode.cache_efficient(1)
        h.finitialize(-65)
        pc.set_maxstep(10)
        pc.psolve(0.1)

    n = 10
    for i in range(0, n):
        controller.submit_call("do_work", (i + 1,), module_name="example_nrn_split")
    s = []
    for i in range(0, n):
        s.append(controller.get_next_result())
    print(s)
    controller.info()


def main_worker(worker):
    h.nrnmpi_init()
    pc = h.ParallelContext()
    pc.subworlds(subworld_size)
    if use_coreneuron:
        h.cvode.cache_efficient(1)
        h.finitialize(-65)
        pc.set_maxstep(10)
        pc.psolve(0.1)


if __name__ == "__main__":
    if distwq.is_controller:
        distwq.run(
            fun_name="main_controller",
            module_name="example_nrn_split",
            verbose=True,
            nprocs_per_worker=subworld_size,
            broker_is_worker=True,
        )
    else:
        distwq.run(
            fun_name="main_worker",
            module_name="example_nrn_split",
            verbose=True,
            nprocs_per_worker=subworld_size,
            broker_is_worker=True,
        )
