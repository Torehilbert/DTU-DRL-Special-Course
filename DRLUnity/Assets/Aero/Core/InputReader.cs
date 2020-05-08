using UnityEngine;
using System.Collections;

public class InputReader
{
    public float[] input = new float[4];

    public void ReadInputs()
    {
        input[0] = Input.GetAxis("Horizontal");
        input[1] = Input.GetAxis("Vertical");
        input[2] = Input.GetAxis("Rudder");
        input[3] = Input.GetAxis("Engine");
    }
}
