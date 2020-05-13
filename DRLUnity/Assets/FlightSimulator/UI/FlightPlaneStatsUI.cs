using UnityEngine;
using System.Collections;
using TMPro;

public class FlightPlaneStatsUI : MonoBehaviour
{
    public TextMeshProUGUI textIAS;
    public TextMeshProUGUI textALT;
    public TextMeshProUGUI textHDG;
    public TextMeshProUGUI textVSI;

    void Start()
    {
        FlightGameManager.instance.onStateChange += CallbackOnStateChange;
    }


    void CallbackOnStateChange(float[] state)
    {
        textIAS.text = "IAS   " + state[4].ToString(".0") +  " m/s";
        textALT.text = "ALT   " + state[2].ToString(".0") + " m";

        float heading = 0;
        if (state[10] > 0)
            heading = Mathf.Asin(state[11]);
        else if (state[11] > 0)
            heading = Mathf.Asin(state[11]) + 2 * (Mathf.PI / 2 - state[11]);
        else
            heading = Mathf.Asin(state[11]) + 2 * (-Mathf.PI / 2 - state[11]);
        textHDG.text = "HDG   " + (heading * Mathf.Rad2Deg).ToString("0") + " deg";
        textVSI.text = "VSI   " + state[6].ToString("0") + " m/s";
    }
}
