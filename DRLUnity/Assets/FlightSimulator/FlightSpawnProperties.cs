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
    const float distanceMin = 50;
    const float distanceMax = 750;
    const float speedMin = 25;
    const float speedMax = 40;
    const float headingMaxDeviation = 10;
    const float bankMaxDeviation = 5;

    public FlightSpawnProperties(Vector3 position, Quaternion rotation, Vector3 velocity, Vector3 angularVelocity)
    {
        this.position = position;
        this.rotation = rotation;
        this.velocity = velocity;
        this.angularVelocity = angularVelocity;
    }


    public static FlightSpawnProperties Generate(float difficulty)
    {
        Roll roll = Roll.Generate();
        float distance = Mathf.Lerp(distanceMin, distanceMin + difficulty * (distanceMax - distanceMin), roll.interpolant);  // Random.Range(distanceMin, distanceMax);

        float distanceInterpolant = roll.interpolant;
        roll = Roll.Generate();
        float slope = Mathf.Lerp(slopeMin, slopeMin + distanceInterpolant * difficulty * (slopeMax - slopeMin), roll.interpolant); // Random.Range(slopeMin, slopeMax);

        roll = Roll.Generate();
        float speed = Mathf.Lerp(speedMin, speedMin + distanceInterpolant * difficulty * (speedMax - speedMin), roll.interpolant);  // Random.Range(speedMin, speedMax);

        roll = Roll.Generate();
        float slopeHeading = roll.sign * Mathf.Lerp(0, distanceInterpolant * difficulty * slopeHeadingMaxDeviation, roll.interpolant);  // Random.Range(-slopeHeadingMaxDeviation, slopeHeadingMaxDeviation);

        roll = Roll.Generate();
        float bank = roll.sign * Mathf.Lerp(0, distanceInterpolant * difficulty * bankMaxDeviation, roll.interpolant);  // Random.Range(-bankMaxDeviation, bankMaxDeviation);

        Vector3 position = Quaternion.AngleAxis(slopeHeading, Vector3.up) * (Quaternion.AngleAxis(slope, Vector3.left) * (distance * Vector3.forward)) + Vector3.forward * 50;
        Vector3 forward = -position.normalized;
        Quaternion rotation = Quaternion.LookRotation(forward, Vector3.up) * Quaternion.AngleAxis(bank, forward);
        Vector3 velocity = speed * forward;
        return new FlightSpawnProperties(position, rotation, velocity, Vector3.zero);
    }


    public static FlightSpawnProperties GenerateLimitTesting(float difficulty)
    {
        float distance = distanceMax + (difficulty > 1.01f ? 10 * (difficulty - 1.00f) : 0);
        float slope = (slopeMin + slopeMax) / 2;
        float speed = (speedMin + speedMax) / 2;

        float sign = (Random.Range(-1, 1) == -1? -1 : 1);
        float slopeHeading = sign * difficulty * 90;
        float bank = 0;

        Vector3 position = Quaternion.AngleAxis(slopeHeading, Vector3.up) * (Quaternion.AngleAxis(slope, Vector3.left) * (distance * Vector3.forward)) + Vector3.forward * 50;
        Vector3 forward = -position.normalized;
        Quaternion rotation = Quaternion.LookRotation(forward, Vector3.up) * Quaternion.AngleAxis(bank, forward);
        Vector3 velocity = speed * forward;
        return new FlightSpawnProperties(position, rotation, velocity, Vector3.zero);
    }


    struct Roll
    {
        public float interpolant;
        public float sign;

        public Roll(float interpolant, float sign)
        {
            this.interpolant = interpolant;
            this.sign = sign;
        }

        public static Roll Generate()
        {
            float activation = Random.Range(0f, 1f);
            activation = activation; // * activation;
            float sign = 2 * (Random.Range(0, 2) - 0.5f);
            return new Roll(activation, sign);
        }
    }
}
