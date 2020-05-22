using UnityEngine;
using System.Collections;
using ArgumentParsing;


public class FlightGameManager : MonoBehaviour
{
    public event System.Action<float[]> onStateChange;
    public event System.Action<float[]> onActionValueChange;
    public event System.Action<FlightLandingReport> onEpisodeEnded;

    public static FlightGameManager instance;
    public const int observationDimension = 15;
    public const int actionDimension = 3;

    public FlightInputReader flightInputReader;
    public AircraftScript aircraftScript;
    public RunwayTouchDownDetector runwayTouchDownDetector;
    public RunwayTouchDownDetector terrainTouchDownDetector;
    public FlightTreeGenerator treeGenerator;
    public Rigidbody airplane;

    AircraftAnalytics analytics;
    AgentController agentController;
    AgentController.ActionResponse response;
    float[] actionsOld = null;
    int responseCount = 0;

    float[] state = new float[observationDimension];
    bool done = false;

    [System.NonSerialized]
    public float difficulty;
    float penaltyActionCoefficient;
    float penaltyTimeCoefficient;
    int actionFrequency;
    int actionSkipCounter;
    float currentReward = 0;
    [System.NonSerialized]
    public float totalActionRewardPenalty = 0;
    [System.NonSerialized]
    public float totalTimeRewardPenalty = 0;

    [System.NonSerialized]
    public bool touchedDown = false;
    [System.NonSerialized]
    public RunwayTouchDownDetector.TouchDownReport touchDownReport;

    FlightLandingReport landingReport;

    string[] messageArgumentSeparator = new string[] { "," };
    string[] messageKeyValueSeparator = new string[] { "=" };

    bool initialRun = true;
    public bool resetOrdered = false;
    public bool exitOrdered = false;

    // Parameters
    bool externalAgent;
    int portAgentSend;
    int portAgentReceive;

    void Awake()
    {
        instance = this;
        Physics.autoSimulation = false;

        analytics = new AircraftAnalytics(airplane, airplane.transform);

        ArgumentParser argParser = new ArgumentParser();
        argParser.AddArgument("-targetFrameRate", false, "50");
        argParser.AddArgument("-portAgentSend", false, "26001");
        argParser.AddArgument("-portAgentReceive", false, "26000");
        argParser.AddArgument("-trees", false, "1");
        argParser.AddArgument("-difficulty", false, "1.0");
        argParser.AddArgument("-actionFrequency", false, "1");
        argParser.AddArgument("-windAngle", false, "0");
        argParser.AddArgument("-windPower", false, "2.5");
        argParser.AddArgument("-windAngleDeviation", false, "25");
        argParser.AddArgument("-penaltyActionCoefficient", false, "0.000");
        argParser.AddArgument("-penaltyTimeCoefficient", false, "0.00000");
        argParser.ParseArguments();

        difficulty = argParser.arguments["-difficulty"].valueFloat;
        actionFrequency = argParser.arguments["-actionFrequency"].valueInt;
        penaltyActionCoefficient = argParser.arguments["-penaltyActionCoefficient"].valueFloat;
        penaltyTimeCoefficient = argParser.arguments["-penaltyTimeCoefficient"].valueFloat;
        FlightWind.windPower = argParser.arguments["-windPower"].valueFloat;
        FlightWind.windMean = FlightWind.windPower;
        FlightWind.pitchDeviationMax = argParser.arguments["-windAngleDeviation"].valueFloat;
        FlightWind.yawDeviationMax = argParser.arguments["-windAngleDeviation"].valueFloat;
        FlightWind.SetWindDirection(argParser.arguments["-windAngle"].valueFloat);
        Application.targetFrameRate = argParser.GetIntArgument("-targetFrameRate");
        QualitySettings.vSyncCount = 0;

        externalAgent = argParser.arguments["-portAgentSend"].isSupplied && argParser.arguments["-portAgentReceive"].isSupplied;
        portAgentSend = argParser.arguments["-portAgentSend"].valueInt;
        portAgentReceive = argParser.arguments["-portAgentReceive"].valueInt;
        
        if (externalAgent)
            agentController = new BoxExternalAgentController(observationDimension, actionDimension, portAgentSend, portAgentReceive);
        else
            agentController = new FlightHumanAgentController(flightInputReader);

        if (argParser.arguments["-trees"].valueInt == 1)
            treeGenerator.enabled = true;

    }

