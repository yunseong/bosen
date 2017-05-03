#!/usr/bin/env python

"""
This script starts a process locally, using <client-id> <hostfile> as inputs.
"""

import os
from os.path import dirname
from os.path import join
import time
import sys

if len(sys.argv) != 3:
  print "usage: %s <client-id> <hostfile>" % sys.argv[0]
  sys.exit(1)

# Please set the absolute path to app dir
app_dir = dirname(dirname(os.path.realpath(__file__)))

client_id = sys.argv[1]
hostfile = sys.argv[2]
proj_dir = dirname(dirname(app_dir))

num_train = 100000
num_partition = 25
train_file = "lr1000_dim20000_s{0}_nnz{1}.x{2}.libsvm.X".format(num_train, int(num_train * 0.05), num_partition)
num_epoch = 5
num_batch = 4
output_dir = "/dfs/logs/bosen/{0}_{1}".format(num_train, num_partition)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

params = {
    "train_file": "hdfs://santaclara-m:9000/user/ubuntu/dataset/mlr/{0}_{1}/".format(num_train, num_partition) + train_file
    , "global_data": "false"
    , "perform_test": "false"
    , "use_weight_file": "false"
    , "weight_file": ""
    , "num_epochs": num_epoch
    , "num_batches_per_epoch": num_batch
    , "init_lr": 0.01 # initial learning rate
    , "lr_decay_rate": 0.99 # lr = init_lr * (lr_decay_rate)^T
    , "num_batches_per_eval": num_batch
    , "num_train_eval": 10000 # compute train error on these many train.
    , "num_test_eval": 20
    , "lambda": 0
    , "output_file_prefix": join(output_dir, train_file + "_epoch_{0}_batch_{1}.out".format(num_epoch, num_batch))
    }

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

# os.system is synchronous call.
os.system("killall -q " + prog_name)
print "Done killing"

cmd = "export CLASSPATH=`hadoop classpath --glob`:$CLASSPATH; "
cmd += env_params + prog_path
petuum_params["client_id"] = client_id
cmd += "".join([" --%s=%s" % (k,v) for k,v in petuum_params.items()])
cmd += "".join([" --%s=%s" % (k,v) for k,v in params.items()])
print cmd
os.system(cmd)
