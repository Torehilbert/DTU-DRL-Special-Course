using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AircraftAnalytics
{
    public float Pitch { get; private set; }
    public float Bank { get; private set; }
    public float Heading { get; private set; }
    public float Velocity { get; private set; }
    public float DescentRate { get; private set; }
    public float GlideRatio { get; private set; }
    public float AngVelPitch { get; private set; }
    public float AngVelBank { get; private set; }
    public float AngVelYaw { get; private set; }
    public float Unsteadiness { get; private set; }

    Rigidbody R;
    Transform T;
    Vector3 lastAngVel = Vector3.zero;

    public AircraftAnalytics(Rigidbody rigidbody, Transform transform)
    {
        R = rigidbody;
        T = transform;
    }

    public void UpdateAnalytics()
    {
        Pitch = Vector3.Angle(T.forward, Vector3.down) - 90;

        Vector3 helper = Vector3.Cross(Vector3.up, T.forward);
        Bank = Vector3.SignedAngle(helper, T.right, T.forward);


        Heading = Vector3.SignedAngle(Vector3.forward, Vector3.ProjectOnPlane(T.forward, Vector3.up), Vector3.up);
        if (Heading < 0)
            Heading = Heading + 360;
        Velocity = R.velocity.magnitude;

        DescentRate = R.velocity.y;
        GlideRatio = Vector3.ProjectOnPlane(R.velocity, Vector3.up).magnitude / R.velocity.y;

        // Calculate angular velocities
        Vector3 angVel = T.InverseTransformDirection(R.angularVelocity) * 180 / Mathf.PI;
        AngVelPitch = -angVel.x;
        AngVelBank = -angVel.z;
        AngVelYaw = -angVel.y;

        // Calculate unsteadiness
        Unsteadiness = (angVel - lastAngVel).magnitude;

        // Cache latest angular velocity
        lastAngVel = angVel;
    }
}
