using UnityEngine;
using System.Collections;

public class FlightCameraFollow : MonoBehaviour
{
    public Transform airplane;
    float distance = 20;
    float heightOffset = 1;
    float velocityLimit = 5;
    Rigidbody rigidbody;

    Vector3 targetDeltaPosition;
    Vector3 deltaPosition;

    void Start()
    {
        rigidbody = airplane.GetComponent<Rigidbody>();
    }


    void LateUpdate()
    {
        if (rigidbody.velocity.magnitude > velocityLimit)
            targetDeltaPosition = -distance * rigidbody.velocity.normalized + Vector3.up*heightOffset;
        deltaPosition = Vector3.Lerp(deltaPosition, targetDeltaPosition, Time.deltaTime);

        transform.position = rigidbody.position + deltaPosition;
        transform.LookAt(airplane);
    }
}
