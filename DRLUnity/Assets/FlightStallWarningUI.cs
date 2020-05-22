using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FlightStallWarningUI : MonoBehaviour
{
    public AircraftScript AS;
    public RectTransform stallWarning;
    Wing[] wings = new Wing[6];

    int stallWarningAngle = 13;

    void Start()
    {
        wings[0] = AS.wingSystem.wings[0];
        wings[1] = AS.wingSystem.wings[1];
        wings[2] = AS.wingSystem.wings[2];
        wings[3] = AS.wingSystem.wings[3];
        wings[4] = AS.wingSystem.wings[4];
        wings[5] = AS.wingSystem.wings[5];
    }


    void Update()
    {
        bool stall = false;
        foreach(Wing w in wings)
        {
            if (w.AngleOfAttack > stallWarningAngle)
            {
                stall = true;
                break;
            }
        }

        if(stall)
        {
            stallWarning.localScale = Mathf.RoundToInt(Time.time*10) % 2 == 0 ? Vector3.one : Vector3.zero;
        }
        else
        {
            stallWarning.localScale = Vector3.zero;
        }
    }
}
