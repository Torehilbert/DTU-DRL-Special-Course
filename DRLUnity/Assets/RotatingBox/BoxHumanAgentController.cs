using UnityEngine;
using System.Collections;

public class BoxHumanAgentController : AgentController
{
    BoxInputReader boxInputReader;
    float[] action = new float[1];


    public BoxHumanAgentController(BoxInputReader boxInputReader)
    {
        this.boxInputReader = boxInputReader;
    }


    public override ActionResponse GetActionResponse(int environmentSymbol, float[] state, float reward, bool done)
    {
        action[0] = boxInputReader.rotationForce;

        ActionResponse response = new ActionResponse();
        response.symbol = AgentActionSymbol.Continue;
        response.actions = action;
        response.msg = "";
        return response;
    }


    public override void CloseAgent()
    {
        
    }
}
