using UnityEngine;
using System.Collections;

public struct FlightSpawnProperties
{
    public Vector3 position;
    public Quaternion rotation;
    public Vector3 velocity;
    public Vector3 angularVelocity;


    const float slopeMin = 3.75f;
    const float slopeMax = 9;
    const float slopeHeadingMaxDeviation = 10;
    const float distanceMin = 100;
    const float distanceMax = 750;
    const float speedMin = 25;
    const float speedMax = 40;
    const float headingMaxDeviation = 10;
    const float bankMaxDeviation = 0;

    public FlightSpawnProperties(Vector3 position, Quaternion rotation, Vector3 velocity, Vector3 angularVelocity)
    {
        this.position = position;
        this.rotation = rotation;
        this.velocity = velocity;
        this.angularVelocity = angularVelocity;
    }


    public static FlightSpawnProperties Generate()
    {
        float slope = Random.Range(slopeMin, slopeMax);
        float distance = Random.Range(distanceMin, distanceMax);
        float speed = Random.Range(speedMin, speedMax);
        float slopeHeading = Random.Range(-slopeHeadingMaxDeviation, slopeHeadingMaxDeviation);
        float bank = Random.Range(-bankMaxDeviation, bankMaxDeviation);

        Vector3 position = Quaternion.AngleAxis(slopeHeading, Vector3.up) * (Quaternion.AngleAxis(slope, Vector3.left) * (distance * Vector3.forward));
        Vector3 forward = -position.normalized;
        Quaternion rotation = Quaternion.LookRotation(forward, Vector3.up) * Quaternion.AngleAxis(bank, forward);
        Vector3 velocity = speed * forward;
        return new FlightSpawnProperties(position, rotation, velocity, Vector3.zero);
    }
}
