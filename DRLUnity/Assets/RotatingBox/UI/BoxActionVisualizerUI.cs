using UnityEngine;
using System.Collections;

public class BoxActionVisualizerUI : MonoBehaviour
{
    public RectTransform actionValuePointer;


    void Start()
    {
        BoxGameManager.instance.onActionValueChange += CallbackOnActionValueChange;
    }


    void CallbackOnActionValueChange(float value)
    {
        actionValuePointer.anchoredPosition = -100 * value * Vector3.right;
    }
}
