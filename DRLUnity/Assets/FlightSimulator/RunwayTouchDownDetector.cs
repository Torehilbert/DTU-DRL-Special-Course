using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RunwayTouchDownDetector : MonoBehaviour
{
    public struct TouchDownReport
    {
        public bool isWheel;
        public Vector3 wheelPosRight;
        public Vector3 wheelPosLeft;
        public Vector3 wheelPosFront;
        public Vector3 relativeVelocity;
    }

    public Collider wheelColliderRight;
    public Collider wheelColliderLeft;
    public Collider wheelColliderFront;

    [System.NonSerialized]
    public bool touchDown = false;
    public TouchDownReport report;

    Collider[] acceptableColliders;
    

    private void Awake()
    {
        acceptableColliders = new Collider[3];
        acceptableColliders[0] = wheelColliderRight;
        acceptableColliders[1] = wheelColliderLeft;
        acceptableColliders[2] = wheelColliderFront;
    }


    private void OnCollisionEnter(Collision collision)
    {
        if (touchDown)
            return;

        touchDown = true;

        bool acceptableCollision = false;
        for(int i=0; i<acceptableColliders.Length; i++)
        {
            if (collision.collider == acceptableColliders[i])
                acceptableCollision = true;
        }

        if (acceptableCollision)
        {
            Debug.Log("Acceptable collider touch: " + collision.collider.name);
            report = new TouchDownReport();
            report.wheelPosRight = wheelColliderRight.transform.position;
            report.wheelPosLeft = wheelColliderLeft.transform.position;
            report.wheelPosFront = wheelColliderFront.transform.position;
            report.relativeVelocity = collision.relativeVelocity;
            report.isWheel = true;

            Debug.DrawLine(collision.collider.transform.position, collision.collider.transform.position + Vector3.up * 4, Color.green, 10);
        }
        else
        {
            Debug.Log("Unacceptable collider touch: " + collision.collider.name);
            report = new TouchDownReport();
            report.isWheel = false;
        }

        FlightGameManager.instance.touchedDown = true;
        FlightGameManager.instance.touchDownReport = report;
    }
}
