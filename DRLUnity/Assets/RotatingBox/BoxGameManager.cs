using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using ArgumentParsing;

public class BoxGameManager : MonoBehaviour
{
    public event System.Action<float[]> onStateChange;
    public event System.Action<float, float, int, int> onTargetChange;
    public event System.Action<float> onActionValueChange;

    public static BoxGameManager instance;
    public const int observationDimension = 7;
    public const int actionDimension = 1;

    public Rigidbody box;
    public Transform boxTransform;
    public BoxMechanics boxMechanics;
    public BoxInputReader boxInputReader;
    AgentController agentController;

    float[] state = new float[observationDimension];
    bool done = false;

    string[] messageArgumentSeparator = new string[] { "," };
    string[] messageKeyValueSeparator = new string[] { "=" };

    public bool exitButtonPressed = false;
    public bool resetButtonPressed = false;

    // Parameters
    bool externalAgent;
    int portAgentSend;
    int portAgentReceive;

    bool controlRotation;
    bool controlVelocity;
    bool autoRollTarget;
    float autoTargetMin;
    float autoTargetMax;

    float angVelStartMin;
    float angVelStartMax;
    float rotStartMin;
    float rotStartMax;
    float velStartMin;
    float velStartMax;

    public void Awake()
    {
        instance = this;
        Physics.autoSimulation = false;

        boxTransform = box.transform;

        // Define and read arguments
        ArgumentParser argParser = new ArgumentParser();
        argParser.AddArgument("-targetFrameRate", false, "50");
        argParser.AddArgument("-portAgentSend", false, "26001");
        argParser.AddArgument("-portAgentReceive", false, "26000");
        argParser.AddArgument("-controlRotation", false, "1");
        argParser.AddArgument("-controlVelocity", false, "0");
        argParser.AddArgument("-autoRollTarget", false, "1");
        argParser.AddArgument("-autoTargetMin", false, "-45");
        argParser.AddArgument("-autoTargetMax", false, "45");
        argParser.AddArgument("-rotStartMin", false, "-20");
        argParser.AddArgument("-rotStartMax", false, "20");
        argParser.AddArgument("-angVelStartMin", false, "-5");
        argParser.AddArgument("-angVelStartMax", false, "5");
        argParser.AddArgument("-velStartMin", false, "-10");
        argParser.AddArgument("-velStartMax", false, "10");
        argParser.ParseArguments();

        // Read arguments
        Application.targetFrameRate = argParser.GetIntArgument("-targetFrameRate");
        QualitySettings.vSyncCount = 0;

        externalAgent = argParser.arguments["-portAgentSend"].isSupplied && argParser.arguments["-portAgentReceive"].isSupplied;
        portAgentSend = argParser.arguments["-portAgentSend"].valueInt;
        portAgentReceive = argParser.arguments["-portAgentReceive"].valueInt;
        controlRotation = argParser.arguments["-controlRotation"].valueInt == 1;
        controlVelocity = argParser.arguments["-controlVelocity"].valueInt == 1;
        autoRollTarget = argParser.arguments["-autoRollTarget"].valueInt == 1;
        autoTargetMin = argParser.arguments["-autoTargetMin"].valueFloat;
        autoTargetMax = argParser.arguments["-autoTargetMax"].valueFloat;
        rotStartMin = argParser.arguments["-rotStartMin"].valueFloat;
        rotStartMax = argParser.arguments["-rotStartMax"].valueFloat;
        angVelStartMin = argParser.arguments["-angVelStartMin"].valueFloat;
        angVelStartMax = argParser.arguments["-angVelStartMax"].valueFloat;
        velStartMin = argParser.arguments["-velStartMin"].valueFloat;
        velStartMax = argParser.arguments["-velStartMax"].valueFloat;

        // Instantiate agent controller (external or local human controller)
        if (externalAgent)
            agentController = new BoxExternalAgentController(observationDimension, actionDimension, portAgentSend, portAgentReceive);
        else
            agentController = new BoxHumanAgentController(boxInputReader);

        // Initiate environment
        ResetEnvironment();
    }

    float lastAction = 0;

