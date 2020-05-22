using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FlightExitButtonUI : MonoBehaviour
{
    public void CallbackExitButtonPressed()
    {
        FlightGameManager.instance.exitOrdered = true;
    }
}
