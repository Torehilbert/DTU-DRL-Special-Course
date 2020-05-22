cd "D:\Projects\DTU DRL Special Course\DRLPython\NG"

python UnityTrain_REINFORCE.py ^
-env="Flight" ^
-iterations=200 ^
-nstep=100 ^
-rolloutlimit=5000 ^
-discount=0.995 ^
-lr_policy=1e-4 ^
-lr_policy_gamma=0.4642 ^
-lr_policy_stepsize=250000 ^
-continuous_sigma=0.25 ^
-continuous_sigma_end=0.25 ^
-continuous_sigma_steps=200 ^
-lr_critic=1e-3 ^
-lr_critic_gamma=0.4642 ^
-lr_critic_stepsize=250000 ^
-critic_lag=10 ^
-reward_normalization=0 ^
-valfreq=50 ^
-valcount=10 ^
-network_save_interval=20000 ^
-portSend=26000 ^
-portReceive=26001 ^
-difficulty=0.75 ^
-actionFrequency=5 ^
-windPower=2.5 ^
-windAngleDeviation=25.0 ^
-path_policy="D:\Projects\DTU DRL Special Course\Results\2020-05-18 15-09-41 Flight\net_final.pt" ^
-path_critic="D:\Projects\DTU DRL Special Course\Results\2020-05-18 15-09-41 Flight\critic_final.pt"

pause