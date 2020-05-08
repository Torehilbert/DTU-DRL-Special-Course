using UnityEngine;
using System.Collections;

public class BoxExitButtonUI : MonoBehaviour
{
    public void CallbackExitButtonPressed()
    {
        BoxGameManager.instance.exitButtonPressed = true;
    }
}
