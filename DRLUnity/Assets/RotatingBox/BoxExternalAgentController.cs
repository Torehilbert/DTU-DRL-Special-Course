using UnityEngine;
using System.Collections;

public class BoxExternalAgentController : AgentController
{
    UDPNetwork network;
    int observationDimension;
    int actionDimension;

    float[] receiveBuffer;

    float[] actions;
    string receivedMessage;


    public BoxExternalAgentController(int observationDimension, int actionDimension, int portSend, int portReceive)
    {
        this.observationDimension = observationDimension;
        this.actionDimension = actionDimension;

        actions = new float[actionDimension];
        receiveBuffer = new float[1 + actionDimension];

        network = new UDPNetwork(portSend, portReceive);
        network.AllocateSendBuffer(4 + 4 * observationDimension + 4 + 4);
    }


    public override ActionResponse GetActionResponse(int environmentSymbol, float[] state, float reward, bool done)
    {
        ActionResponse response = new ActionResponse();

        // Send message with (symbol, *state, reward, done)
        network.SetFloatInBuffer(environmentSymbol, 0);
        network.SetArrayFloatsInBuffer(state, 1);
        network.SetFloatInBuffer(reward, observationDimension + 1);
        network.SetFloatInBuffer(done ? 1f : 0f, observationDimension + 2);
        network.Send();

        // Receive status symbol & action
        network.ReceiveFloatsAndString(1 + actionDimension, receiveBuffer, ref receivedMessage);
        AgentActionSymbol agentSymbol = (AgentActionSymbol)Mathf.RoundToInt(receiveBuffer[0]);
        for (int i = 1; i < receiveBuffer.Length; i++)
            actions[i - 1] = receiveBuffer[i];

        // Return
        response.symbol = agentSymbol;
        response.actions = actions;
        response.msg = receivedMessage;
        return response;
    }

    public override void CloseAgent()
    {
        network.SetFloatInBuffer(2, 0);
        network.SetArrayFloatsInBuffer(new float[observationDimension], 1);
        network.SetFloatInBuffer(0, observationDimension + 1);
        network.SetFloatInBuffer(1f, observationDimension + 2);
        network.Send();
    }
}
