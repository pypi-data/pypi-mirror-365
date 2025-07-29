#!/usr/bin/env python3
import curses
import sys
import os
from dataclasses import dataclass, field

@dataclass
class EditorState:
    lines: list[str] = field(default_factory=lambda: [""])
    cy: int = 0
    cx: int = 0
    filename: str = ""
    message: str = ""
    kill_ring: list[str] = field(default_factory=list)
    execute_pending: bool = False

@dataclass
class AppState:
    buffers: list[EditorState] = field(default_factory=list)
    current: int = 0

def open_buffer(path: str, app: AppState):
    buf = EditorState()
    buf.filename = path
    try:
        with open(path) as f:
            buf.lines = f.read().splitlines() or [""]
    except FileNotFoundError:
        buf.lines = [""]
    app.buffers.append(buf)
    app.current = len(app.buffers) - 1
    
def draw(stdscr, st: EditorState):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    for i, line in enumerate(st.lines[: h - 1]):
        stdscr.addstr(i, 0, line[: w - 1])
    status = f"{st.filename or '[No File]'} — {st.cy+1},{st.cx+1}"
    stdscr.addstr(h - 1, 0, status.ljust(w - 1), curses.A_REVERSE)
    if st.message:
        stdscr.addstr(h - 1, len(status) + 1, st.message[: w - len(status)-2], curses.A_REVERSE)
    stdscr.move(st.cy, st.cx)
    stdscr.refresh()
    st.message = ""

def save_file(st: EditorState):
    try:
        with open(st.filename, "w") as f:
            f.write("\n".join(st.lines))
        st.message = "Saved"
    except Exception as e:
        st.message = f"Error: {e}"

def open_file(st: EditorState, path: str):
    st.filename = path
    if os.path.exists(path):
        with open(path) as f:
            st.lines = f.read().splitlines() or [""]
    else:
        st.lines = [""]
    st.cy = st.cx = 0

        
# ----------------------------------------
# Helper: yank any text chunk (may contain "\n")
# ----------------------------------------
def do_yank(st: EditorState, text: str):
    if "\n" not in text:
        # simple insert
        line = st.lines[st.cy]
        st.lines[st.cy] = line[:st.cx] + text + line[st.cx:]
        st.cx += len(text)
    else:
        # multi-line insert
        parts = text.split("\n")
        need_suffix = text.endswith("\n")

        old = st.lines[st.cy]
        prefix, suffix = old[:st.cx], old[st.cx:]

        new_lines = []
        # first line = prefix + first killed piece
        new_lines.append(prefix + parts[0])
        # middle lines = any in-between killed lines
        for piece in parts[1:]:
            new_lines.append(piece)

        if need_suffix:
            # trailing newline: the suffix becomes its own line
            new_lines.append(suffix)
        else:
            # no trailing newline: append suffix to last piece
            new_lines[-1] += suffix

        # splice into buffer
        st.lines[st.cy:st.cy + 1] = new_lines

        # update cursor to end of yanked block
        st.cy += len(new_lines) - 1
        st.cx = 0 if need_suffix else len(parts[-1])

def search_forward(st, stdscr):
    curses.echo()
    height, _ = stdscr.getmaxyx()
    stdscr.addstr(height - 1, 0, "Search: ")
    query = stdscr.getstr().decode()
    curses.noecho()

    for y in range(st.cy, len(st.lines)):
        xstart = st.cx if y == st.cy else 0
        idx = st.lines[y].find(query, xstart)
        if idx != -1:
            st.cy, st.cx = y, idx
            st.message = f"Found: {query}"
            return
    st.message = f"Not found: {query}"
    
