using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class JetEngine
{
    float throttle = 0;
    public float Throttle
    {
        get
        {
            return throttle;
        }
        set
        {
            throttle = Mathf.Clamp01(value);
        }
    }

    public float rpm { get; private set; } = 0;
    public float MaxForce { get; set; } = 1500;
    public float MaxRPMChange { get; set; } = 0.02f;
    public Rigidbody rigidbody;
    public Transform parent;
    public Vector3 localPosition;
    public Vector3 localThrustDirection;


    public JetEngine(Rigidbody rigidbody, Transform parent, Vector3 localPosition, Vector3 localThrustDirection)
    {
        this.rigidbody = rigidbody;
        this.parent = parent;
        this.localPosition = localPosition;
        this.localThrustDirection = localThrustDirection;
    }

    public void ApplyForce()
    {
        rpm += Mathf.Clamp(Throttle - rpm, -MaxRPMChange, MaxRPMChange);
        float forceMagnitude = rpm * MaxForce;
        Vector3 thrustDirection = parent.TransformDirection(localThrustDirection).normalized;
        rigidbody.AddForceAtPosition(thrustDirection * forceMagnitude, parent.TransformPoint(localPosition));
    }
}
