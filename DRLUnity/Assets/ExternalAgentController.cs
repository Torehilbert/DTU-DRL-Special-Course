using UnityEngine;
using System.Collections;

public class ExternalAgentController : AgentController
{
    UDPNetwork network;
    float[] actions;

    public ExternalAgentController(int actionDimension)
    {
        // Should start up python process on its own. Currently it is needed to manually open process
        //...

        actions = new float[actionDimension];
        network = new UDPNetwork(26000, 26001);
    }

    public override ActionResponse GetActionResponse(int environmentSymbol, float[] state, float reward, bool done)
    {
        throw new System.NotImplementedException();
    }

    public override void CloseAgent()
    {
        throw new System.NotImplementedException();
    }
}
