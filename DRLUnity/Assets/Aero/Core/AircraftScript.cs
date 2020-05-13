using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AircraftScript : MonoBehaviour
{
    [System.NonSerialized]
    public Rigidbody R;
    public AircraftWingSystem wingSystem;

    [System.NonSerialized]
    public RotationMechanism rotatorAileronRight;
    [System.NonSerialized]
    public RotationMechanism rotatorAileronLeft;
    [System.NonSerialized]
    public RotationMechanism rotatorElevator;
    [System.NonSerialized]
    public RotationMechanism rotatorRudder;

    [System.NonSerialized]
    public RotationMechanism rotatorBrakeLeft;
    [System.NonSerialized]
    public RotationMechanism rotatorBrakeRight;
    [System.NonSerialized]
    public RotationMechanism rotatorBrakeBottom;

    FlightBrakes brakes;

    public float inputAileron = 0;
    public float inputElevator = 0;
    public float inputBrake = 0;


    private void Awake()
    {
        R = GetComponent<Rigidbody>();
        R.centerOfMass = Vector3.zero;
        R.inertiaTensor = 10 * R.mass * Vector3.one;
        rotatorAileronRight = new RotationMechanism(transform.GetChild(0), new Vector3(-2, 0, 0), new Vector3(1, 0, 0), 5);
        rotatorAileronLeft = new RotationMechanism(transform.GetChild(1), new Vector3(-2, 0, 0), new Vector3(1, 0, 0), -5);
        rotatorElevator = new RotationMechanism(transform.GetChild(2), new Vector3(3, 0, 0), new Vector3(1, 0, 0), -15);
        rotatorAileronRight.maxChange = 0.5f;
        rotatorAileronLeft.maxChange = 0.5f;
        rotatorElevator.maxChange = 0.5f;

        wingSystem = new AircraftWingSystem(R);
        wingSystem.wings.Add(new Wing(6.5f * Vector3.right + 0.2f * Vector3.back, transform.GetChild(0), 22.75f));
        wingSystem.wings.Add(new Wing(6.5f * Vector3.left + 0.2f * Vector3.back, transform.GetChild(1), 22.75f));
        wingSystem.wings.Add(new Wing(Vector3.zero, transform.GetChild(2), 2 * 3.094f));
        wingSystem.wings.Add(new Wing(Vector3.zero, transform.GetChild(3), 1.8f));

        rotatorBrakeLeft = new RotationMechanism(transform.GetChild(4), new Vector3(0, 0, -27), Vector3.up, 80);
        rotatorBrakeRight = new RotationMechanism(transform.GetChild(5), new Vector3(0, 0, 27), Vector3.up, -80);
        rotatorBrakeBottom = new RotationMechanism(transform.GetChild(6), new Vector3(0, 0, -90), Vector3.up, -80);
        rotatorBrakeLeft.maxChange = 2f;
        rotatorBrakeRight.maxChange = 2f;
        rotatorBrakeBottom.maxChange = 2f;
        brakes = new FlightBrakes(rotatorBrakeBottom, 3 * 1f);
    }


    public void SetControlInput(float[] inputs)
    {
        inputElevator = inputs[0];
        inputAileron = inputs[1];
        inputBrake = inputs[2];
    }


    public void Simulate()
    {
        rotatorAileronRight.Rotate(inputAileron);
        rotatorAileronLeft.Rotate(inputAileron);
        rotatorElevator.Rotate(inputElevator);
        rotatorBrakeLeft.Rotate(inputBrake);
        rotatorBrakeRight.Rotate(inputBrake);
        rotatorBrakeBottom.Rotate(inputBrake);
        wingSystem.ApplyForces();

        Force brakeForce = brakes.GetForce(R);
        R.AddForceAtPosition(brakeForce.force, brakeForce.position);
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
