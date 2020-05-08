using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System;

namespace ArgumentParsing
{
    public class Argument
    {
        public string key;
        public bool required = false;
        public string defaultValue;

        public bool isSupplied = false;
        public string valueString;
        public float valueFloat;
        public int valueInt;

        public Argument(string key, bool required, string defaultValue)
        {
            this.key = key;
            this.required = required;
            this.defaultValue = defaultValue;
        }


        public void SetValue(string value)
        {
            valueString = value;
            int.TryParse(value, out valueInt);
            float.TryParse(value, out valueFloat);

            isSupplied = true;
        }

        public void ConvertDefaultValue()
        {
            SetValue(defaultValue);
            isSupplied = false;
        }

    }

    public class ArgumentParser
    {
        public Dictionary<string, Argument> arguments = new Dictionary<string, Argument>();

        public void AddArgument(string key)
        {
            AddArgument(key, true, "");
        }

        public void AddArgument(string key, bool required, string defaultValue)
        {
            arguments.Add(key, new Argument(key, required, defaultValue));
        }


        public void ParseArguments()
        {
            // Apply values to supplied arguments
            string[] args = System.Environment.GetCommandLineArgs();
            List<string> suppliedArguments = new List<string>();
            for (int i=0; i<args.Length; i++)
            {
                string[] splits = args[i].Split(new string[] { "=" }, System.StringSplitOptions.None);
                if(arguments.ContainsKey(splits[0]))
                {
                    arguments[splits[0]].SetValue(splits[1]);
                    suppliedArguments.Add(splits[0]);
                }
            }

            // Apply default values to non-supplied arguments
            foreach(string key in arguments.Keys)
            {
                if(!suppliedArguments.Contains(key))
                {
                    if (arguments[key].required)
                        throw new System.Exception("Argument <" + key + "> needs to be supplied!");
                    else
                        arguments[key].ConvertDefaultValue();
                }
            }
            
        }

        public string GetStringArgument(string key)
        {
            return arguments[key].valueString;
        }

        public int GetIntArgument(string key)
        {
            return arguments[key].valueInt;
        }

        public float GetFloatArgument(string key)
        {
            return arguments[key].valueFloat;
        }
    }
}