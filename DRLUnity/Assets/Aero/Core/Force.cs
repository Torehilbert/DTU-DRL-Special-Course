using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public struct Force
{
    public Vector3 position;
    public Vector3 force;

    public Force(Vector3 position, Vector3 force)
    {
        this.position = position;
        this.force = force;
    }
}
