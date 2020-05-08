using UnityEngine;
using System.Collections;

public class InitialVelocity : MonoBehaviour
{
    Rigidbody R;
    void Start()
    {
        R = GetComponent<Rigidbody>();
        R.velocity = R.transform.forward * 67;
        Destroy(this);
    }
}
