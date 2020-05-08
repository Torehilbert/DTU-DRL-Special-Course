using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public abstract class MultiAgentEnvironment
{
    public int numAgents;
    public bool done;

    public MultiAgentEnvironment(string[] args) { }
    public abstract EnvironmentResponse[] Step(int[] action);
    public abstract EnvironmentResponse[] Reset();
    public abstract int[] ObservationDimension();       // Number of floats agent-wise
    public abstract int[] ActionDimension();            // Number of discrete actions agent-wise
}
