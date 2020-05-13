using UnityEngine;
using System.Collections;

public class FlightLandingReport
{
    public float rewardHeading;
    public float rewardX;
    public float rewardBank;
    public float rewardIAS;
    public float rewardVSI;
    public float rating;

    public FlightLandingReport(float headingRadians, float x, float bank, float ias, float vsi)
    {
        rewardHeading = GetRewardHeading(headingRadians);
        rewardX = GetRewardX(x);
        rewardBank = GetRewardBank(bank);
        rewardIAS = GetRewardIAS(ias);
        rewardVSI = GetRewardVSI(vsi);

        rating = 2 * (rewardHeading + rewardX + rewardBank + rewardIAS + rewardVSI);
    }

    
    public float GetRewardHeading(float headingRadians)
    {
        return Mathf.Exp(-0.5f * (headingRadians - Mathf.PI) * (headingRadians - Mathf.PI) / 0.0076f);
    }

    
    public float GetRewardX(float x)
    {
        return Mathf.Exp(-0.5f * (x * x) / 9);
    }


    public static bool AcceptableZ(float z)
    {
        if (z < 15 && z > -15)
            return true;
        else
            return false;
    }


    public float GetRewardBank(float bank)
    {
        return Mathf.Exp(-0.5f * (bank * bank) / 9);
    }


    public float GetRewardIAS(float ias)
    {
        return ias < 25 ? 1 : Mathf.Exp(-0.5f * (ias - 25) * (ias - 25) / 25);
    }


    public float GetRewardVSI(float vsi)
    {
        return Mathf.Exp(-0.5f * (vsi * vsi) / 4);
    }
}
