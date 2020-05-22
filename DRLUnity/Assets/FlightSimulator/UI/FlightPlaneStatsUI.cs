using UnityEngine;
using System.Collections;
using TMPro;

public class FlightPlaneStatsUI : MonoBehaviour
{
    public Rigidbody R;
    public TextMeshProUGUI textIAS;
    public TextMeshProUGUI textALT;
    public TextMeshProUGUI textVSI;

    void Start()
    {
        FlightGameManager.instance.onStateChange += CallbackOnStateChange;
    }


    void CallbackOnStateChange(float[] state)
    {
        textIAS.text = "IAS   " + (R.velocity.magnitude).ToString(".0") +  " m/s";
        textALT.text = "ALT   " + (R.position.y).ToString(".0") + " m";
        textVSI.text = "VSI   " + (R.velocity.y).ToString("0") + " m/s";
    }
}
