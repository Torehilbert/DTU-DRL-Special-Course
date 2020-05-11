cd "D:\Projects\DTU DRL Special Course\DRLPython\NG"

python UnityTrain_REINFORCE.py ^
-iterations=200000 -nstep=10 -rolloutlimit=500 -discount=0.995 ^
-lr_policy=1e-4 -lr_policy_gamma=0.4642 -lr_policy_stepsize=50000 ^
-continuous_sigma=0.5 -continuous_sigma_end=0.025 -continuous_sigma_steps=50000 ^
-lr_critic=1e-3 -lr_critic_gamma=0.4642 -lr_critic_stepsize=50000 -critic_lag=10 ^
-reward_normalization=0 -valfreq=5000 -valcount=15 ^
-network_save_interval=20000 ^
-portSend=26002 -portReceive=26003

pause