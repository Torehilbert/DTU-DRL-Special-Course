using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;


public class BoxVelocityTargetUI : MonoBehaviour
{
    public Slider slider;
    public TextMeshProUGUI text;

    private void Start()
    {
        slider.onValueChanged.AddListener(CallbackSliderChange);
        BoxGameManager.instance.onTargetChange += CallbackOnTargetChange;
    }


    void CallbackSliderChange(float value)
    {
        BoxGameManager.instance.ChangeVelocityTarget(value);
    }

    void CallbackOnTargetChange(float velocityTarget, float rotationTarget, int velocityModeOn, int rotationModeOn)
    {
        if(velocityModeOn == 1)
            text.text = velocityTarget.ToString("0.00");
    }
}
