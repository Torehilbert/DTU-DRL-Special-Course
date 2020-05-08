using UnityEngine;
using System.Collections;
using System;

namespace arglib
{
    public class Parse
    {
        public static T FindArgument<T>(string[] args, string label)
        {
            for (int i = 0; i < args.Length; i++)
            {
                if (args[i] == label)
                    return (T)Convert.ChangeType(args[i + 1], typeof(T));
            }
            throw new Exception("The argument label was not found!");
        }

        public static bool TryFindArgument<T>(string[] args, string label, ref T result)
        {
            for (int i = 0; i < args.Length; i++)
            {
                if (args[i] == label)
                {
                    result = (T)Convert.ChangeType(args[i + 1], typeof(T));
                    return true;
                }
            }
            return false;
        }
    }
}

