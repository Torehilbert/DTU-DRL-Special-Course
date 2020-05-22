using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FlightWind
{
    public static Vector3 windDirection = Vector3.forward;
    public static float windPower = 5;
    public static float windMean = 5;
    public static float pitchDeviationMax = 25;
    public static float yawDeviationMax = 25;

    public static Vector3 GetWind(Vector3 position)
    {
        float magnitude = windMean + windPower * (2*Mathf.PerlinNoise(0.1f * position.x, 0.1f * position.z) - 0.5f);
        float heightCoefficient = 0;
        if (position.y > 0)
            heightCoefficient = Mathf.Sqrt(0.2f * position.y) / (1 + Mathf.Sqrt(0.2f * position.y));
        float rollYaw = 2*(Mathf.PerlinNoise(0.03f * position.x + 1000, 0.03f * position.z + 1000) - 0.5f);
        float pitchYaw = 2 * (Mathf.PerlinNoise(0.03f * position.x + 2000, 0.03f * position.z + 2000) - 0.5f);

        Vector3 direction = Quaternion.AngleAxis(yawDeviationMax * rollYaw, Vector3.up) * (Quaternion.AngleAxis(pitchDeviationMax* pitchYaw, Vector3.Cross(windDirection, Vector3.up)) *  windDirection);
        return heightCoefficient * magnitude * direction;
    }


    public static void SetWindDirection(float angle)
    {
        windDirection = Quaternion.AngleAxis(angle, Vector3.up) * Vector3.forward;
    }
}
