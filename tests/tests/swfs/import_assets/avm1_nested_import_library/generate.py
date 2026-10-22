"""Generate a nested shared-library regression without external game assets."""
from pathlib import Path
import struct

ROOT = Path(__file__).parent

def tag(code, data=b''):
    return struct.pack('<HI', (code << 6) | 63, len(data)) + data

def push(value):
    data = b'\0' + value.encode() + b'\0'
    return b'\x96' + struct.pack('<H', len(data)) + data

def number(value):
    return b'\x96\x05\0\x07' + struct.pack('<i', value)

def trace(value):
    return push(value) + b'\x26'

def attach(symbol, instance):
    return number(20 if symbol == "Late" else 10) + push(instance) + push(symbol) + number(3) + push('_root') + b'\x1c' + push('attachMovie') + b'\x52'

def sprite(char_id, actions):
    return tag(39, struct.pack('<HH', char_id, 1) + tag(12, actions + b'\x07\0') + tag(1) + tag(0))

def export(char_id, name):
    return tag(56, struct.pack('<HH', 1, char_id) + name.encode() + b'\0')

def imported(url, char_id, name):
    return tag(71, url.encode() + b'\0\1\0' + struct.pack('<HH', 1, char_id) + name.encode() + b'\0')

def swf(name, tags):
    # RECT with zero bounds, 12fps, one frame; only trace output is tested.
    body = b'\x08\0' + struct.pack('<HH', 12 << 8, 1) + tags + tag(1) + tag(0)
    (ROOT / name).write_bytes(b'FWS\x08' + struct.pack('<I', len(body) + 8) + body)

swf('leaf.swf', sprite(1, b'') + export(1, 'Leaf'))
swf('library.swf',
    sprite(1, trace('Library frame') + push('attached=') + attach('Late', 'late') + b'\x21\x26')
    + export(1, 'Entry')
    + imported('leaf.swf', 3, 'Leaf')
    + sprite(2, trace('Late frame')) + export(2, 'Late'))
swf('test.swf', imported('library.swf', 1, 'Entry')
    + tag(12, trace('Main frame') + attach('Entry', 'entry') + b'\x17\x07\0'))
