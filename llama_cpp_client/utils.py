import requests
import json

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

