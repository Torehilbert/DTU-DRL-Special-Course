using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FlightInputReader : MonoBehaviour
{
    public float inputAileron = 0;
    public float inputElevator = 0;
    public float inputBrakes = -1;

    public bool inputReset = false;
    bool inputResetDown = false;


    void Update()
    {
        inputAileron = Input.GetAxis("Horizontal") * Input.GetAxis("Horizontal") * Mathf.Sign(Input.GetAxis("Horizontal"));
        inputElevator = Input.GetAxis("Vertical");
        inputBrakes = Input.GetAxis("Brake");

        if (Input.GetAxis("Reset") > 0.5f)
        {
            if(!inputResetDown)
            {
                inputReset = true;
            }
            else
            {
                inputReset = false;
            }

            inputResetDown = true;

        }
        else
        {
            inputResetDown = false;
            inputReset = false;
        }
    }
}
