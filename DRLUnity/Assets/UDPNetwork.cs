using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System;

public class UDPNetwork
{
    public byte[] sendBuffer;
    public int portSend { get; private set; } = -1;
    public int portReceive { get; private set; } = -1;

    UdpClient sender = null;
    UdpClient receiver = null;
    IPEndPoint endPoint = null;

    public UDPNetwork(int portSend, int portReceive)
    {
        this.portSend = portSend;
        this.portReceive = portReceive;

        sender = new UdpClient(portSend);
        sender.Connect("127.0.0.1", portSend);
        receiver = new UdpClient(portReceive);
        endPoint = new IPEndPoint(IPAddress.Any, portReceive);
    }

    public void AllocateSendBuffer(int nBytes)
    {
        sendBuffer = new byte[nBytes];
    }

    public void Send()
    {
        Send(sendBuffer);
    }

    public void Send(string text)
    {
        Send(System.Text.Encoding.ASCII.GetBytes(text));
    }

    public void Send(byte[] bytes)
    {
        sender.Send(bytes, bytes.Length);
    }

    public byte[] Receive()
    {
        return receiver.Receive(ref endPoint);
    }

    public void ReceiveFloatsAndString(int floats, float[] outFloats, ref string outString)
    {
        byte[] bytes = Receive();

        // set floats
        for (int i = 0; i < floats; i++)
            outFloats[i] = System.BitConverter.ToSingle(bytes, 4 * i);

        // set optional trailing string
        int stringLength = bytes.Length - 4 * floats;
        if (stringLength > 0)
            outString = System.Text.Encoding.UTF8.GetString(bytes, 4*floats, stringLength);
        else
            outString = "";
    }

    public void ReceiveFloatsInBuffer(int floatCount, float[] outArray)
    {
        byte[] bytes = Receive();
        for (int i = 0; i < floatCount; i++)
            outArray[i] = System.BitConverter.ToSingle(bytes, 4 * i);
    }

    public void Shutdown()
    {
        receiver.Close();
        sender.Close();
    }

    public void SetFloatInBuffer(float value, int position)
    {
        byte[] bytes = System.BitConverter.GetBytes(value);
        for(int i=0; i< bytes.Length; i++)
            sendBuffer[i + 4*position] = bytes[i];
    }


    public void SetArrayFloatsInBuffer(float[] array, int position_start)
    {
        for (int i = 0; i < array.Length; i++)
            SetFloatInBuffer(array[i], position_start + i);
    }
}
