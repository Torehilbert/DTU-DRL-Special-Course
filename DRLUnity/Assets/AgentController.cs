using UnityEngine;
using System.Collections;


public abstract class AgentController
{
    public enum AgentActionSymbol {Continue=0, Reset=1, Exit=2}
    public struct ActionResponse
    {
        public AgentActionSymbol symbol;
        public float[] actions;
        public string msg;
    }

    public AgentController() { }
    public abstract ActionResponse GetActionResponse(int environmentSymbol, float[] state, float reward, bool done);
    public abstract void CloseAgent();
}
