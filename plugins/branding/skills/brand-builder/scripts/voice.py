#!/usr/bin/env python3
"""Pronunciation clips and the hear-it-then-spell-it test, with the OpenAI audio API.

Needs OPENAI_API_KEY in the environment. Each clip costs a fraction of a cent; the
hearing test makes 12 speech clips and 24 transcriptions per name.

Usage:
  voice.py say  --name trepil --say "TRIP-ul, like triple" [--display Trepil] --out audio/
      writes audio/trepil.mp3 (meant to sound) and audio/trepil__read.mp3 (first read)
  voice.py hear --name trepil --say "exactly like the English word triple" [--display Trepil]
      [--sentence "Can you share your {name} notes from the call?"] [--out hear/]
      speaks the name in six voices, alone and in the sentence, transcribes each clip with
      two models, and prints exact spellings out of 24 plus the most common mishearings.

This is a machine proxy for people hearing the name once. Report it as that.
"""
import argparse, collections, json, os, re, sys, urllib.request, uuid
from concurrent.futures import ThreadPoolExecutor

API = "https://api.openai.com/v1/audio"
VOICES = ["coral", "alloy", "sage", "ash", "verse", "onyx"]


def key():
    k = os.environ.get("OPENAI_API_KEY")
    if not k: sys.exit("OPENAI_API_KEY is not set. Skip the recordings, or ask the user to set a key.")
    return k


def tts(text, instructions, out, voice="coral", model="gpt-4o-mini-tts"):
    body = {"model": model, "voice": voice, "input": text, "response_format": "mp3", "instructions": instructions}
    req = urllib.request.Request(f"{API}/speech", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + key(), "Content-Type": "application/json"})
    data = urllib.request.urlopen(req, timeout=60).read()
    open(out, "wb").write(data)
    return len(data)


def stt(path, model):
    b = "----" + uuid.uuid4().hex
    parts = [f'--{b}\r\nContent-Disposition: form-data; name="model"\r\n\r\n{model}\r\n'.encode(),
             f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode()
             + open(path, "rb").read() + b"\r\n", f"--{b}--\r\n".encode()]
    req = urllib.request.Request(f"{API}/transcriptions", data=b"".join(parts),
                                 headers={"Authorization": "Bearer " + key(), "Content-Type": "multipart/form-data; boundary=" + b})
    return json.loads(urllib.request.urlopen(req, timeout=90).read())["text"]


CALM = ("Calm, relaxed, everyday conversational voice, the way you would mention a name in normal "
        "conversation. Normal pace, no emphasis, no announcing. One smooth word, no extra words.")


def cmd_say(a):
    os.makedirs(a.out, exist_ok=True)
    disp = a.display or a.name.capitalize()
    n1 = tts(disp, f"Say this one name once. It sounds like {a.say}. {CALM}", os.path.join(a.out, f"{a.name}.mp3"))
    n2 = tts(disp, f"Read this one word once, the way a typical English speaker would say it the first time they see it written. {CALM}",
             os.path.join(a.out, f"{a.name}__read.mp3"))
    print(f"wrote {a.out}/{a.name}.mp3 ({n1} bytes) and {a.name}__read.mp3 ({n2} bytes)")


def cmd_hear(a):
    os.makedirs(a.out, exist_ok=True)
    disp = a.display or a.name.capitalize()
    lines = {"word": disp + ".", "sentence": a.sentence.replace("{name}", disp)}
    ins = f"Say it in a calm, everyday conversational voice. The product name is pronounced {a.say}."
    jobs = [(v, k, t) for v in VOICES for k, t in lines.items()]

    def run(j):
        v, k, t = j
        p = os.path.join(a.out, f"{a.name}_{v}_{k}.mp3")
        if not os.path.exists(p): tts(t, ins, p, voice=v)
        return [{"voice": v, "kind": k, "model": m, "heard": stt(p, m)} for m in ("whisper-1", "gpt-4o-transcribe")]

    with ThreadPoolExecutor(6) as ex:
        res = [x for r in ex.map(run, jobs) for x in r]
    json.dump(res, open(os.path.join(a.out, f"{a.name}_results.json"), "w"), indent=1)
    words = []
    for x in res:
        h = x["heard"]
        m = re.search(r"your\s+(.+?)\s+notes", h, re.I) if x["kind"] == "sentence" else None
        words.append((m.group(1) if m else h).strip(" .!?,").lower())
    exact = sum(1 for w in words if re.sub(r"[\s-]", "", w) == a.name.lower())
    print(f"{a.name}: exact {exact} / {len(words)}")
    for w, c in collections.Counter(words).most_common(8): print(f"  {c:2}  {w}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("say"); s.add_argument("--name", required=True); s.add_argument("--say", required=True)
    s.add_argument("--display"); s.add_argument("--out", default="audio")
    h = sp.add_parser("hear"); h.add_argument("--name", required=True); h.add_argument("--say", required=True)
    h.add_argument("--display"); h.add_argument("--sentence", default="Can you share your {name} notes from the call?")
    h.add_argument("--out", default="hear")
    a = ap.parse_args()
    (cmd_say if a.cmd == "say" else cmd_hear)(a)


if __name__ == "__main__":
    main()
