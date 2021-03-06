#!/usr/bin/env python
import ast
import os
import sys
from os.path import dirname
from os.path import join

app_dir = dirname(dirname(os.path.realpath(__file__)))
prog = join(app_dir, "bin", "gen_data_sparse")

num_train = int(sys.argv[1]) # FYI. 10000 instances -> 124MB
num_nodes = int(sys.argv[2]) # How many nodes to run
one_based = ast.literal_eval(sys.argv[3]) # Spark: true, Dolphin, false
sparsity = 0.05 # 5 percent

# no trailing /
prefix_path = "/dfs/dataset/mlr/{0}_{1}".format(num_train, num_nodes)
if not os.path.exists(prefix_path):
    os.makedirs(prefix_path)

params = {
    "num_train": num_train
    , "feature_dim": 20000
    , "num_partitions": num_nodes
    , "nnz_per_col": int(sparsity * num_train)
    , "one_based": one_based 
    , "beta_sparsity": 1
    , "correlation_strength": 0
    , "noise_ratio": 0
    , "snappy_compressed": "false"
    , "num_labels": 1000
    }
params["output_file"] = join(prefix_path, "lr%d_dim%d_s%d_nnz%d%s") \
    % (params["num_labels"], params["feature_dim"], \
    params["num_train"], params["nnz_per_col"], "_one_based" if one_based else '')


env_params = (
  "GLOG_logtostderr=true "
  "GLOG_v=-1 "
  "GLOG_minloglevel=0 "
  )

cmd = env_params + prog
cmd += "".join([" --%s=%s" % (k,v) for k,v in params.items()])
print cmd
os.system(cmd)
