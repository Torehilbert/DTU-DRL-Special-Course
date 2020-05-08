using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class Wing
{
    public float AngleOfAttack { get; private set; }


    public float wingArea;
    public AirProfile liftProfile;
    public AirProfile dragProfile;

    public Transform parent = null;
    public Vector3 localPosition = Vector3.zero;
    public bool debugOn = false;

    public Wing(Vector3 localPosition, Transform parent, float wingArea)
    {
        this.localPosition = localPosition;
        this.parent = parent;
        this.wingArea = wingArea;

        liftProfile = Resources.Load<AirProfile>("LiftCoefficient");
        dragProfile = Resources.Load<AirProfile>("DragCoefficient");
    }


    public Force GetForce()
    {
        return GetForce(Vector3.zero);
    }


    public Force GetForce(Rigidbody rigidbody)
    {
        Vector3 worldPosition = parent.TransformPoint(localPosition);
        return GetForce(rigidbody.GetPointVelocity(worldPosition), worldPosition);
    }


    public Force GetForce(Vector3 velocity)
    {
        Vector3 worldPosition = parent.TransformPoint(localPosition);
        return GetForce(velocity, worldPosition);
    }


    public Force GetForce(Vector3 velocity, Vector3 worldPosition)
    {
        AngleOfAttack = Vector3.Angle(parent.up, velocity) - 90;
        if (debugOn)
            Debug.Log("Aoa: " + AngleOfAttack);
        Vector3 liftDirection = Vector3.Cross(velocity, Vector3.Cross(parent.up, velocity)).normalized;
        Vector3 dragDirection = -velocity.normalized;

        float liftForce = 0.5f*1.225f*velocity.sqrMagnitude*liftProfile.Sample(AngleOfAttack) * wingArea;
        float dragForce = 0.5f*1.225f*velocity.sqrMagnitude*dragProfile.Sample(AngleOfAttack) * wingArea;
        Debug.DrawLine(worldPosition, worldPosition + liftForce * liftDirection / 750, Color.green);
        Vector3 force = liftForce * liftDirection + dragForce * dragDirection;
        return new Force(worldPosition, force);
    }

    public void TurnDebugOn()
    {
        debugOn = true;
    }

    public List<float> GetLiftToDrag(int aoamax)
    {
        List<float> ld = new List<float>();
        for (int i=0; i <= aoamax; i++)
        {
            ld.Add(liftProfile.Sample(i) / dragProfile.Sample(i));
        }
        return ld;
    }
}

/*
 * 			Vector3 norm = W.up;
			Vector3 forw = W.forward;
			Vector3 cop = T.TransformPoint(W.localPosition);
			Vector3 vel = R.GetPointVelocity (cop);
			float aoa = Vector3.Angle (norm, vel) - 90;
			float cl = FC.interp1 ("CL", aoa);
			float cd = FC.interp1 ("CD", aoa);
			Vector3 liftDir = Vector3.Cross(vel, Vector3.Cross(norm, vel)).normalized;
			Vector3 lift = 0.5f*1.225f*vel.sqrMagnitude*FC.wingArea*cl*liftDir;
			Vector3 drag = -0.5f*1.225f*vel.sqrMagnitude*FC.wingArea*cd*vel.normalized;
			if (aoa > 19) {
				Debug.DrawLine (cop, cop + lift / 750, Color.yellow);
			} else {
				Debug.DrawLine (cop, cop + lift / 750, Color.green);
			}
			Debug.DrawLine (cop, cop + drag/750,Color.red);
			R.AddForceAtPosition(lift+drag, cop);
            */
