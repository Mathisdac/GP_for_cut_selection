import os
import shutil
import conf
import argparse
from data.build_gisp_instances import *
from GNN_genetic_programming_for_node_scoring import *
from artificial_pbs.evaluation_convergence_of_GP_over_gens_articial_pbs import *
from artificial_pbs.evaluation_artificial_problems import *
from artificial_pbs.build_tables_artificial_pb_perfs import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('seed', type=str, help="Seed that we choose")
    parser.add_argument('sol_path', type=str, help="Path to the solution file")
    args = parser.parse_args()
    
    # Parameters for GP_function training
    problem = "GNN_gisp"  # Problem type
    training_folder = "Train"
    testing_folder= "Test"
    initial_pop = 50  # Population size for tree-based heuristics
    mate = 0.9  # Crossover rate
    mutate = 0.1  # Mutation rate
    nb_of_gen = 20  # Number of generations
    seed = args.seed  # Random seed
    sol_path = args.sol_path  # Path to the solution file

    node_select = "BFS"  # Node selection method (BFS allows testing DFS as well)

    # Tournament parameters
    fitness_size = 5  # Number of individuals in the fitness tournament
    parsimony_size = 1.2  # Parameter for size-based tournament
    time_limit = int(1e8)  # Time limit (not applicable for artificial problems)
    nb_of_instances = 0  # Number of instances (not applicable for artificial problems)

    # Environment parametrisation for SCIP solving
    GNN_comparison = True
    #semantic_algo = False

    GNN_transformed = True  # Whether to use the transformed version of the problem for comparison with GNN
    root = False
    if root:
        node_lim = 1  # Node limit for GNN comparison
    else:
        node_lim = -1
    
    """########### SMALL PARAM FOR TESTING ###########
    n_test_instances=4
    initial_pop=5
    nb_of_gen=2
    seed=1
    node_lim=1
    fitness_size=2
    ############ SMALL PARAM FOR TESTING ###########"""

    dossier = os.path.join(conf.ROOT_DIR, "GNN_method", "TransformedInstances", testing_folder)
    contenu = os.listdir(dossier)
    fichiers = [f for f in contenu if os.path.isfile(os.path.join(dossier, f))]

    n_test_instances = len(fichiers)  

    simulation_folder = os.path.join(conf.ROOT_DIR, problem + "__seed__" + seed)
    if not os.path.exists(simulation_folder):
        os.makedirs(simulation_folder)
    function_folder = os.path.join(simulation_folder, "GP_function")
    problem_folder = os.path.join(simulation_folder, problem)
    os.makedirs(function_folder, exist_ok=True)  # Create the problem folder if it doesn't exist
    os.makedirs(problem_folder, exist_ok=True)

    # Construct a unique name for the run
    name = f"{problem}_pop_{initial_pop}_nb_gen{nb_of_gen}_seed_{seed}"
    # Run the GP_function training
    main_GP(
        problem=problem,
        initial_pop=initial_pop,
        mate=mate,
        mutate=mutate,
        nb_of_gen=nb_of_gen,
        seed=seed,
        node_select=node_select,
        saving_folder=function_folder,
        name=name,
        training_folder=training_folder,
        fitness_size=fitness_size,
        parsimony_size=parsimony_size,
        time_limit=time_limit,
        nb_of_instances=nb_of_instances,
        fixedcutsel=GNN_comparison,
        node_lim=node_lim,
        sol_path=sol_path,
        transformed=GNN_transformed
    )  

    # Evaluate the convergence of GP across generations
    gp_function = convergence_of_gp_over_generations(simulation_folder,saving=False, show=False)

    gp_func_dic = {"1.2":gp_function}#1.2 is meant for the parsimony parameter
    print(gp_function, flush=True)
    evaluation_gnn_gp(problem, testing_folder, n_test_instances, gp_func_dic, time_limit=time_limit, fixedcutsel=GNN_comparison, 
                      GNN_transformed=GNN_transformed, node_lim=node_lim, sol_path=sol_path, do_gnn=False, 
                      build_set_of_instances=False,saving_folder=simulation_folder)

    # Gather information from JSON files for the specified problems and partitions
    dic_info = gather_info_from_json_files(problems=[problem], partitions=[testing_folder], saving_folder=simulation_folder)

    # Display the output results
    just_get_the_output_results(dic_info)