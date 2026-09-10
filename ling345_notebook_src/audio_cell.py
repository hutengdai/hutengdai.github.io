# =====================================================================
#  LING 345 -- the audio helper.  Run this cell once.  It is plumbing:
#  it turns sound into a list of numbers between -1.0 and 1.0, which is
#  the only thing your recognizer knows how to read.
#
#      samples = record(2.0)          record 2 seconds from your microphone
#      samples = demo_audio("no")     a stand-in sound, no microphone needed
#      samples = upload_audio()       use a sound file instead
#      samples = trim_silence(samples)  throw away the quiet ends
#
#  You are welcome to read it, but you do not need to.
# =====================================================================
import array, base64, json, math, struct, subprocess, sys

SAMPLE_RATE = 16000


# ------------------------------------------------------------------ setup
def _in_colab():
    try:
        import google.colab  # noqa: F401
        return True
    except Exception:
        return False


class MicrophoneError(RuntimeError):
    """Raised with a plain-English explanation when recording is impossible."""


_HELP = """
--------------------------------------------------------------------
We could not record from your microphone.  Two things you can try:

  1. UPLOAD A SOUND FILE INSTEAD
       samples = upload_audio()     # then pick a file from your computer
     (Record a voice memo on your phone, email it to yourself, and
      choose that file.  Any format works in Colab; use .wav locally.)

  2. USE THE STAND-IN SOUND so you can keep going with the lesson
       samples = demo_audio("no")   # or demo_audio("go")

If you want to fix the microphone: make sure you clicked "Allow" on the
browser's permission popup, that no other app (Zoom, Teams) is holding
the mic, and that the notebook tab is the one you are looking at.
--------------------------------------------------------------------
"""


# ------------------------------------------------------- number crunching
def _b64_pcm16_to_floats(b64_string):
    """base64 of little-endian 16-bit PCM -> list of floats in -1..1"""
    raw = base64.b64decode(b64_string)
    raw = raw[: len(raw) - (len(raw) % 2)]
    a = array.array("h")
    a.frombytes(raw)
    if sys.byteorder == "big":
        a.byteswap()
    return [v / 32768.0 for v in a]


def _resample(samples, src_rate, dst_rate):
    """Convert a list of floats from src_rate to dst_rate samples/second."""
    src_rate, dst_rate = int(src_rate), int(dst_rate)
    if not samples or src_rate == dst_rate:
        return list(samples)
    n_out = max(1, int(round(len(samples) * dst_rate / float(src_rate))))
    try:                                    # best: scipy (Colab + Anaconda have it)
        from fractions import Fraction
        import numpy as np
        from scipy.signal import resample_poly
        f = Fraction(dst_rate, src_rate).limit_denominator(1000)
        y = resample_poly(np.asarray(samples, dtype=np.float64), f.numerator, f.denominator)
        return [float(v) for v in y]
    except Exception:
        pass
    try:                                    # ok: numpy only
        import numpy as np
        x = np.asarray(samples, dtype=np.float64)
        if src_rate > dst_rate:
            w = int(round(src_rate / float(dst_rate)))
            if w > 1:
                x = np.convolve(x, np.ones(w) / w, mode="same")
        return [float(v) for v in np.interp(np.linspace(0, len(x) - 1, n_out),
                                            np.arange(len(x)), x)]
    except Exception:
        pass
    x = list(samples)                       # last resort: pure Python
    if src_rate > dst_rate:
        w = int(round(src_rate / float(dst_rate)))
        if w > 1:
            half, n, sm = w // 2, len(x), []
            for i in range(n):
                lo, hi = max(0, i - half), min(n, i - half + w)
                sm.append(sum(x[lo:hi]) / (hi - lo))
            x = sm
    n, out = len(x), []
    for k in range(n_out):
        p = k * (n - 1) / float(n_out - 1) if n_out > 1 else 0.0
        i = int(p)
        if i >= n - 1:
            out.append(x[-1])
        else:
            out.append(x[i] * (1 - (p - i)) + x[i + 1] * (p - i))
    return out


