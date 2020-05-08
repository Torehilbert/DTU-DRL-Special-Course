using UnityEngine;
using System.Collections;

public class BoxInputReader : MonoBehaviour
{
    //[System.NonSerialized]
    public float rotationForce = 0;

    void Update()
    {
        if (Input.GetKey(KeyCode.LeftArrow))
            rotationForce = 1;
        else if (Input.GetKey(KeyCode.RightArrow))
            rotationForce = -1;
        else
            rotationForce = 0;
    }
}
