import requests

try:
    v = requests.get("http://127.0.0.1:" + str(8200) + "/camera_config/config")
    if v.status_code != 500:
        print("YES" + str(v))
    else:
        print("NO" + str(v))
except Exception as e:
    print("ConnectionRefusedError" + str(type(e)))
