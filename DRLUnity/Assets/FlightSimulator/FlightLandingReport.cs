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

        //rating = 2 * (rewardHeading + rewardX + rewardBank + rewardIAS + rewardVSI);
        rating = rewardHeading * rewardX * rewardBank * rewardIAS * rewardVSI;
    }

    
    public float GetRewardHeading(float headingRadians)
    {
        //return Mathf.Exp(-0.5f * (headingRadians - Mathf.PI) * (headingRadians - Mathf.PI) / 0.0076f);
        return Mathf.Clamp01(1 - 4 * Mathf.Abs(headingRadians - Mathf.PI));
    }

    
    public float GetRewardX(float x)
    {
        //return Mathf.Exp(-0.5f * (x * x) / 9);
        return Mathf.Clamp01(1 - Mathf.Abs(0.05f * x));
    }


    public static bool AcceptableZ(float z)
    {
        if (z <= 100 && z >= 0)
            return true;
        else
            return false;
    }


    public float GetRewardBank(float bank)
    {
        //return Mathf.Exp(-0.5f * (bank * bank) / 9);
        return Mathf.Clamp01(1 - Mathf.Abs(0.075f * bank));
    }


    public float GetRewardIAS(float ias)
    {
        //return ias < 25 ? 1 : Mathf.Exp(-0.5f * (ias - 25) * (ias - 25) / 25);
        return ias < 22 ? 1 : Mathf.Clamp01(1 - 0.075f * (ias - 22));
    }


    public float GetRewardVSI(float vsi)
    {
        //return Mathf.Exp(-0.5f * (vsi * vsi) / 4);
        return Mathf.Clamp01(1 + 0.15f * vsi);
    }
}
