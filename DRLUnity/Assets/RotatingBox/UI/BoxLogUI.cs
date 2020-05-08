using UnityEngine;
using System.Collections;
using TMPro;

public class BoxLogUI : MonoBehaviour
{
    public static BoxLogUI instance;
    public TextMeshProUGUI logObj;


    private void Awake()
    {
        instance = this;
    }


    public void Log(string message)
    {
        logObj.text = logObj.text + "\n" + message;
    }
}
