using UnityEngine;
using System.Collections;

public class HumanControl : MonoBehaviour
{
    public AircraftScript AS;
    float[] input = new float[4];

    void Start()
    {

    }

    void Update()
    {
        input[0] = Input.GetAxis("Horizontal");
        input[1] = Input.GetAxis("Vertical");
        input[2] = Input.GetAxis("Rudder");
        input[3] = Input.GetAxis("Engine");
        AS.SetControlInput(input);
    }
}
