using UnityEngine;
using System.Collections;

public class BoxResetButtonUI : MonoBehaviour
{
    public void CallbackResetButtonPressed()
    {
        BoxGameManager.instance.resetButtonPressed = true;
    }
}
