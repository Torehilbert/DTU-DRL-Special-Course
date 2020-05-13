using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AircraftWingSystem
{
    public List<Transform> transforms;
    public List<Wing> wings;
    public Rigidbody rigidbody;
    Transform transform;

    public AircraftWingSystem(Rigidbody rigidbody)
    {
        this.rigidbody = rigidbody;
        transform = rigidbody.transform;
        transforms = new List<Transform>();
        wings = new List<Wing>();
    }

    public void ApplyForces()
    {
        for (int i=0; i<wings.Count; i++)
        {
            Force force = wings[i].GetForce(rigidbody);
            //rigidbody.AddForceAtPosition(force.force, transform.TransformPoint(force.position));
            rigidbody.AddForceAtPosition(force.force, force.position);
        }
    }
}


