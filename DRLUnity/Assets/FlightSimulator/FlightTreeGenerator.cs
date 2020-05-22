using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FlightTreeGenerator : MonoBehaviour
{
    public GameObject treePrefab;

    float runwayWidth = 20;
    float runwayWidthMargin = 30;
    float runwayLength = 200;
    float runwayLengthMargin = 300;
    Vector3 runwayStart = new Vector3(0, 0, 30);

    float worldRadius = 600;

    int treeCount = 2500;

    void Start()
    {
        Vector2 widthDeadZone = new Vector2(runwayStart.x - runwayWidth/2 - runwayWidthMargin, runwayStart.x + runwayWidth / 2 + runwayWidthMargin);
        Vector2 lengthDeadZone = new Vector2(runwayStart.z - runwayLength - runwayLengthMargin, runwayStart.z + runwayLengthMargin);
        for (int i=0; i<treeCount; i++)
        {
            float x = 0;
            float z = -100;
            while (!(x < widthDeadZone[0] || x > widthDeadZone[1] || z < lengthDeadZone[0] || z > lengthDeadZone[1]))
            {
                x = Random.Range(-1000, 1000);
                z = Random.Range(-1000, 1000);
            }                

            GameObject obj = Instantiate(treePrefab, new Vector3(x, 0, z), Quaternion.Euler(0, Random.Range(0, 360), 0));
            obj.transform.localScale = Vector3.one * Random.Range(0.65f, 1.45f);
        }
    }

}
