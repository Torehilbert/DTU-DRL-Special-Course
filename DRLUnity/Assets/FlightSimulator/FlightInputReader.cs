using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FlightInputReader : MonoBehaviour
{
    public float inputAileron = 0;
    public float inputElevator = 0;
    public float inputBrakes = -1;


    void Update()
    {
        inputAileron = Input.GetAxis("Horizontal") * Input.GetAxis("Horizontal") * Mathf.Sign(Input.GetAxis("Horizontal"));
        inputElevator = Input.GetAxis("Vertical");
        inputBrakes = Input.GetAxis("Brake");
        //if (Input.GetKey(KeyCode.B))
        //    inputBrakes = 1;
        //else
        //    inputBrakes = 0;
    }
}
