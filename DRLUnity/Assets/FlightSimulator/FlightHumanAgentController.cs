using UnityEngine;
using System.Collections;

public class FlightHumanAgentController : AgentController
{
    FlightInputReader flightInputReader;

    float[] action = new float[3];


    public FlightHumanAgentController(FlightInputReader flightInputReader)
    {
        this.flightInputReader = flightInputReader;
    }


    public override ActionResponse GetActionResponse(int environmentSymbol, float[] state, float reward, bool done)
    {
        action[0] = flightInputReader.inputElevator;
        action[1] = flightInputReader.inputAileron;
        action[2] = flightInputReader.inputBrakes;

        ActionResponse response = new ActionResponse();
        response.symbol = flightInputReader.inputReset ? AgentActionSymbol.Reset : AgentActionSymbol.Continue;
        response.actions = action;
        response.msg = "";
        return response;
    }


    public override void CloseAgent()
    {

    }
}
