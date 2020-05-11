cd "D:\Projects\DTU DRL Special Course\DRLPython\NG"

python UnityTrain_REINFORCE.py ^
-episodes=1000 -nstep=5 -rolloutlimit=500 -discount=0.995 -lr_policy=1e-4 ^
-lr_critic=1e-3 -critic_lag=5 ^
-reward_normalization=0 -valfreq=10 -valcount=2 ^
-continuous_sigma=0.5 -continuous_sigma_end=0.1 ^
-portSend=26008 -portReceive=26009

pause