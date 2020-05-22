using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AircraftScript : MonoBehaviour
{
    [System.NonSerialized]
    public Rigidbody R;
    public AircraftWingSystem wingSystem;

    [System.NonSerialized]
    public RotationMechanism rotatorAileronRight_outer;
    [System.NonSerialized]
    public RotationMechanism rotatorAileronRight_mid;
    [System.NonSerialized]
    public RotationMechanism rotatorAileronRight_inner;
    [System.NonSerialized]
    public RotationMechanism rotatorAileronLeft_outer;
    [System.NonSerialized]
    public RotationMechanism rotatorAileronLeft_mid;
    [System.NonSerialized]
    public RotationMechanism rotatorAileronLeft_inner;
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
        rotatorAileronRight_outer = new RotationMechanism(transform.GetChild(0), new Vector3(-0, 0, 0), new Vector3(1, 0, 0), 5);
        rotatorAileronRight_mid = new RotationMechanism(transform.GetChild(1), new Vector3(-1.5f, 0, 0), new Vector3(1, 0, 0), 5);
        rotatorAileronRight_inner = new RotationMechanism(transform.GetChild(2), new Vector3(-3.0f, 0, 0), new Vector3(1, 0, 0), 5);

        rotatorAileronLeft_outer = new RotationMechanism(transform.GetChild(3), new Vector3(-0, 0, 0), new Vector3(1, 0, 0), -5);
        rotatorAileronLeft_mid = new RotationMechanism(transform.GetChild(4), new Vector3(-1.5f, 0, 0), new Vector3(1, 0, 0), -5);
        rotatorAileronLeft_inner = new RotationMechanism(transform.GetChild(5), new Vector3(-3.0f, 0, 0), new Vector3(1, 0, 0), -5);

        rotatorElevator = new RotationMechanism(transform.GetChild(6), new Vector3(3, 0, 0), new Vector3(1, 0, 0), -15);
        rotatorAileronRight_outer.maxChange = 0.5f;
        rotatorAileronRight_mid.maxChange = 0.5f;
        rotatorAileronRight_inner.maxChange = 0.5f;
        rotatorAileronLeft_outer.maxChange = 0.5f;
        rotatorAileronLeft_mid.maxChange = 0.5f;
        rotatorAileronLeft_inner.maxChange = 0.5f;
        rotatorElevator.maxChange = 0.5f;

        wingSystem = new AircraftWingSystem(R);
        // Wing Right
        wingSystem.wings.Add(new Wing(11.50f * Vector3.right + 0.0f * Vector3.back, transform.GetChild(0), 5.06f));
        wingSystem.wings.Add(new Wing(7.17f * Vector3.right + 0.1f * Vector3.back, transform.GetChild(1), 7.58f));
        wingSystem.wings.Add(new Wing(2.84f * Vector3.right + 0.2f * Vector3.back, transform.GetChild(2), 10.12f));
        // Wing Left
        wingSystem.wings.Add(new Wing(11.50f * Vector3.left + 0.0f * Vector3.back, transform.GetChild(3), 5.06f));
        wingSystem.wings.Add(new Wing(7.17f * Vector3.left + 0.1f * Vector3.back, transform.GetChild(4), 7.58f));
        wingSystem.wings.Add(new Wing(2.84f * Vector3.left + 0.2f * Vector3.back, transform.GetChild(5), 10.12f));

        wingSystem.wings.Add(new Wing(Vector3.zero, transform.GetChild(6), 2 * 3.094f));
        wingSystem.wings.Add(new Wing(Vector3.zero, transform.GetChild(7), 1.8f));
        wingSystem.wings.Add(new Wing(Vector3.zero, transform.GetChild(8), 1.8f));


        rotatorBrakeLeft = new RotationMechanism(transform.GetChild(9), new Vector3(0, 0, -27), Vector3.up, 80);
        rotatorBrakeRight = new RotationMechanism(transform.GetChild(10), new Vector3(0, 0, 27), Vector3.up, -80);
        rotatorBrakeBottom = new RotationMechanism(transform.GetChild(11), new Vector3(0, 0, -90), Vector3.up, -80);
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

    public void ResetControlInput()
    {
        inputElevator = 0;
        inputAileron = 0;
        inputBrake = 0;
        rotatorAileronRight_outer.Reset();
        rotatorAileronRight_mid.Reset();
        rotatorAileronRight_inner.Reset();
        rotatorAileronLeft_outer.Reset();
        rotatorAileronLeft_mid.Reset();
        rotatorAileronLeft_inner.Reset();
        rotatorElevator.Reset();

        rotatorBrakeLeft.Reset();
        rotatorBrakeRight.Reset();
        rotatorBrakeBottom.Reset();
    }

    public void Simulate()
    {
        rotatorAileronRight_outer.Rotate(inputAileron);
        rotatorAileronRight_mid.Rotate(inputAileron);
        rotatorAileronRight_inner.Rotate(inputAileron);

        rotatorAileronLeft_outer.Rotate(inputAileron);
        rotatorAileronLeft_mid.Rotate(inputAileron);
        rotatorAileronLeft_inner.Rotate(inputAileron);

        rotatorElevator.Rotate(inputElevator);
        rotatorBrakeLeft.Rotate(Mathf.Clamp01(inputBrake));
        rotatorBrakeRight.Rotate(Mathf.Clamp01(inputBrake));
        rotatorBrakeBottom.Rotate(Mathf.Clamp01(inputBrake));
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
