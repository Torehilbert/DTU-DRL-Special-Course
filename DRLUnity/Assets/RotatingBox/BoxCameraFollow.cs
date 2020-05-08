using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BoxCameraFollow : MonoBehaviour
{
    public Transform target;
    float z;

    void Start()
    {
        z = transform.position.z;
    }


    void LateUpdate()
    {
        transform.position = new Vector3(target.position.x, 0, z);
    }
}
