using UnityEngine;
using System.Collections;

public class BoxMechanics : MonoBehaviour
{
    Rigidbody box;
    public float rotationForce = 0;

    void Awake()
    {
        box = GetComponent<Rigidbody>();
    }


    //public void FixedUpdate()
    //{
    //    ManualFixedUpdate();
    //}


    public void ManualFixedUpdate()
    {
        box.AddTorque(5 * rotationForce * box.mass * Vector3.forward);
        box.AddForce(10 * box.mass * box.transform.up);
    }


}
