using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public struct EnvironmentResponse
{
    public float[] state;
    public bool done;
    public float reward;

    public EnvironmentResponse(float[] state, bool done, float reward)
    {
        this.state = state;
        this.done = done;
        this.reward = reward;
    }
}

public abstract class Environment
{
    public float[] state;
    public bool done;

    public Environment(string[] args){}
    public abstract EnvironmentResponse Step(float[] action);
    public abstract EnvironmentResponse Reset();
    public abstract int ObservationDimension();     // Number of floats
    public abstract int ActionDimension();          // Number of continuous actions
    public abstract void Config(string config);
}
