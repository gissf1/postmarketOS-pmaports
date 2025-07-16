#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aron Ravikumar <aron.raviku@gmail.com>

from evdev import UInput, InputDevice, ecodes as e
import time
import threading

device = InputDevice('/dev/input/event2')
ENABLED = 1 # enabled
MODES = 2 # enabled or disabled
SPEED = 10
INTERVAL = 0.04  # seconds between moves
DPAD_MOVES = {
    e.BTN_DPAD_UP:    (0, -SPEED),
    e.BTN_DPAD_DOWN:  (0, SPEED),
    e.BTN_DPAD_LEFT:  (-SPEED, 0),
    e.BTN_DPAD_RIGHT: (SPEED, 0),
}

BUTTON_MAP = {
    e.BTN_WEST: e.KEY_ENTER,
    e.BTN_EAST:  e.BTN_LEFT,    # A: left click
    e.BTN_SOUTH: e.BTN_RIGHT,   # B: right click
    e.BTN_NORTH:  e.KEY_ESC,
    e.BTN_SELECT: e.KEY_ENTER,
    e.BTN_START: e.KEY_ENTER,
}

held_keys = set()
held_keys_lock = threading.Lock()

input_cap = {
    e.EV_REL: (e.REL_X, e.REL_Y),
    e.EV_KEY: (
        e.BTN_LEFT, e.BTN_RIGHT,
        e.KEY_ENTER, e.KEY_ESC
        ),
}

def cursor_loop():
    while True:
        time.sleep(INTERVAL)
        if ENABLED == 0:
            continue
        with held_keys_lock:
            for key in held_keys:
                dx, dy = DPAD_MOVES.get(key, (0, 0))
                ui.write(e.EV_REL, e.REL_X, dx)
                ui.write(e.EV_REL, e.REL_Y, dy)
            ui.syn()

ui = UInput(input_cap, name='Virtual Input')
print("Starting input conversion...")
threading.Thread(target=cursor_loop, daemon=True).start()
for event in device.read_loop():
#while True:
#    event = device.read_one()
    if event != None and event.type == e.EV_KEY:
        #print(event)
        code = event.code
        # D-Pad handling
        if code in DPAD_MOVES:
            with held_keys_lock:
                if event.value == 1:   # Press
                    held_keys.add(code)
                elif event.value == 0: # Release
                    held_keys.discard(code)
        # A/B mouse button click
        elif code == e.BTN_MODE and event.value == 1:
            ENABLED = (ENABLED + 1) % 2
        elif code in BUTTON_MAP and ENABLED == 1:
            button = BUTTON_MAP[code]
            ui.write(e.EV_KEY, button, event.value) # 1 for down, 0 for up
            ui.syn()
