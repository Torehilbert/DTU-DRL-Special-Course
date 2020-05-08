using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AircraftScript : MonoBehaviour
{
    public Rigidbody R;
    public AircraftWingSystem wingSystem;
    RotationMechanism rotatorAileronRight;
    RotationMechanism rotatorAileronLeft;
    RotationMechanism rotatorElevator;
    RotationMechanism rotatorRudder;

    JetEngine engine;

    public float inputAileron = 0;
    public float inputElevator = 0;
    public float inputRudder = 0;
    public float inputEngine = 0;

    private void Awake()
    {
        R = GetComponent<Rigidbody>();
        R.centerOfMass = Vector3.zero;
        R.inertiaTensor = 4 * R.mass * Vector3.one;

        rotatorAileronRight = new RotationMechanism(transform.GetChild(0), new Vector3(-1, 0, 0), new Vector3(1, 0, 0), 3);
        rotatorAileronLeft = new RotationMechanism(transform.GetChild(1), new Vector3(-1, 0, 0), new Vector3(1, 0, 0), -3);
        rotatorElevator = new RotationMechanism(transform.GetChild(2), new Vector3(3, 0, 0), new Vector3(1, 0, 0), -10);
        rotatorElevator.maxChange = 0.5f;
        rotatorRudder = new RotationMechanism(transform.GetChild(3), new Vector3(0, 0, 90), new Vector3(1, 0, 0), -10);

        wingSystem = new AircraftWingSystem(R);
        wingSystem.wings.Add(new Wing(Vector3.zero, transform.GetChild(0), 3));
        wingSystem.wings.Add(new Wing(Vector3.zero, transform.GetChild(1), 3));
        wingSystem.wings.Add(new Wing(Vector3.zero, transform.GetChild(2), 3.75f));
        wingSystem.wings.Add(new Wing(Vector3.zero, transform.GetChild(3), 1.875f));
        wingSystem.wings.Add(new Wing(Vector3.zero, transform.GetChild(4), 2 * 1.875f));

        engine = new JetEngine(R, transform, Vector3.zero, Vector3.forward);
    }

    public void SetControlInput(float[] inputs)
    {
        inputAileron = inputs[0];
        inputElevator = inputs[1];
        inputRudder = inputs[2];
        inputEngine = inputs[3];
    }

    public void Simulate()
    {
        engine.Throttle = inputEngine;
        rotatorAileronRight.Rotate(inputAileron);
        rotatorAileronLeft.Rotate(inputAileron);
        rotatorElevator.Rotate(inputElevator);
        rotatorRudder.Rotate(inputRudder);
        wingSystem.ApplyForces();
        engine.ApplyForce();
    }

    void FixedUpdate()
    {
        Simulate();
    }

    void PrintLiftToDragRatios()
    {
        List<float> ld = wingSystem.wings[0].GetLiftToDrag(25);
        string msg = "LD: ";
        for (int i = 0; i < ld.Count; i++)
        {
            msg = msg + ld[i].ToString("0.00") + "\n";
        }
        Debug.Log(msg);
    }
}
