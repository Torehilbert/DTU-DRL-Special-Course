using UnityEngine;
using System.Collections;

public class TestEnvironment : Environment
{
    float movementSpeed = 0.02f;
    float goalTolerance = 0.05f;

    public TestEnvironment(string[] args):base(args)
    {
        state = new float[ObservationDimension()];
    }

    public override EnvironmentResponse Step(float[] action)
    {
        state[0] += movementSpeed * Mathf.Clamp(action[0], -1, 1);

        if (Mathf.Abs(state[0]) < goalTolerance)
        {
            done = true;
            return new EnvironmentResponse(state, done, 100);
        }
        else if(Mathf.Abs(state[0]) > 1.5f)
        {
            done = true;
            return new EnvironmentResponse(state, done, -100);
        }
        else
            return new EnvironmentResponse(state, done, -1);
    }

    public override EnvironmentResponse Reset()
    {
        state[0] = (Random.Range(0, 2) * 2 - 1);
        done = false;
        return new EnvironmentResponse(state, done, 0);
    }

    public override int ObservationDimension()
    {
        return 1;
    }

    public override int ActionDimension()
    {
        return 1;
    }

    public override void Config(string config)
    {
        throw new System.NotImplementedException();
    }
}
