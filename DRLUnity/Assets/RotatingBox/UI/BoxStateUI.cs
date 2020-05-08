using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using TMPro;


public class BoxStateUI : MonoBehaviour
{
    TextMeshProUGUI textObj;
    List<string> stateLabels = new List<string>();

    private void Awake()
    {
        textObj = GetComponent<TextMeshProUGUI>();
    }

    void Start()
    {
        stateLabels.Add("Velocity");
        stateLabels.Add("Rotation");
        stateLabels.Add("Angular Velocity");
        stateLabels.Add("Velocity (target)");
        stateLabels.Add("Rotation (target)");
        stateLabels.Add("Velocity Mode");
        stateLabels.Add("Rotation Mode");
        BoxGameManager.instance.onStateChange += UpdateStateText;
    }


    void UpdateStateText(float[] state)
    {
        string msg = "";
        for(int i=0; i<state.Length; i++)
        {
            msg += stateLabels[i] + "   " + state[i].ToString("0.00") + "\n";
        }

        textObj.text = msg;
    }
}
