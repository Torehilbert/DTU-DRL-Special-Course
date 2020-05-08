#!/bin/sh
#BSUB -q gpuv100
#BSUB -J exp_20_100
#BSUB -n 7
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 23:59
#BSUB -R "rusage[mem=2GB]"
#BSUB -u s144328@student.dtu.dk
#BSUB -N
#BSUB -o logs/%J.out
#BSUB -e logs/%J.err

module load python3/3.6.2
python3 ~/DRL/A3C/main_a3c.py --env="LunarLander-v2" --lr=1e-4 --critic_weight=1e+0 --output_path="OP/20_100_01" --max_updates=2000000 --num_envs=6 --entropy_weight=0.5 --rollout_limit=500 --num_steps=20
python3 ~/DRL/A3C/main_a3c.py --env="LunarLander-v2" --lr=1e-4 --critic_weight=1e+0 --output_path="OP/20_100_02" --max_updates=2000000 --num_envs=6 --entropy_weight=0.5 --rollout_limit=500 --num_steps=20
python3 ~/DRL/A3C/main_a3c.py --env="LunarLander-v2" --lr=1e-4 --critic_weight=1e+0 --output_path="OP/20_100_03" --max_updates=2000000 --num_envs=6 --entropy_weight=0.5 --rollout_limit=500 --num_steps=20
python3 ~/DRL/A3C/main_a3c.py --env="LunarLander-v2" --lr=1e-4 --critic_weight=1e+0 --output_path="OP/20_100_04" --max_updates=2000000 --num_envs=6 --entropy_weight=0.5 --rollout_limit=500 --num_steps=20
