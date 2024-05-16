import requests
import json


def start_instance(instance_name):
    instance_id = get_instance(instance_name)['id']

    url = f"https://api.genesiscloud.com/compute/v1/instances/{instance_id}/actions"
    payload = {
        "action": "start"
    }
    headers = {
        'Authorization': 'Bearer GCCA4BEfQvIHNODy1vJrp8FMx2RYbT7Bwqwa'
    }
    response = requests.post(url, headers=headers, json=payload)
    return response


def get_actions(instance_name):
    instance = get_instance(instance_name)

    url = f"https://api.genesiscloud.com/compute/v1/instances/{instance['id']}/actions"
    payload = {
    }
    headers = {

        'Authorization': 'Bearer GCCA4BEfQvIHNODy1vJrp8FMx2RYbT7Bwqwa'
    }
    print(url)
    response = requests.request("GET", url, headers=headers, data=payload)
    return response


def get_instances():
    url = "https://api.genesiscloud.com/compute/v1/instances"
    payload = {}
    headers = {
        'Authorization': 'Bearer GCCA4BEfQvIHNODy1vJrp8FMx2RYbT7Bwqwa'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)['instances']


def get_instance(name):
    instances = get_instances()
    return next((x for x in instances if x['name'] == name), None)


def get_available_models(llm_api_ip):
    import http.client

    conn = http.client.HTTPConnection(llm_api_ip, 9000)
    payload = ''
    headers = {
        'accept': 'application/json'
    }
    conn.request("GET", "/models", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")


def start_server_model(llm_api_ip, model_name, n_ctx, port):
    import http.client

    conn = http.client.HTTPConnection(llm_api_ip, 9000)
    payload = ''
    headers = {
        'accept': 'application/json'
    }
    conn.request(f"POST", f"/start-server/?model_name={model_name}&n_ctx={n_ctx}&port={port}", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")


def stop_model(llm_api_ip, pid):
    import http.client

    conn = http.client.HTTPConnection(llm_api_ip, 9000)
    payload = ''
    headers = {
        'accept': 'application/json'
    }
    conn.request(f"GET", f"/stop_model/?pid={pid}", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")


def running_servers(llm_api_ip):
    import http.client

    conn = http.client.HTTPConnection(llm_api_ip, 9000)
    payload = ''
    headers = {
        'accept': 'application/json'
    }
    conn.request("GET", "/running-servers", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")


def tokenize(llm_api_ip, text):
    payload = json.dumps({
        "content": text
    })
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", "http://" + llm_api_ip + '/tokenize', headers=headers, data=payload,
                                timeout=300)

    return response.text


def embed(llm_api_ip, text):
    payload = json.dumps({
        "content": text
    })
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", "http://" + llm_api_ip + '/embeddings', headers=headers, data=payload,
                                timeout=300)

    return response


def call_model(server_ip, prompt, openai_api=False,
               n_predict=2048,
               temperature=0,
               stop=None,
               repeat_last_n=256,
               repeat_penalty=1.18,
               penalize_nl=False,
               top_k=40,
               top_p=0.95,
               min_p=0.05,
               tfs_z=1,
               typical_p=1,
               presence_penalty=0,
               frequency_penalty=0,
               mirostat=2,
               mirostat_tau=5,
               mirostat_eta=0.1,
               grammar="",
               n_probs=0,
               min_keep=0,
               cache_prompt=True,
               ):
    if stop is None:
        stop = []
    url = "http://" + server_ip + ('/v1/completions' if openai_api else '/completion')

    payload = json.dumps({
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": temperature,
        "stop": stop,
        "repeat_last_n": repeat_last_n,
        "repeat_penalty": repeat_penalty,
        "penalize_nl": penalize_nl,
        "top_k": top_k,
        "top_p": top_p,
        "min_p": min_p,
        "tfs_z": tfs_z,
        "typical_p": typical_p,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "mirostat": mirostat,
        "mirostat_tau": mirostat_tau,
        "mirostat_eta": mirostat_eta,
        "grammar": grammar,
        "n_probs": n_probs,
        "min_keep": min_keep,
        "cache_prompt": cache_prompt,
    })
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=600)

    return json.loads(response.text)['content']

