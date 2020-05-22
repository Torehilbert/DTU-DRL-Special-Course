using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;


public class FlightInputVisualizerUI : MonoBehaviour
{
    public AircraftScript AS;
    public RectTransform controlKnob;
    public RectTransform controlState;
    public RectTransform brakeKnob;
    public RectTransform brakeState;
    public RectTransform parent;

    float yMultiplier;
    float xMultiplier;


    void Start()
    {
        FlightGameManager.instance.onActionValueChange += CallbackOnActionChange;
    }


    void CallbackOnActionChange(float[] actions)
    {
        controlKnob.anchoredPosition = 100 * new Vector3(actions[1], actions[0], 0);
        controlState.anchoredPosition = 100 * new Vector3(AS.rotatorAileronLeft_outer.smoothAngle / AS.rotatorAileronLeft_outer.magnitude, AS.rotatorElevator.smoothAngle / AS.rotatorElevator.magnitude, 0);

        brakeKnob.anchoredPosition = 100 * new Vector3(0, actions[2], 0);
        brakeState.anchoredPosition = 100 * new Vector3(0, AS.rotatorBrakeBottom.smoothAngle / AS.rotatorBrakeBottom.magnitude, 0);
    }
}
