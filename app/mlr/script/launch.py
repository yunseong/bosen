#!/usr/bin/env python

import os
from os.path import dirname, join
import time

hostfile_name = "localserver"

app_dir = dirname(dirname(os.path.realpath(__file__)))
proj_dir = dirname(dirname(app_dir))

hostfile = join(proj_dir, "machinefiles", hostfile_name)

ssh_cmd = (
    "ssh "
    "-o StrictHostKeyChecking=no "
    "-o UserKnownHostsFile=/dev/null "
    )

petuum_params = {
    "hostfile": hostfile
    , "num_app_threads": 2
    , "staleness": 2
    , "num_comm_channels_per_client": 2 # 1~2 are usually enough.
    }

prog_name = "mlr_main"
prog_path = join(app_dir, "bin", prog_name)

env_params = (
  "GLOG_logtostderr=true "
  "GLOG_v=-1 "
  "GLOG_minloglevel=0 "
  )

# Get host IPs
with open(hostfile, "r") as f:
  hostlines = f.read().splitlines()
host_ips = [line.split()[1] for line in hostlines]
petuum_params["num_clients"] = len(host_ips)

"""
# os.system is synchronous call.
os.system("killall -q " + prog_name)
print "Done killing"

if not params["output_file_prefix"].startswith("hdfs://"):
  os.system("mkdir -p " + join(app_dir, "output"))
"""
def execute(batch):
  for client_id, ip in enumerate(host_ips):
    petuum_params["client_id"] = client_id
    cmd = ssh_cmd + ip + " "
    cmd += "\'python " + join(app_dir, "script/run_local.py")
    cmd += " %d %s %d\'" % (client_id, hostfile, batch)
    cmd += " &"
    print cmd
    os.system(cmd)


    if client_id == 0:
      print "Waiting for first client to set up"
      time.sleep(2)

for batch in [1]:
  execute(batch)