    // Update is called once per frame
    void Update()
    {
        // Check UI buttons
        if (initialRun || resetOrdered)
        {
            ResetEnvironment();
            resetOrdered = false;
            initialRun = false;
            return;
        }
        if (exitOrdered)
        {
            agentController.CloseAgent();
            Close();
            return;
        }

        // Execute Physics
        ExecutePhysics();

        // Update state
        analytics.UpdateAnalytics();
        UpdateState();
        onStateChange?.Invoke(state);
        
        // Calculate reward
        currentReward += CalculateReward();

        // Check done
        if (touchedDown && !done)
        {
            onEpisodeEnded?.Invoke(landingReport);
            done = true;
        }
        if (airplane.position.z < 0)
        {
            done = true;
        }

        // Get action from agent
        if(actionSkipCounter == actionFrequency || done)
        {
            for (int i = 0; i < actionsOld.Length; i++)
                actionsOld[i] = response.actions[i];

            response = agentController.GetActionResponse(0, state, currentReward, done);
            responseCount++;
            aircraftScript.SetControlInput(response.actions);
            onActionValueChange?.Invoke(response.actions);
            actionSkipCounter = 1;
            currentReward = 0;       
        }
        else
            actionSkipCounter++;

        // Perform configurations received from custom message string in agent response
        if (response.msg.Length > 0)
        {
            //BoxLogUI.instance.Log("Received message from agent: ");
            foreach (string s in response.msg.Split(messageArgumentSeparator, System.StringSplitOptions.None))
            {
                //BoxLogUI.instance.Log(s);
                HandleMessage(s);
            }
        }

        // Perform exit or reset on environment if told so by agent, else run physics
        if (response.symbol == AgentController.AgentActionSymbol.Exit)
            Close();
        else if (response.symbol == AgentController.AgentActionSymbol.Reset)
            resetOrdered = true;
    }

    void ExecutePhysics()
    {
        Physics.Simulate(0.02f);  // note: onCollision events happens on this call      
        aircraftScript.Simulate();
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
        float referenceSlope = 3;

        state[0] = Vector3.SignedAngle(Vector3.ProjectOnPlane(-airplane.position, Vector3.up), Vector3.back, Vector3.up) / 10;              // theta_p_h
        state[1] = (Vector3.SignedAngle(Vector3.ProjectOnPlane(-airplane.position, Vector3.right), Vector3.back, Vector3.right) - referenceSlope) / 10;  // theta_p_v
        
        state[2] = (float)System.Math.Tanh(airplane.position.magnitude / 250);    // pmag
        state[3] = (float)System.Math.Tanh(0.05f * airplane.position.x);     // runway x alignment
        state[4] = (float)System.Math.Tanh(0.25f * (airplane.position.y - 2.5f));    // runway height feature

        state[5] = state[0] - Vector3.SignedAngle(Vector3.ProjectOnPlane(airplane.velocity, Vector3.up), Vector3.back, Vector3.up) / 10;    // theta_v_h
        state[6] = state[1] - (Vector3.SignedAngle(Vector3.ProjectOnPlane(airplane.velocity, Vector3.right), Vector3.back, Vector3.right) - referenceSlope) / 10;  // theta_v_v
        state[7] = (airplane.velocity.magnitude - 25) / 5;
        
        state[8] = analytics.Bank / 10;
        state[9] = analytics.Pitch / 5;
        state[10] = Mathf.Cos(analytics.Heading * Mathf.Deg2Rad);
        state[11] = 5*Mathf.Sin(analytics.Heading * Mathf.Deg2Rad);

        state[12] = analytics.AngVelBank / 15;
        state[13] = analytics.AngVelPitch / 15;
        state[14] = analytics.AngVelYaw / 15;
    }


    float CalculateReward()
    {
        // reward if touchdown
        if (touchedDown)
        {
            if (touchDownReport.isWheel && FlightLandingReport.AcceptableZ(airplane.position.z))
            {
                landingReport = new FlightLandingReport(
                    analytics.Heading * Mathf.Deg2Rad, 
                    airplane.position.x,
                    analytics.Bank, 
                    touchDownReport.relativeVelocity.magnitude, 
                    touchDownReport.relativeVelocity.y
                );
                return landingReport.rating;
            }
            else
            {
                landingReport = null;
                return -1;
            }
        }

        // reward if in step
        float rewardPenaltyTime = -penaltyTimeCoefficient;
        totalTimeRewardPenalty += rewardPenaltyTime;
        if (responseCount > 2)
        {
            float rewardPenaltyAction = 0;
            for (int i=0; i<actionsOld.Length; i++)
                rewardPenaltyAction += -penaltyActionCoefficient * Mathf.Abs(response.actions[i] - actionsOld[i]);

            totalActionRewardPenalty += rewardPenaltyAction;
            return rewardPenaltyTime + rewardPenaltyAction;
        }
        else
        {
            return rewardPenaltyTime;
        }
    }


    void ResetEnvironment()
    {
        actionSkipCounter = actionFrequency;
        FlightSpawnProperties properties = FlightSpawnProperties.Generate(difficulty);

        airplane.transform.position = properties.position; // new Vector3(0, 100, 750);
        airplane.transform.rotation = properties.rotation; // Quaternion.Euler(0, 180, 0);
        airplane.velocity = properties.velocity; // - 30 * Vector3.forward; // airplane.transform.forward;
        airplane.angularVelocity = properties.angularVelocity; // Vector3.zero;
        done = false;
        touchedDown = false;
        runwayTouchDownDetector.touchDown = false;
        terrainTouchDownDetector.touchDown = false;

        actionsOld = new float[3] { 0, 0, 0 };
        responseCount = 0;
        totalActionRewardPenalty = 0;
        response = new AgentController.ActionResponse();
        response.actions = new float[] { 0, 0, 0 };
        response.symbol = AgentController.AgentActionSymbol.Continue;
        response.msg = "";
        aircraftScript.ResetControlInput();
    }


    public void HandleMessage(string message)
    {
        string[] splits = message.Split(messageKeyValueSeparator, System.StringSplitOptions.None);
        if (splits.Length == 2)
        {
            //...
        }
    }
}