def _finish(samples, src_rate, sample_rate, seconds=None, normalise=True):
    """Resample, trim/pad to the requested length, and gently normalise."""
    out = _resample(samples, src_rate, sample_rate)
    if seconds:
        want = int(round(seconds * sample_rate))
        out = out[:want] + [0.0] * max(0, want - len(out))
    if normalise:
        peak = max((abs(v) for v in out), default=0.0)
        if peak > 1e-6:
            out = [v * (0.95 / peak) for v in out]
    return out


# ------------------------------------------- read a .wav file, stdlib only
def wav_bytes_to_samples(data, sample_rate=SAMPLE_RATE):
    """RIFF/WAVE bytes -> (mono list of floats, sample_rate).  No dependencies.
    Handles 8/16/24/32-bit integer PCM and 32/64-bit float PCM, any channel count."""
    if len(data) < 12 or data[0:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise ValueError("That file is not a .wav file. Please export/convert it to WAV.")
    fmt_tag = chans = rate = bits = frames = None
    pos = 12
    while pos + 8 <= len(data):
        cid = data[pos:pos + 4]
        size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
        body = data[pos + 8:pos + 8 + size]
        if cid == b"fmt " and len(body) >= 16:
            fmt_tag, chans, rate, _br, _ba, bits = struct.unpack("<HHIIHH", body[:16])
            if fmt_tag == 0xFFFE and len(body) >= 40:          # WAVE_FORMAT_EXTENSIBLE
                fmt_tag = struct.unpack("<H", body[24:26])[0]
        elif cid == b"data":
            frames = body
        pos += 8 + size + (size & 1)
    if fmt_tag is None or frames is None:
        raise ValueError("This .wav file is damaged (no 'fmt ' or 'data' chunk).")
    if fmt_tag not in (1, 3):
        raise ValueError("This WAV uses a compressed encoding. Please export plain PCM WAV.")
    chans = max(1, chans or 1)

    if fmt_tag == 3 and bits == 32:
        n = len(frames) // 4
        flat = list(struct.unpack("<%df" % n, frames[:4 * n]))
    elif fmt_tag == 3 and bits == 64:
        n = len(frames) // 8
        flat = list(struct.unpack("<%dd" % n, frames[:8 * n]))
    elif bits == 8:
        flat = [(b - 128) / 128.0 for b in frames]
    elif bits == 16:
        a = array.array("h"); a.frombytes(frames[: len(frames) - (len(frames) % 2)])
        if sys.byteorder == "big": a.byteswap()
        flat = [v / 32768.0 for v in a]
    elif bits == 24:
        flat = []
        for i in range(0, len(frames) - 2, 3):
            v = frames[i] | (frames[i + 1] << 8) | (frames[i + 2] << 16)
            flat.append((v - 0x1000000 if v & 0x800000 else v) / 8388608.0)
    elif bits == 32:
        a = array.array("i"); a.frombytes(frames[: len(frames) - (len(frames) % 4)])
        if sys.byteorder == "big": a.byteswap()
        flat = [v / 2147483648.0 for v in a]
    else:
        raise ValueError("Unsupported WAV bit depth: %s" % bits)

    if chans > 1:
        n = len(flat) // chans
        flat = [sum(flat[i * chans:(i + 1) * chans]) / chans for i in range(n)]
    return _finish(flat, rate, sample_rate, seconds=None), sample_rate


# ------------------------------------------------ browser recorder (Colab)
_BROWSER_JS = r"""
window._ling345 = async function(mode, ms, targetRate) {
  const panel = document.createElement('div');
  panel.style.cssText = 'font:15px/1.5 system-ui,sans-serif;padding:12px 14px;border:2px solid #3367d6;'
                      + 'border-radius:10px;display:inline-block;min-width:280px;background:#f6f9ff;color:#111';
  const line = document.createElement('div'); panel.appendChild(line);
  const slot = document.createElement('div'); slot.style.marginTop = '8px'; panel.appendChild(slot);
  document.body.appendChild(panel);
  const say = t => { line.textContent = t; };
  const sleep = t => new Promise(r => setTimeout(r, t));
  let blob;
  try {
    if (mode === 'file') {
      say('Choose a sound file from your device:');
      const inp = document.createElement('input');
      inp.type = 'file'; inp.accept = 'audio/*,video/*';
      slot.appendChild(inp);
      blob = await new Promise((res, rej) => {
        inp.onchange = () => inp.files && inp.files.length ? res(inp.files[0])
                                                          : rej(new Error('No file was chosen.'));
        setTimeout(() => rej(new Error('Timed out waiting for a file (5 minutes).')), 300000);
      });
      say('Reading ' + blob.name + ' ...');
    } else {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia)
        throw new Error('This browser does not offer microphone access (no getUserMedia).');
      say('Click "Allow" if the browser asks to use your microphone...');
      const stream = await navigator.mediaDevices.getUserMedia({audio: {
        channelCount: 1, echoCancellation: false, noiseSuppression: false, autoGainControl: false}});
      for (const n of ['3', '2', '1']) { say('Get ready...  ' + n); await sleep(650); }
      const rec = new MediaRecorder(stream), chunks = [];
      rec.ondataavailable = e => { if (e.data && e.data.size) chunks.push(e.data); };
      const stopped = new Promise(r => { rec.onstop = r; });
      rec.start();
      say('*** RECORDING -- SPEAK NOW ***');
      await sleep(ms);
      rec.stop();
      stream.getTracks().forEach(t => t.stop());
      await stopped;
      if (!chunks.length) throw new Error('The microphone produced no audio at all.');
      blob = new Blob(chunks, {type: chunks[0].type || 'audio/webm'});
      say('Done. Listen back if you like:');
    }
    const bytes = await blob.arrayBuffer();
    const player = document.createElement('audio');
    player.controls = true; player.src = URL.createObjectURL(blob); slot.appendChild(player);

    // Decode + resample in the browser: no Python audio libraries needed.
    let buf = null, rate = targetRate;
    const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    if (OAC) {
      try {                                    // decodeAudioData resamples to ctx rate
        buf = await new OAC(1, 1, targetRate).decodeAudioData(bytes.slice(0));
        rate = buf.sampleRate;
      } catch (e) { buf = null; }
    }
    if (!buf) {                                // fall back: native rate, Python resamples
      const AC = window.AudioContext || window.webkitAudioContext;
      const ac = new AC();
      buf = await ac.decodeAudioData(bytes.slice(0));
      rate = buf.sampleRate;
      if (ac.close) ac.close();
    }
    const n = buf.length, ch = buf.numberOfChannels, mono = new Float32Array(n);
    for (let c = 0; c < ch; c++) {
      const d = buf.getChannelData(c);
      for (let i = 0; i < n; i++) mono[i] += d[i] / ch;   // down-mix to mono
    }
    const pcm = new Int16Array(n);
    for (let i = 0; i < n; i++) {
      const s = Math.max(-1, Math.min(1, mono[i]));
      pcm[i] = s < 0 ? s * 32768 : s * 32767;
    }
    const u8 = new Uint8Array(pcm.buffer);
    let bin = '';
    for (let i = 0; i < u8.length; i += 8192)
      bin += String.fromCharCode.apply(null, u8.subarray(i, i + 8192));
    say((mode === 'file' ? 'Loaded ' : 'Recorded ') + (n / rate).toFixed(2) + ' seconds of audio.');
    return JSON.stringify({ok: true, sampleRate: rate, pcm: btoa(bin)});
  } catch (err) {
    const name = (err && err.name) || 'Error', msg = (err && err.message) || String(err);
    say('Could not get audio: ' + name + ' -- ' + msg);
    return JSON.stringify({ok: false, name: name, message: msg});
  }
};
"""

_BROWSER_HINTS = {
    "NotAllowedError": "The browser blocked the microphone. Click the camera/mic icon in the "
                       "address bar (or the popup) and choose Allow, then run the cell again.",
    "NotFoundError":   "No microphone was found. Plug one in, or use upload_audio().",
    "NotReadableError":"Another app (Zoom, Teams, Voice Memos) is using the microphone. "
                       "Quit it and run the cell again.",
    "SecurityError":   "The notebook page is not allowed to use the microphone.",
    "AbortError":      "The browser gave up on the microphone. Try running the cell again.",
}


def _browser_capture(mode, seconds, sample_rate):
    from IPython.display import Javascript, display
    from google.colab import output
    display(Javascript(_BROWSER_JS))
    call = '_ling345("%s", %d, %d)' % (mode, int(seconds * 1000), int(sample_rate))
    limit = 330 if mode == "file" else int(seconds) + 120
    try:
        reply = output.eval_js(call, timeout_sec=limit)
    except Exception as e:
        raise MicrophoneError("The browser never answered (%s).\n%s" % (type(e).__name__, _HELP))
    if not reply:
        raise MicrophoneError("The browser sent nothing back. Re-run this cell; if the notebook "
                              "was reloaded, run the setup cell again first.\n" + _HELP)
    info = json.loads(reply)
    if not info.get("ok"):
        hint = _BROWSER_HINTS.get(info.get("name")) or ("The browser reported: %s -- %s"
                                                       % (info.get("name"), info.get("message")))
        raise MicrophoneError("%s\n%s" % (hint, _HELP))
    samples = _b64_pcm16_to_floats(info["pcm"])
    if not samples:
        raise MicrophoneError("The recording came back empty.\n" + _HELP)
    return _finish(samples, info.get("sampleRate", sample_rate), sample_rate,
                   seconds=(seconds if mode == "mic" else None))


# ------------------------------------------- local microphone (sounddevice)
def _local_capture(seconds, sample_rate):
    try:
        import sounddevice as sd
    except ImportError:
        raise MicrophoneError(
            "Recording on your own computer needs one small extra package.\n"
            "Put this in a new cell, run it, then come back here:\n"
            "\n"
            "    %pip install sounddevice\n"
            "\n"
            "(On Linux you may also need:  !apt-get install -y libportaudio2 )\n"
            "Or skip the microphone entirely and use demo_audio(\"no\").\n" + _HELP)
    try:
        rate = int(sample_rate)
        try:
            sd.check_input_settings(samplerate=rate, channels=1, dtype="float32")
        except Exception:                       # device refuses 16 kHz -> use its own rate
            rate = int(sd.query_devices(kind="input")["default_samplerate"])
        print("Get ready...")
        print("*** RECORDING -- SPEAK NOW (%.1f seconds) ***" % seconds)
        buf = sd.rec(int(seconds * rate), samplerate=rate, channels=1, dtype="float32",
                     blocking=True)
        print("Done.")
    except Exception as e:
        raise MicrophoneError("The microphone could not be opened (%s).\n%s" % (e, _HELP))
    flat = [float(v[0]) for v in buf]
    if max((abs(v) for v in flat), default=0.0) < 1e-4:
        raise MicrophoneError(
            "The recording is completely silent.\n"
            "On a Mac this usually means the app running Jupyter has not been given\n"
            "microphone permission: System Settings > Privacy & Security > Microphone.\n"
            "On Windows: Settings > Privacy & security > Microphone.\n"
            "Turn it on, restart Jupyter, and try again." + _HELP)
    return _finish(flat, rate, sample_rate, seconds=seconds)


# ------------------------------------------------------------ upload paths
def upload_audio(sample_rate=SAMPLE_RATE):
    """Use a sound file from your computer or phone instead of the microphone."""
    if _in_colab():
        return _browser_capture("file", 0, sample_rate)
    try:
        import ipywidgets
        from IPython.display import display
    except ImportError:
        raise MicrophoneError("Please put a .wav file next to this notebook and run:\n"
                              "    samples = load_wav('myvoice.wav')")
    box = ipywidgets.FileUpload(accept=".wav", multiple=False, description="Choose .wav")
    display(box)
    print("Click the button above and pick a .wav file,")
    print("then run the next cell.")
    return box


def finish_upload(box, sample_rate=SAMPLE_RATE):
    """Turn the file chosen with upload_audio() into samples (local Jupyter)."""
    value = getattr(box, "value", None)
    if not value:
        raise MicrophoneError("No file has been chosen yet. Click the button above first.")
    if isinstance(value, dict):                      # ipywidgets 7 (dict keyed by filename)
        item = list(value.values())[0]
        data = item["content"]
    else:                                            # ipywidgets 8 (list/tuple of dicts)
        data = value[0]["content"]
    data = bytes(data)
    samples, _ = wav_bytes_to_samples(data, sample_rate)
    return samples


def load_wav(path, sample_rate=SAMPLE_RATE):
    """Read a .wav file from disk into samples."""
    with open(path, "rb") as f:
        return wav_bytes_to_samples(f.read(), sample_rate)[0]


# ------------------------------------------------------ trimming silence
def trim_silence(samples, threshold=0.10):
    """Throw away the quiet run at each end of a recording.

    Silence is mostly microphone noise, and noise crosses zero constantly,
    so leaving it in swamps the eight numbers features() cares about.
    A sample counts as "sound" if it reaches `threshold` of the loudest one.
    """
    if not samples:
        return list(samples)
    peak = max(abs(v) for v in samples)
    if peak < 1e-6:
        return list(samples)
    loud = [i for i, v in enumerate(samples) if abs(v) >= threshold * peak]
    if not loud:
        return list(samples)
    return list(samples[loud[0]:loud[-1] + 1])


# --------------------------------------------------------------- stand-in
def demo_audio(word="no", seconds=1.0, sample_rate=SAMPLE_RATE):
    """A synthetic stand-in so the lesson works with no microphone at all.
    'no' = voiced nasal onset (few zero crossings); 'go' = noisy burst then vowel."""
    import random
    random.seed(1 if word == "go" else 0)   # a fixed seed: the same word every time
    n, out = int(seconds * sample_rate), []
    onset = int(0.18 * n)
    for i in range(n):
        t = i / float(sample_rate)
        env = min(1.0, i / (0.02 * sample_rate)) * min(1.0, (n - i) / (0.05 * sample_rate))
        if word == "go" and i < int(0.03 * n):
            s = random.uniform(-1, 1) * 0.6                      # burst: high ZCR
        elif i < onset and word == "no":
            s = 0.5 * math.sin(2 * math.pi * 250 * t) + 0.2 * math.sin(2 * math.pi * 500 * t)
        else:                                                    # the vowel
            s = (0.6 * math.sin(2 * math.pi * 130 * t)
                 + 0.3 * math.sin(2 * math.pi * 600 * t)
                 + 0.15 * math.sin(2 * math.pi * 1000 * t)
                 + 0.02 * random.uniform(-1, 1))
        out.append(s * env * 0.8)
    return _finish(out, sample_rate, sample_rate, seconds=seconds)


# ------------------------------------------------------------------ record
def record(seconds=2.0, sample_rate=SAMPLE_RATE, source="auto"):
    """Record `seconds` of your voice and return a list of floats (-1.0 .. 1.0).

    seconds     : how long to record
    sample_rate : samples per second in the result (default 16000)
    source      : "auto" (default), "mic", or "upload"
    """
    seconds = float(seconds)
    sample_rate = int(sample_rate)
    if source == "upload":
        return upload_audio(sample_rate)
    if _in_colab():
        return _browser_capture("mic", seconds, sample_rate)
    return _local_capture(seconds, sample_rate)


print("Audio helper ready.")
print('  record(2.0)          record from your microphone')
print('  demo_audio("no")     a stand-in sound, no microphone needed')
print('  upload_audio()       use a sound file from your computer')
print('  trim_silence(x)      cut the quiet ends off a recording')
