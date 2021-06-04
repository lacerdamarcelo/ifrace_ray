#for func_num in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
#for func_num in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
#for func_num in 1
#do
#    sbatch run_ifrace_sbatch.sh experiments_output/ifrace_binary_ga_${func_num}.out 48 binary_ga_config.json BinGA Knapsack knapsack_config/knapsack_ifrace_func${func_num}_instances.txt 48 20 0.3 1 10 30 30 300 /home/g/gomesper/ray_results/validation_data/ifrace_binary_ga_${func_num}.txt
#    sbatch run_ifrace_sbatch.sh experiments_output/ifrace_aco_tsp_${func_num}.out 48 aco_tsp_config.json ACO_TSP TSP tsp_config/tsp_ifrace_func${func_num}_instances.txt 48 20 0.3 1 10 30 30 300 /home/g/gomesper/ray_results/validation_data/ifrace_aco_tsp_${func_num}.txt
#done

for func_num in 1 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
#for func_num in 1
do
#    sbatch run_ifrace_sbatch.sh experiments_output/ifrace_de_${func_num}.out 48 de_config.json DE CEC17 cec17_config/cec17_ifrace_func${func_num}_instances.txt 48 20 0.3 1 10 30 30 300 /home/g/gomesper/ray_results/validation_data/ifrace_de_${func_num}.txt
    sbatch run_ifrace_sbatch.sh experiments_output/ifrace_hclpso_${func_num}_600.out 48 hclpso_config.json HCLPSO CEC17 cec17_config/cec17_ifrace_func${func_num}_instances.txt 48 20 0.3 1 10 30 30 600 /home/g/gomesper/ray_results/validation_data/ifrace_hclpso_${func_num}_600.txt
#     sbatch run_ifrace_sbatch.sh experiments_output/ifrace_fss_${func_num}.out 48 fss_config.json FSS CEC17 cec17_config/cec17_ifrace_func${func_num}_instances.txt 48 20 0.3 1 10 30 30 300 /home/g/gomesper/ray_results/validation_data/ifrace_fss_${func_num}.txt
#    sbatch run_ifrace_sbatch.sh experiments_output/ifrace_aco_tsp_${func_num}.out 48 aco_tsp_config.json ACO_TSP TSP tsp_config/tsp_ifrace_func${func_num}_instances.txt 48 20 0.3 1 10 30 30 300 /home/g/gomesper/ray_results/validation_data/ifrace_aco_tsp_${func_num}.txt
done