def main(stdscr, path=None):
    curses.raw()
    stdscr.keypad(True)
    app = AppState()
    if path:
        open_buffer(path, app)
    else:
        app.buffers.append(EditorState())
    st = app.buffers[app.current]
    
    while True:
        draw(stdscr, st)
        k = stdscr.getch()

        # Exit sequence Ctrl-x (24), then Ctrl-c (3)
        if k == 24:
            st.execute_pending = True
            st.message = "^X"
            continue
        if st.execute_pending and k == 3:
            break

        # Save (Ctrl-x Ctrl-s)
        if st.execute_pending and k == 19:
            if not st.filename:
                st.message = "No filename"
            else:
                save_file(st)
            continue

        if st.execute_pending and k == ord('b'):  # Ctrl-x b
            app.current = (app.current + 1) % len(app.buffers)
            st = app.buffers[app.current]
            continue

        if st.execute_pending and k == 6:  # Ctrl-x Ctrl-f
            curses.echo()
            height, _ = stdscr.getmaxyx()
            stdscr.addstr(height - 1, 0, "Open: ")
            stdscr.clrtoeol()
            stdscr.refresh()
            path = stdscr.getstr().decode()
            curses.noecho()
            open_buffer(path, app)
            st = app.buffers[app.current]
            continue

        st.execute_pending = False

        # Search (Ctrl-s)
        # Ctrl-s: search forward
        if k == 19:
            search_forward(st, stdscr)
            continue
        
        # ----------------------------------------
        # Ctrl-K: kill‐line
        # ----------------------------------------
        if k == 11:  # Ctrl-K
            line = st.lines[st.cy]
        
            if st.cx < len(line):
                # kill from cursor to end-of-line, plus newline if there's a next line
                if st.cy + 1 < len(st.lines):
                    killed = line[st.cx:] + "\n"
                    # join with next line
                    st.lines[st.cy] = line[:st.cx] + st.lines.pop(st.cy + 1)
                else:
                    killed = line[st.cx:]
                    st.lines[st.cy] = line[:st.cx]
            else:
                # at end-of-line: kill the newline only (if any)
                if st.cy + 1 < len(st.lines):
                    killed = "\n"
                    st.lines[st.cy] = line + st.lines.pop(st.cy + 1)
                else:
                    killed = ""
        
            if killed:
                st.kill_ring.insert(0, killed)
            continue
        
        # ----------------------------------------
        # Ctrl-Y: yank most recent kill
        # ----------------------------------------
        if k == 25:  # Ctrl-Y
            if st.kill_ring:
                do_yank(st, st.kill_ring[0])
            continue
        
        
        # ----------------------------------------
        # Alt-Y: rotate the kill-ring, then yank
        # ----------------------------------------
        if k == 27:  # ESC, start of an Alt-sequence
            nxt = stdscr.getch()
            if nxt == ord("y"):
                if len(st.kill_ring) > 1:
                    # move the head to the tail
                    st.kill_ring.append(st.kill_ring.pop(0))
                do_yank(st, st.kill_ring[0])
            else:
                # you could handle other Alt-keys here
                pass
            continue

        # Movement
        if k in (curses.KEY_LEFT, 2):  # Ctrl-b
            if st.cx > 0: st.cx -= 1
            elif st.cy > 0:
                st.cy -= 1; st.cx = len(st.lines[st.cy])
            continue
        if k in (curses.KEY_RIGHT, 6):  # Ctrl-f
            line = st.lines[st.cy]
            if st.cx < len(line): st.cx += 1
            elif st.cy + 1 < len(st.lines):
                st.cy += 1; st.cx = 0
            continue
        if k in (curses.KEY_UP, 16):  # Ctrl-p
            if st.cy > 0:
                st.cy -= 1; st.cx = min(st.cx, len(st.lines[st.cy]))
            continue
        if k in (curses.KEY_DOWN, 14):  # Ctrl-n
            if st.cy + 1 < len(st.lines):
                st.cy += 1; st.cx = min(st.cx, len(st.lines[st.cy]))
            continue

        # Enter
        if k in (curses.KEY_ENTER, 10, 13):
            line = st.lines[st.cy]
            st.lines[st.cy : st.cy + 1] = [line[: st.cx], line[st.cx :]]
            st.cy += 1; st.cx = 0
            continue

        # Backspace
        if k in (curses.KEY_BACKSPACE, 127, 8):
            if st.cx > 0:
                line = st.lines[st.cy]
                st.lines[st.cy] = line[: st.cx - 1] + line[st.cx :]
                st.cx -= 1
            elif st.cy > 0:
                prev = st.lines[st.cy - 1]
                curr = st.lines.pop(st.cy)
                st.cy -= 1
                st.cx = len(prev)
                st.lines[st.cy] = prev + curr
            continue

        # Regular insert
        if 32 <= k <= 126:
            ch = chr(k)
            line = st.lines[st.cy]
            st.lines[st.cy] = line[: st.cx] + ch + line[st.cx :]
            st.cx += 1

    # On exit, auto-save if filename set
    if st.filename:
        save_file(st)

