using UnityEngine;
using System.Collections;

public class FlightBrakes
{
    RotationMechanism rotator;
    float dragCoefficientMin = 0.05f;
    float dragCoefficientMax = 1.28f;
    float dragCoefficientMaxDegress = 90f;
    float area;


    public FlightBrakes(RotationMechanism rotator, float area)
    {
        this.rotator = rotator;
        this.area = area;
    }


    public Force GetForce(Rigidbody rigidbody)
    {
        Force force = new Force();

        float currentAngle = Mathf.Sign(rotator.magnitude) * rotator.smoothAngle;

        float brakeActivation = currentAngle / dragCoefficientMaxDegress;
        float cosineInterpolationValue = 1 - (0.5f * Mathf.Cos(brakeActivation * Mathf.PI) + 0.5f);
        float dragCoefficient = cosineInterpolationValue * dragCoefficientMax + (1 - cosineInterpolationValue) * dragCoefficientMin;
        float crossSectionalArea = area * Mathf.Sin(brakeActivation * 0.5f * Mathf.PI);
        //Debug.Log("Act: " + brakeActivation + "  intp: " + cosineInterpolationValue + "  cd: " + dragCoefficient + "  csA: " + crossSectionalArea);
        float forceMagnitude = 0.5f * 1.225f * rigidbody.velocity.sqrMagnitude * dragCoefficient * crossSectionalArea;
        Vector3 forceDirection = -rigidbody.velocity.normalized;

        return new Force(rigidbody.position, forceMagnitude * forceDirection);
    }
    
}
