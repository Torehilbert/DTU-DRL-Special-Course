using UnityEngine;
using System.Collections;

public class RotationMechanism
{
    public Transform transform;
    public Vector3 eulerAngles;
    public Vector3 rotationAxis;
    public float magnitude;
    public float maxChange = 1;
    public float smoothAngle;


    public RotationMechanism(Transform transform, Vector3 localEulerAngles, Vector3 localRotationAxis, float magnitude)
    {
        this.transform = transform;
        this.eulerAngles = localEulerAngles;
        this.rotationAxis = localRotationAxis;
        this.magnitude = magnitude;
        smoothAngle = 0;
    }


    public void Rotate(float input)
    {
        smoothAngle = smoothAngle + Mathf.Clamp(input * magnitude - smoothAngle, -maxChange, maxChange);
        RotateMechanism(smoothAngle);
    }


    public void Reset()
    {
        smoothAngle = 0;
        RotateMechanism(smoothAngle);
    }


    void RotateMechanism(float angle)
    {
        Quaternion rot = Quaternion.Euler(eulerAngles) * Quaternion.AngleAxis(angle, rotationAxis);
        transform.localRotation = rot;
    }
}