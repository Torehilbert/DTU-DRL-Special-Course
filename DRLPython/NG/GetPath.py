import os
import datetime


def get_environment_executable_path(env_name):
    os_name = "WIN" if os.name == "nt" else "LINUX"
    extension = ".exe" if os_name == "WIN" else ".x86_64"

    env_folder = _get_environment_folder(env_name)
    env_filename = env_name + extension
    executable_path = os.path.join(env_folder, os_name, env_filename)
    return executable_path


def create_result_folder(env_name):
    results_folder_path = _get_results_folder()
    folder_name = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + " " + env_name
    folder_path = os.path.join(results_folder_path, folder_name)
    os.makedirs(folder_path, exist_ok=False)
    return folder_path


def _get_root_folder():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


def _get_environment_folder(env_name):
    root = _get_root_folder()
    return os.path.join(root, "UnityEnvironments", env_name)


def _get_results_folder():
    root = _get_root_folder()
    return os.path.join(root, "Results")


def log_rewards(filename, folder, step_arr, reward_arr):
    try:
        filepath = os.path.join(folder, filename)

        if not os.path.isdir(folder):
            print("ERROR (log_rewards): Specified folder does not exist!")
            return
        if len(step_arr) != len(reward_arr):
            print("ERROR (log_rewards): Given arrays are not of equal length!")
            return

        with open(filepath, 'w') as f:
            for i in range(len(reward_arr)):
                s = step_arr[i]
                r = reward_arr[i]
                f.write(str(s) + "," + str(r) + "\n")
    except Exception as e:
        print("ERROR (log_rewards): " + e)


if __name__ == "__main__":
    print("Root path:", _get_root_folder())
    print("Env folder path:", _get_environment_folder("Box"))
    print("Env exe path:", get_environment_executable_path("Box"))
    print("")
    print("Result folder:", _get_results_folder())
    print("New:", create_result_folder("Box"))
