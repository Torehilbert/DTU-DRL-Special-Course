using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[CreateAssetMenu(fileName = "AirProfile", menuName = "Profiles/AirProfile", order = 1)]
public class AirProfile : ScriptableObject
{
    public AnimationCurve profile;
    public float negativeAOACoefficient = -1;

    public float Sample(float aoa)
    {
        if(aoa < -90 || aoa > 90)
            throw new System.Exception("Angle of attack is outside range!");

        if (aoa < 0)
            return negativeAOACoefficient * profile.Evaluate(-aoa);
        else
            return profile.Evaluate(aoa);
    }
}
