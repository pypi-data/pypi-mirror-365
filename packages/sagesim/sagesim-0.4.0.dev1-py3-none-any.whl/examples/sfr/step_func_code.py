from cupyx import jit
import os
import sys
module_path = os.path.abspath('/home/co1/sagesim_github/SAGESim/examples/sfr')
if module_path not in sys.path:
	sys.path.append(module_path)
from sfr_breed import *


@jit.rawkernel(device='cuda')
def stepfunc(
global_tick,
device_global_data_vector,
a0,a1,a2,a3,
sync_workers_every_n_ticks,
num_rank_local_agents,
agent_ids,
):
	thread_id = jit.blockIdx.x * jit.blockDim.x + jit.threadIdx.x
	agent_index = thread_id
	if agent_index < num_rank_local_agents:
		breed_id = a0[agent_index]
		for tick in range(sync_workers_every_n_ticks):

			thread_local_tick = int(global_tick) + tick

			if breed_id == 0:
				step_func(
					thread_local_tick,
					agent_index,
					device_global_data_vector,
					agent_ids,
					a0,a1,a2,a3,
				)