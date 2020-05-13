using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class FlightLandingReportUI : MonoBehaviour
{
    public TextMeshProUGUI textField;

    void Start()
    {
        FlightGameManager.instance.onEpisodeEnded += CallbackOnNewReport;
    }


    void CallbackOnNewReport(FlightLandingReport report)
    {
        string msg = "Report\n";
        if (report != null)
        {
            msg += "---------------\n";
            msg += "HDG   " + (100 * report.rewardHeading).ToString("0") + "%\n";
            msg += "X     " + (100 * report.rewardX).ToString("0") + "%\n";
            msg += "BANK  " + (100 * report.rewardBank).ToString("0") + "%\n";
            msg += "IAS   " + (100 * report.rewardIAS).ToString("0") + "%\n";
            msg += "VSI   " + (100 * report.rewardVSI).ToString("0") + "%\n";
            msg += "---------------\n";
            msg += "TOTAL = " + report.rating.ToString(".00");
        }
        else
        {
            msg += "Unaccetable";
        }
        textField.text = msg;
    }
}
