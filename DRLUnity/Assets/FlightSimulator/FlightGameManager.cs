using UnityEngine;
using System.Collections;
using ArgumentParsing;


public class FlightGameManager : MonoBehaviour
{
    public event System.Action<float[]> onStateChange;
    public event System.Action<float[]> onActionValueChange;
    public event System.Action<FlightLandingReport> onEpisodeEnded;

    public static FlightGameManager instance;
    public const int observationDimension = 16;
    public const int actionDimension = 3;

    public FlightInputReader flightInputReader;
    public AircraftScript aircraftScript;
    public RunwayTouchDownDetector runwayTouchDownDetector;
    public Rigidbody airplane;

    AircraftAnalytics analytics;
    AgentController agentController;

    float[] state = new float[observationDimension];
    bool done = false;

    [System.NonSerialized]
    public bool touchedDown = false;
    [System.NonSerialized]
    public RunwayTouchDownDetector.TouchDownReport touchDownReport;

    FlightLandingReport landingReport;

    string[] messageArgumentSeparator = new string[] { "," };
    string[] messageKeyValueSeparator = new string[] { "=" };

    public bool exitButtonPressed = false;
    public bool resetButtonPressed = false;

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
        argParser.ParseArguments();

        Application.targetFrameRate = argParser.GetIntArgument("-targetFrameRate");
        QualitySettings.vSyncCount = 0;

        externalAgent = argParser.arguments["-portAgentSend"].isSupplied && argParser.arguments["-portAgentReceive"].isSupplied;
        portAgentSend = argParser.arguments["-portAgentSend"].valueInt;
        portAgentReceive = argParser.arguments["-portAgentReceive"].valueInt;
        
        if (externalAgent)
            agentController = new BoxExternalAgentController(observationDimension, actionDimension, portAgentSend, portAgentReceive);
        else
            agentController = new FlightHumanAgentController(flightInputReader);

        ResetEnvironment();
    }

    // Update is called once per frame
    void Update()
    {
        // Check UI buttons
        if (resetButtonPressed)
        {
            ResetEnvironment();
            resetButtonPressed = false;
            return;
        }
        if (exitButtonPressed)
        {
            agentController.CloseAgent();
            Close();
            return;
        }

        // Update state
        analytics.UpdateAnalytics();
        UpdateState();
        onStateChange?.Invoke(state);

        // Calculate reward
        float reward = CalculateReward();

        // Check done
        if (touchedDown && !done)
        {
            onEpisodeEnded?.Invoke(landingReport);
            done = true;
        }

        // Get action from agent
        AgentController.ActionResponse response = agentController.GetActionResponse(0, state, reward, done);

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
        {
            ResetEnvironment();
            return;
        }
        else
        {
            // Execute physics
            aircraftScript.SetControlInput(response.actions);
            aircraftScript.Simulate();
            Physics.Simulate(0.02f);  // note: onCollision events happens on this call      
            onActionValueChange?.Invoke(response.actions);
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
        // Position
        state[0] = airplane.position.magnitude;
        state[1] = airplane.position.x;
        state[2] = airplane.position.y;
        state[3] = airplane.position.z;

        // Velocity
        state[4] = analytics.Velocity;
        state[5] = airplane.velocity.x;
        state[6] = airplane.velocity.y;
        state[7] = airplane.velocity.z;

        // Rotation
        state[8] = analytics.Bank;
        state[9] = analytics.Pitch;
        state[10] = analytics.Heading * Mathf.Deg2Rad;
        state[11] = Mathf.Cos(analytics.Heading * Mathf.Deg2Rad);
        state[12] = Mathf.Sin(analytics.Heading * Mathf.Deg2Rad);

        // Angular velocity
        state[13] = analytics.AngVelBank;
        state[14] = analytics.AngVelPitch;
        state[15] = analytics.AngVelYaw;
    }


    float CalculateReward()
    {
        if (touchedDown)
        {
            if (touchDownReport.isWheel && FlightLandingReport.AcceptableZ(state[3]))
            {
                landingReport = new FlightLandingReport(
                    state[10], 
                    state[1], 
                    state[8], 
                    touchDownReport.relativeVelocity.magnitude, 
                    touchDownReport.relativeVelocity.y
                );
                return 100 * landingReport.rating;
            }
            else
            {
                landingReport = null;
                return -1;
            }
        }
        return -0.001f;
    }


    void ResetEnvironment()
    {
        done = false;
        FlightSpawnProperties properties = FlightSpawnProperties.Generate();

        airplane.transform.position = properties.position; // new Vector3(0, 100, 750);
        airplane.transform.rotation = properties.rotation; // Quaternion.Euler(0, 180, 0);
        airplane.velocity = properties.velocity; // - 30 * Vector3.forward; // airplane.transform.forward;
        airplane.angularVelocity = properties.angularVelocity; // Vector3.zero;
        runwayTouchDownDetector.touchDown = false;
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