    private void Update()
    {
        // Check UI buttons
        if (resetButtonPressed)
        {
            ResetEnvironment();
            resetButtonPressed = false;
        }
        if (exitButtonPressed)
        {
            agentController.CloseAgent();
            Close();
            return;
        }

        // Update state
        UpdateState();
        onStateChange?.Invoke(state);

        // Calculate reward
        float reward = 1f;
        if(state[5] > 0.5f)
        {
            reward -= (state[3] - state[0]) * (state[3] - state[0]);
        }
        else
        {
            // new method
            float rotationDelta = state[4] - state[1];
            reward = HillFunction(rotationDelta, 0, 5) - 0.01f * Mathf.Abs(lastAction);

            // old method
            //reward -= Mathf.Abs((state[4] - state[1])/45);
            //reward -= 0.05f * lastAction * lastAction;
        }

        // Check done
        if (Mathf.Abs(state[1]) > 135f)
        {
            reward = -100;
            done = true;
        }
        
        // Get Action from agent
        AgentController.ActionResponse response = agentController.GetActionResponse(0, state, reward, done);

        // Perform configurations received from custom message string in agent response
        if (response.msg.Length > 0)
        {
            BoxLogUI.instance.Log("Received message from agent: ");
            foreach (string s in response.msg.Split(messageArgumentSeparator, System.StringSplitOptions.None))
            {
                BoxLogUI.instance.Log(s);
                HandleMessage(s);
            }
        }


        // Perform Exit or Reset on environment if told so by agent
        if (response.symbol == AgentController.AgentActionSymbol.Exit)
            Close();
        else if (response.symbol == AgentController.AgentActionSymbol.Reset)
        {
            ResetEnvironment();
            lastAction = 0;
            return;
        }
        else
        {
            // Execute physics
            boxMechanics.rotationForce = response.actions[0];
            boxMechanics.ManualFixedUpdate();
            Physics.Simulate(0.02f);

            onActionValueChange?.Invoke(response.actions[0]);
            lastAction = response.actions[0];
        }
    }


    void Close()
    {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
    }

    void UpdateState()
    {
        state[0] = box.velocity.x;
        state[1] = Vector3.SignedAngle(boxTransform.up, Vector3.up, Vector3.forward);
        state[2] = -box.angularVelocity.z * Mathf.Rad2Deg;
    }

    void ResetEnvironment()
    {
        done = false;

        // Roll random start values
        float startRotation = Random.Range(rotStartMin, rotStartMax);
        float startVelocity = Random.Range(velStartMin, velStartMax);
        float startAngularVelocity = Random.Range(angVelStartMin, angVelStartMax);

        // Set physic transfom/rigidbody values
        boxTransform.position = Vector3.zero;
        boxTransform.rotation = Quaternion.Euler(0, 0, startRotation);
        box.velocity = startVelocity * Vector3.right;
        box.angularVelocity = startAngularVelocity * Vector3.forward;

        // Set new target value automatically if enabled
        if(autoRollTarget && controlRotation)
            ChangeRotationTarget(Random.Range(autoTargetMin, autoTargetMax));
        else if(autoRollTarget && controlVelocity)
            ChangeVelocityTarget(Random.Range(autoTargetMin, autoTargetMax));
    }


    public void HandleMessage(string message)
    {
        string[] splits = message.Split(messageKeyValueSeparator, System.StringSplitOptions.None);
        if(splits.Length == 2)
        {
            float target = 0;
            if (splits[0].Equals("v"))
            {
                if (float.TryParse(splits[1], out target))
                    ChangeVelocityTarget(target);
            }
            else if (splits[0].Equals("r"))
            {
                if (float.TryParse(splits[1], out target))
                    ChangeRotationTarget(target);
            }
        }
    }


    public void ChangeVelocityTarget(float target)
    {
        controlVelocity = true;
        state[3] = target;
        state[4] = 0;
        state[5] = 1;
        state[6] = 0;
        onTargetChange?.Invoke(state[3], state[4], 1, 0);
        BoxLogUI.instance.Log("Changed velocity target to " + state[3].ToString("0.00"));
    }


    public void ChangeRotationTarget(float target)
    {
        controlRotation = true;
        state[3] = 0;
        state[4] = target;
        state[5] = 0;
        state[6] = 1;
        onTargetChange?.Invoke(state[3], state[4], 0, 1);
        BoxLogUI.instance.Log("Changed rotation target to " + state[4].ToString("0.00"));
    }

    float HillFunction(float x, float mu, float sigma)
    {
        // Function for reward, like the normal distribution but with the peak always taking value y=1 independently of sigma
        return Mathf.Exp(-0.5f * ((x - mu) / sigma) * ((x - mu) / sigma));
    }
}
