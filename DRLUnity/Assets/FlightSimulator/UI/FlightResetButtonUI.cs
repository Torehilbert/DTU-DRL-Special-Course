using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FlightResetButtonUI : MonoBehaviour
{
    public void CallbackResetButtonPressed()
    {
        FlightGameManager.instance.resetButtonPressed = true;
    }
}
