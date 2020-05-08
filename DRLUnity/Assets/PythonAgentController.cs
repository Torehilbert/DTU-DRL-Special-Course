using UnityEngine;
using System.Collections;
using System;

public class PythonAgentController : AgentController
{
    Environment environment;
    public UDPNetwork network { get; private set;}

    int observationDimension = 0;
    int actionDimension = 0;

    // Constructor to use for training, i.e. when Python starts everything
    public PythonAgentController(Environment environment, int portSend, int portReceive)
    {
        this.environment = environment;
        network = new UDPNetwork(portSend, portReceive);
        observationDimension = environment.ObservationDimension();
        actionDimension = environment.ActionDimension();
        network.AllocateSendBuffer(1 + 4 + 4 * observationDimension);
        
        /* Send network msg to Python (12 bytes)
         1. port                    (int = 4 bytes) (port that python sends and unity receives)
         2. observation dimension   (int = 4 bytes)
         3. action dimension        (int = 4 bytes)
         */
        byte[] obsdimBytes = BitConverter.GetBytes(observationDimension);
        byte[] actdimBytes = BitConverter.GetBytes(actionDimension);
        byte[] introMsg = new byte[2 * 4];
        introMsg[0] = obsdimBytes[0];
        introMsg[1] = obsdimBytes[1];
        introMsg[2] = obsdimBytes[2];
        introMsg[3] = obsdimBytes[3];
        introMsg[4] = actdimBytes[0];
        introMsg[5] = actdimBytes[1];
        introMsg[6] = actdimBytes[2];
        introMsg[7] = actdimBytes[3];
        network.Send(introMsg);
    }

    // Constructor to use for visualization, i.e. when Unity starts everything
    public PythonAgentController(Environment environment, int agentID)
    {
        // Start Python
        System.Diagnostics.Process process = new System.Diagnostics.Process();
        System.Diagnostics.ProcessStartInfo startInfo = new System.Diagnostics.ProcessStartInfo();
        startInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
        startInfo.FileName = "python.exe";
        startInfo.Arguments = "/C copy /b Image1.jpg + Archive.rar Image2.jpg";
        process.StartInfo = startInfo;
        process.Start();



        throw new NotImplementedException("Constructor for visualization is not implemented yet!");
    }

    public override ActionResponse GetActionResponse(int environmentSymbol, float[] state, float reward, bool done)
    {
        throw new NotImplementedException();
    }

    public override void CloseAgent()
    {
        throw new NotImplementedException();
    }
}
