import subprocess
import os
import shutil
import sys
import json
from pathlib import Path
import re

import conf
import data.build_instances


def evaluation_gnn_gp(problem, testing_folder, nb_of_test_instances, gp_func_dic, time_limit=None, 
                        fixedcutsel=False, GNN_transformed=False, node_lim=-1, sol_path=None, 
                        do_gnn=True, build_set_of_instances=True,saving_folder="simulation_outcomes",
                        num_cuts_per_round=10, RL=False, heuristic=False, get_scores=False):
    nb_of_built_instances = 100
    json_gp_func_dic = json.dumps(gp_func_dic)
    is_ok = False
    if do_gnn:
        evaluation = {"SCIP": {}, "best_estimate_BFS": {}, "best_estimate_DFS": {}, "best_LB_BFS": {},
                      "GP_parsimony_parameter_1.2": {}, "GP_parsimony_parameter_1.4": {}, "gnn_bfs_nprimal=2": {},
                      "gnn_bfs_nprimal=100000": {}}
    else:
        evaluation = {"SCIP": {}, "best_estimate_BFS": {}, "Test_SCIP": {}, "best_estimate_DFS": {}, "best_LB_BFS": {},
                      "GP_parsimony_parameter_1.2": {}, "GP_parsimony_parameter_1.4": {}}
    done = 0
    while is_ok is False:
        print("here we go again", flush=True)



        # building instances
        if build_set_of_instances:
            try:
                shutil.rmtree(os.path.join(conf.ROOT_DIR, f"data/{problem}/{testing_folder}"))
            except:
                ''
            data.build_instances.build_new_set_of_instances(problem, testing_folder, nb_of_instances=nb_of_built_instances)

        if GNN_transformed:
            path = os.path.join(conf.ROOT_DIR, f"GNN_method/TransformedInstances/{testing_folder}")
        else:
            path = os.path.join(conf.ROOT_DIR, f"data/{problem}/{testing_folder}")
            
        for instance in os.listdir(path):
            is_ok = True
            # solving GNN
            if do_gnn:
                main_GNN = os.path.join(conf.ROOT_DIR, "artificial_pbs/subprocess_evaluation_gnn.py")
                result_gnn = subprocess.run(
                    ['python', main_GNN, problem, testing_folder, instance, saving_folder],
                    capture_output=True, text=True)
                print("result for", testing_folder, " gnn : ", result_gnn.stdout)
                if "It is ok for GNN" not in result_gnn.stdout:
                    is_ok = False
                    print("stderr: ", result_gnn.stderr)
                    try:
                        shutil.rmtree(os.path.join(conf.ROOT_DIR, f"stats/{problem}"))
                    except:
                        ''

            # solving GP_function and heuristics and SCIP
            GP_and_SCIP = os.path.join(conf.ROOT_DIR, "artificial_pbs/subprocess_evaluation_gp_SCIPbaseline.py")
            result = subprocess.run(
                ['python', GP_and_SCIP, problem, testing_folder, json_gp_func_dic, str(time_limit), 
                                                   str(int(fixedcutsel)), str(int(GNN_transformed)), str(node_lim), 
                                                   sol_path, instance, saving_folder, str(num_cuts_per_round),
                                                   str(int(RL)), str(int(heuristic)), str(int(get_scores))],
                capture_output=True, text=True)
            print("result for", testing_folder, "GP_function and SCIP : ", result.stdout, flush=True)

            if "It is ok for GP_function and the SCIP baseline" not in result.stdout:
                is_ok = False
                print("stderr: ", result.stderr, flush=True)

            if is_ok is True:
                done+=1
                print("one is done, with total of ",done, flush=True)
                dir = os.path.join(conf.ROOT_DIR,  # - 25
                                   f'{saving_folder}/{problem}/')
                for one_perf_file in os.listdir(dir):
                    if re.match(testing_folder, one_perf_file):
                        method = one_perf_file[len(testing_folder)+1: len(one_perf_file) - 5]
                        one_perf_path = dir + str(one_perf_file)
                        # print(instance)
                        with open(
                                one_perf_path,
                                'r') as openfile:
                            perfs = json.load(openfile)
                        evaluation[method][instance] = perfs[list(perfs.keys())[0]]

                if done == nb_of_test_instances:
                    print("everything is solved", flush=True)
                    print(evaluation)
                    for one_perf_file in os.listdir(dir):
                        if re.match(testing_folder, one_perf_file):
                            method = one_perf_file[len(testing_folder) + 1: len(one_perf_file) - 5]
                            new_json_dir = os.path.join(conf.ROOT_DIR,  # - 25
                                                        f'{saving_folder}/{problem}/{testing_folder}_{method}.json')
                            with open(new_json_dir,
                                        "w+") as outfile:
                                json.dump(evaluation[method], outfile)
                    print("ALL GUCCI GOOD")
                    return
    print("is not ok")


if __name__ == "__main__":

    problem = "wpms"
    testing_folder = 'test'
    print(sys.argv)
    for i in range(1, len(sys.argv), 2):
        if sys.argv[i] == '-problem':
            problem = sys.argv[i + 1]
        if sys.argv[i] == '-testing_folder':
            testing_folder = sys.argv[i + 1]
    evaluation_gnn_gp(problem, testing_folder, conf.gp_funcs_artificial_problems[problem])
