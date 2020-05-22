using UnityEngine;
using System.Collections;

public class FlightCameraFollow : MonoBehaviour
{
    public enum CameraMode {FPV=0, Orbit=2, Static=3}
    CameraMode cameraMode = CameraMode.Orbit;
    public Transform airplane;
    float distance = 20;
    float heightOffset = 1;
    float velocityLimit = 5;
    Rigidbody rigidbody;

    Vector3 targetDeltaPosition;
    Vector3 deltaPosition;

    bool toggle = false;

    void Start()
    {
        rigidbody = airplane.GetComponent<Rigidbody>();
    }


    float yawRotation = 0;
    float pitchRotation = 0;

    void LateUpdate()
    {
        // Change camera mode
        if(Input.GetAxis("Camera Mode") > 0.1f)
        {
            if(!toggle)
            {
                int newModeInt = (int)cameraMode + 1;
                if (newModeInt > 2)
                    newModeInt = 0;
                cameraMode = (CameraMode)newModeInt;
            }
            toggle = true;
        }
        else
        {
            toggle = false;
        }

        // Perform camera mode
        switch(cameraMode)
        {
            case CameraMode.FPV:
                transform.position = rigidbody.position + rigidbody.transform.up * 0.65f;
                transform.rotation = rigidbody.rotation;
                break;
            case CameraMode.Orbit:

                yawRotation += Mathf.Clamp(60 * Input.GetAxis("Look X") * Time.deltaTime, -180, 180);
                pitchRotation += Mathf.Clamp(60 * Input.GetAxis("Look Y") * Time.deltaTime, -89, 89);

                if (Mathf.Abs(Input.GetAxis("Look X")) < 0.05f && Mathf.Abs(Input.GetAxis("Look Y")) < 0.05f)
                {
                    yawRotation = Mathf.Lerp(yawRotation, 0, Time.deltaTime);
                    pitchRotation = Mathf.Lerp(pitchRotation, 0, Time.deltaTime);
                }

                Vector3 forwardAxis = -rigidbody.velocity.normalized;
                Vector3 rightAxis = Vector3.Cross(forwardAxis, Vector3.up);

                Vector3 cameraOffset = Quaternion.AngleAxis(pitchRotation, rightAxis) * forwardAxis;
                cameraOffset = Quaternion.AngleAxis(yawRotation, Vector3.up) * cameraOffset;

                deltaPosition = Vector3.Lerp(deltaPosition, distance * cameraOffset, Time.deltaTime);
                transform.position = rigidbody.position + deltaPosition;
                transform.LookAt(airplane);
                break;
            case CameraMode.Static:
                transform.LookAt(airplane);
                break;
            default:
                break;
        }
    }
}
