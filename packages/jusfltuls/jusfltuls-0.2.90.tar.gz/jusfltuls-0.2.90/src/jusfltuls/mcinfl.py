import curses
import click
import logging
import random

import jusfltuls.mcinfl_library as maninf
#from  jusfltuls.mcinfl_library import user_glob # set this for all session
import sys
import datetime as dt
import os
import time
from console import fg, bg, fx
import socket
from jusfltuls.check_new_version import is_there_new_version

"""
1.    -portable   -skip-errors   sometimes not possibnle

~/.visidatarc
# ------------------------------------------------------------
# RUNWITH  uvx --with=numpy visidata -p export_local_flashcam5000_20250522_0838_01.vdj
options.color_key_col=''
options.color_selected_row='yellow'
options.color_note_type='yellow'
#options.color_graph_hidden='blue'
options.color_column_sep='blue'
# COMMAND FOR '1'
BaseSheet.addCommand('1', 'hello-world1', 'status("Hello world! C-D saves and -p saved.vdj replays; z| sel ...; gt; gd; ")')
import numpy as np
import datetime as dt
BaseSheet.addCommand('2', 'hello-world2', 'status(f"Random sample: {np.random.sample()}  {dt.datetime.now().strftime(\'%t\')}")')
def t2d(time):
    return dt.datetime.fromtimestamp(time/1000000000)


"""


DISK_MIRROR_PATH = os.path.expanduser('~/INFLUXDB_MIRROR')

# In curses_main add state for disk mode per panel
# Add variables at start of curses_main:
left_disk_mode = False
right_disk_mode = False


def rename_with_extension_preserved(old_name, new_name):
    logging.debug(f" renaming_w_e_p  {old_name} to {new_name} ")

    base, ext = os.path.splitext(old_name.rstrip("/")) # if folder, I strip / to see ext
    mynew_name = new_name
    if not mynew_name.endswith(ext):
        logging.debug(f"  ext was  /{ext}/ BUT it doesnt match  ")
        mynew_name += ext
    logging.debug(f"  ext was  {ext} and new name is   {mynew_name} ")
    return mynew_name



# ================================================================================
#    panels status  +disk
# --------------------------------------------------------------------------------

def get_disk_panel_status():
    if not os.path.exists(DISK_MIRROR_PATH):
        os.makedirs(DISK_MIRROR_PATH)
    try:
        items = os.listdir(DISK_MIRROR_PATH)
    except Exception as e:
        items = []
    # Mark directories with trailing slash for clarity
    items = [f + '/' if os.path.isdir(os.path.join(DISK_MIRROR_PATH, f)) else f for f in items]
    return sorted(items)



# Modify get_left_panel_status and get_right_panel_status to check disk mode:
def get_left_panel_status():
    if left_disk_mode:
        return get_disk_panel_status()
    else:
        return maninf.show_databases()

def get_right_panel_status():
    if right_disk_mode:
        return get_disk_panel_status()
    else:
        return maninf.show_databases()


# def get_left_panel_status():
#     res = maninf.show_databases()
#     logging.debug(f"{res}")
#     return res#["file1.txt", "file2.txt", "dir1/", "file3.log"]

# def get_right_panel_status():
#     res = maninf.show_databases()
#     logging.debug(f"{res}")# return ["doc1.pdf", "image.png", "music.mp3", "video.mp4"]
#     return res
#     #return ["doc1.pdf", "image.png", "music.mp3", "video.mp4"]


# ================================================================================
#  JUST A MESSAGE
# --------------------------------------------------------------------------------

def show_message_box(stdscr, message, wait_key=True):
    if message is None:
        return
    lines = [line.strip() for line in message.strip().split('\n')]
    h, w = stdscr.getmaxyx()
    #
    box_h = 8
    if len(lines) > 6 and len(lines) < h - 3:
        box_h = len(lines) + 2
    elif len(lines) > 6:
        box_h = h - 1
    box_w = max(len(line) for line in lines) + 4
    if box_w > w - 2:
        box_w = w - 2
    #
    win = curses.newwin(box_h, box_w, (h - box_h)//2, (w - box_w)//2)
    win.box()
    for i, line in enumerate(lines[:box_h - 2]):
        win.addstr(1 + i, 2, line[:box_w - 4])
    win.refresh()
    if wait_key:
        win.getch()  # wait for key press
    win.clear()
    stdscr.refresh()


# ================================================================================
#  CONFIRM   MESSAGE
# --------------------------------------------------------------------------------


def confirm_dialog(stdscr, prompt):
    h, w = stdscr.getmaxyx()
    pro = prompt.split("\n")
    lines = len(pro)
    lenpromptmax = 1
    for i in pro:
        if len(i) > lenpromptmax:
            lenpromptmax =len(i)

    win = curses.newwin(5 + lines, lenpromptmax + 12, h//2 - 2, (w - lenpromptmax - 12)//2)
    win.box()
    ii = 0
    for i in pro:
        win.addstr(1 + ii, 3, i)
        ii += 1
    win.addstr(3 + lines, 4, "Yes (y) / No (n)")
    win.refresh()
    while True:
        c = win.getch()
        if c in (ord('y'), ord('Y')):
            return True
        elif c in (ord('n'), ord('N')):
            return False


def on_backup(stdscr):
    """
     RUN  influxd backup  -portable  to the hardcoded PATH
    """
    NOW = dt.datetime.now().strftime("%Y%m%d_%H%M")
    #PATH = f"~/INFL_BACKUP_PORTABLE_{NOW}"
    PATH = f"{DISK_MIRROR_PATH}/_full_backup_{NOW}"
    #newname = input_dialog(stdscr, f"Backup Full Influx? -portable -skip-errors")
    confirm = confirm_dialog(stdscr, f"Backup Full Influx? -portable -skip-errors; {PATH}")
    if confirm:
        PATH = os.path.expanduser(PATH)
        if os.path.exists(PATH):
            pass
        else:
            os.mkdir(PATH)
        logging.debug(f"Started  backup to {PATH}")
        maninf.backup_portable(PATH)
        logging.debug(f"Done backup to {PATH}")

def on_copy(name, dbase, other_dbase, stdscr, wordcopy="COPY", asking=True):
    logging.debug(f"copying - {name}/{dbase} -> {other_dbase};")
    if stdscr:
        confirm = True
        if asking:
            confirm = confirm_dialog(stdscr, f"{wordcopy} measurement '{name}' of {dbase} TO {other_dbase}?")
        if confirm:
            if (name is None) or (dbase is None) or (other_dbase is None):
                pass
            else:
                res = maninf.copy_measurement(name, dbase, other_dbase, silent=True)
                logging.debug( f"{res}")
            logging.debug(f"copied '{name}'")
        else:
            logging.debug(f"copying cancelled for '{name}'")
    else:
        # If no stdscr provided, assume yes or handle differently
        # maninf.drop_database(name)
        logging.debug(f"copied '{name}' without confirmation")
    pass

def on_move():
    logging.debug(f"moving - ;")
    pass

def on_create_database(name):
    logging.debug(f"creating new thing - {name};")
    if name is None or len(name) == 0:
        return
    maninf.create_database(name)
    pass

def on_delete_database(name, stdscr):
    logging.debug(f"deleting database - {name};")
    if stdscr:
        confirm = confirm_dialog(stdscr, f"Delete database '{name}'?")
        if confirm:
            maninf.drop_database(name)
            logging.debug(f"Deleted '{name}'")
        else:
            logging.debug(f"Deletion cancelled for '{name}'")
    else:
        # If no stdscr provided, assume yes or handle differently
        # maninf.drop_database(name)
        logging.debug(f"Deleted '{name}' without confirmation")


def on_delete_measurement(name, database, stdscr, asking=True):
    """
    I took the same as delete database
    """
    logging.debug(f"deleting measurement - {name} from {database};")
    if stdscr:
        confirm = True
        if asking:
            confirm = confirm_dialog(stdscr, f"Delete measurement '{name}' of {database}?")
        if confirm:
            maninf.delete_measurement(name, database)
            logging.debug(f"Deleted measurement '{name}' from {database}")
        else:
            logging.debug(f"Deletion cancelled for meas. '{name}' of {database}")
    else:
        # If no stdscr provided, assume yes or handle differently
        # maninf.drop_database(name)
        logging.debug(f"Deleted '{name}' without confirmation")



def draw_panel(win, items, selected_idx, active, offset, disk_mode=False):
    """
     updated for offset to enable scrolling; updated to show mode
    """
    h, w = win.getmaxyx()
    win.clear()
    win.box()
    # Draw mode indicator inside the top border line, centered
    mode_text = "[DISK MODE]" if disk_mode else "[INFLUXDB]"
    #mode_text = mode_text.center(w - 2)
    try:
        # Add mode text on top border line at row 0, col 1 (inside box)
        win.addstr(0, w - len(mode_text) * 2, mode_text, curses.A_BOLD | (curses.A_REVERSE if active else curses.A_DIM))
    except curses.error:
        pass
    visible_items = items[offset:offset + h - 2]
    for idx, item in enumerate(visible_items):
        real_idx = idx + offset
        if real_idx == selected_idx:
            mode = curses.A_REVERSE if active else curses.A_BOLD
        else:
            mode = curses.A_NORMAL
        try:
            win.addstr(idx + 1, 1, item[:w-3], mode)
        except curses.error:
            pass
    win.refresh()

def draw_bottom_bar(stdscr):

    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)  # text black, background cyan

    h, w = stdscr.getmaxyx()
    #
    #
    bar_text = " 2 Export  (s-)3 View  4 Insert  5 Copy  6 Move/RenameDB  7 Create  8 Delete [b-backup r-refresh d-diskpanel] "
    hostname = socket.gethostname()
    # Reserve space for hostname plus a space before it
    max_bar_width = w - len(hostname) - 1
    bar_text = bar_text[:max_bar_width]
    bar_text = bar_text.ljust(max_bar_width) + " " + hostname
    #
    #
    stdscr.attron(curses.color_pair(1))
    #stdscr.attron(curses.A_REVERSE)

    # Truncate bar_text if wider than screen width
    text = bar_text[:w]
    try:
        stdscr.addstr(h-1, 0, text.ljust(w))
    except curses.error:
        # In case window too small, ignore error
        pass
    #stdscr.attroff(curses.A_REVERSE)
    stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()

def input_dialog(stdscr, prompt):
    curses.echo()
    h, w = stdscr.getmaxyx()
    win = curses.newwin(3, w//2, h//2 - 1, w//4)
    win.box()
    win.addstr(1, 2, prompt)
    win.refresh()
    stdscr.refresh()
    curses.curs_set(1)
    input_win = curses.newwin(1, w//2 - len(prompt) - 4, h//2, w//4 + len(prompt) + 2)
    curses.echo()
    input_win.clear()
    input_win.refresh()
    s = input_win.getstr().decode('utf-8')
    curses.noecho()
    curses.curs_set(0)
    return s

# ================================================================================
#    MAIN *****************************
# --------------------------------------------------------------------------------

@click.command()
@click.option('--logfile', default='/tmp/mcinflux_debug.log', help='Log file path')
@click.option('--user', "-u", is_flag=True, help='Act as user, use user name and pass')
def main(logfile, user):

    global user_glob
    global left_disk_mode, right_disk_mode

    is_there_new_version(package="jusfltuls", printit=True, printall=True)

    print("Hey, machine is expected in the format like '127.0.0.1' or 'www.example.com' (where --ssl is selected) ")
    logging.basicConfig(filename=logfile, level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.debug('Debug log started')

    print("""
---------------------------------------------------------------------------
THE FILE(S) NEEDED:""")
    maninf.verify_files(justprint=True)
    print()

    print(f"i... switch 'user' is {user}")
    maninf.user_glob = user # set this for all session
    print(f"i... global var 'userg' is {maninf.user_glob}")
    #
    ok = maninf.verify_files()
    if not ok:
        print("X...  files missing")
        sys.exit(1)
    #
    u, p, serv =maninf.get_user_pass()
    if u is None or p is None:
        print("X... user o pass problem", u)
        sys.exit(1)
    #else:        print(f"/{u}/, /{p}/")

    m =serv#maninf.get_local_machine()

    if m is None:
        print("X... machine name problem")
        sys.exit(1)

    print(f"i... user: {fg.green}{u}{fg.default} on machine: {fg.yellow}{m}{fg.default} , I am going  there")
    res = maninf.show_databases()
    if len(res) == 0:
        print(f"X... NO DATABASES seen:   trying -u switch, {fg.magenta} changing user {fg.default} ")
        time.sleep(1)
        #
        maninf.user_glob = not user # set this for all session
        print(f"i... variable 'userg' is {maninf.user_glob}")
        #
        u, p, serv =maninf.get_user_pass()
        if u is None or p is None:
            print("X... user or passwd problem")
            maninf.is_infl_active()
            sys.exit(1)
        #else:        print(f"/{u}/, /{p}/")

        m =serv#maninf.get_local_machine()

        if m is None:
            print("X... machine name problem")
            sys.exit(1)

            print(f"i... user: {u} on machine: {m} , I am going  there")


    print("""
    TO CREATE A USER AND PRIVILEGE:
    nano /etc/influxdb/influxdb.conf ; auth-enabled = false ;
    influx ; create user abc with password 'def' with all privileges;
    nano /etc/influxdb/influxdb.conf; auth-enabled = true;
    systemctl restart influxd
    ---------------------------------------------------------------------------
""")
    maninf.verify_files()

    def curses_main(stdscr):

        global left_disk_mode, right_disk_mode

        #print("Ciao")
        logging.debug("Ciao")
        left_db_selected = None
        right_db_selected = None

        # previous idx==remember where to return
        left_idx_prev = 0
        right_idx_prev = 0

        left_offset, right_offset = 0, 0

        curses.curs_set(0)
        stdscr.clear()
        stdscr.refresh()
        left_items = get_left_panel_status()
        right_items = get_right_panel_status()
        left_idx, right_idx = 0, 0
        active_panel = 'left'

        h, w = stdscr.getmaxyx()
        mid = w // 2

        left_win = curses.newwin(h-1, mid, 0, 0)
        right_win = curses.newwin(h-1, w - mid, 0, mid)


        # Modify refresh_panels to use updated get_left_panel_status and get_right_panel_status
        def refresh_panels():
            nonlocal left_items, right_items, left_idx, right_idx
            global left_disk_mode, right_disk_mode

            if left_disk_mode:
                left_items = get_disk_panel_status()
            else:
                if left_db_selected is None:
                    left_items = maninf.show_databases()
                else:
                    left_items = ['..'] + maninf.show_measurements(left_db_selected)
            if right_disk_mode:
                right_items = get_disk_panel_status()
            else:
                if right_db_selected is None:
                    right_items = maninf.show_databases()
                else:
                    right_items = ['..'] + maninf.show_measurements(right_db_selected)
            left_idx = min(left_idx, len(left_items) - 1) if left_items else 0
            right_idx = min(right_idx, len(right_items) - 1) if right_items else 0

        # def refresh_panels():
        #     nonlocal left_items, right_items, left_idx, right_idx
        #     if left_db_selected is None:
        #         left_items = get_left_panel_status()
        #     else:
        #         left_items = ['..'] + maninf.show_measurements(left_db_selected)
        #     if right_db_selected is None:
        #         right_items = get_right_panel_status()
        #     else:
        #         right_items = ['..'] + maninf.show_measurements(right_db_selected)
        #     left_idx = min(left_idx, len(left_items) - 1) if left_items else 0
        #     right_idx = min(right_idx, len(right_items) - 1) if right_items else 0

        refresh_panels()

        # older
        #draw_panel(left_win, left_items, left_idx, active_panel == 'left')
        #draw_panel(right_win, right_items, right_idx, active_panel == 'right')
        # newer with scrolling
        draw_panel(left_win, left_items, left_idx, active_panel == 'left', left_offset, disk_mode=left_disk_mode)
        draw_panel(right_win, right_items, right_idx, active_panel == 'right', right_offset, disk_mode=right_disk_mode)
        #
        draw_bottom_bar(stdscr)

        while True:
            key = stdscr.getch()
            if key == 9:  # TAB
                active_panel = 'right' if active_panel == 'left' else 'left'
                if active_panel == 'left':
                    left_idx = max(0, min(left_idx, len(left_items) - 1))
                else:
                    right_idx = max(0, min(right_idx, len(right_items) - 1))

            # ---------------------------------------- original movement in panels

            # elif key == curses.KEY_UP:
            #     if active_panel == 'left':
            #         left_idx = max(0, left_idx - 1)
            #     else:
            #         right_idx = max(0, right_idx - 1)

            # elif key == curses.KEY_DOWN:
            #     if active_panel == 'left':
            #         left_idx = min(len(left_items) - 1, left_idx + 1)
            #     else:
            #         right_idx = min(len(right_items) - 1, right_idx + 1)


            # new panel movement with scrolling
            elif (key == curses.KEY_UP) and active_panel == 'left':
                if left_idx > 0:
                    left_idx -= 1
                    if left_idx < left_offset:
                        left_offset -= 1
            elif (key == curses.KEY_DOWN) and active_panel == 'left':
                if left_idx < len(left_items) - 1:
                    left_idx += 1
                    h, _ = left_win.getmaxyx()
                    if left_idx >= left_offset + h - 2:
                        left_offset += 1
            elif (key == curses.KEY_UP) and active_panel == 'right':
                if right_idx > 0:
                    right_idx -= 1
                    if right_idx < right_offset:
                        right_offset -= 1
            elif (key == curses.KEY_DOWN) and active_panel == 'right':
                if right_idx < len(right_items) - 1:
                    right_idx += 1
                    h, _ = right_win.getmaxyx()
                    if right_idx >= right_offset + h - 2:
                        right_offset += 1



            # ------------------------------------------------------------
            elif key == ord('2'):# --------------------------------- export measurement to csv file
                if (active_panel == 'left' and left_disk_mode) or (active_panel == 'right' and right_disk_mode):
                    show_message_box(stdscr, "FEATURE NOT IMPLEMENTED")
                    pass
                else:
                    name = None
                    dbase = None
                    if active_panel == 'left':
                        name = left_items[left_idx]
                        dbase = left_db_selected
                        other_dbase = right_db_selected
                    else:
                        name = right_items[right_idx]
                        dbase = right_db_selected
                        other_dbase = left_db_selected

                    res = maninf.export_measurement(name, dbase, silent=True)
                    logging.debug(f"{res}")
                    #show_message_box(stdscr, f"{res}")
                refresh_panels()

            elif key == ord('3'):# --------------------------------- View measurement
                if (active_panel == 'left' and left_disk_mode) or (active_panel == 'right' and right_disk_mode):
                    show_message_box(stdscr, "FEATURE NOT IMPLEMENTED")
                    pass
                else:
                    name = None
                    dbase = None
                    if active_panel == 'left':
                        name = left_items[left_idx]
                        dbase = left_db_selected
                        other_dbase = right_db_selected
                    else:
                        name = right_items[right_idx]
                        dbase = right_db_selected
                        other_dbase = left_db_selected

                    res = maninf.show_measurement_newest_sample(name, dbase, silent=True)
                    logging.debug(f"{res}")
                    show_message_box(stdscr, f"{res}")
                refresh_panels()

            elif key == ord('#'):#   shift-3------------------- VIEW measurement continuously
                if (active_panel == 'left' and left_disk_mode) or (active_panel == 'right' and right_disk_mode):
                    show_message_box(stdscr, "FEATURE NOT IMPLEMENTED")
                    pass
                else:
                    name = None
                    dbase = None
                    if active_panel == 'left':
                        name = left_items[left_idx]
                        dbase = left_db_selected
                        other_dbase = right_db_selected
                    else:
                        name = right_items[right_idx]
                        dbase = right_db_selected
                        other_dbase = left_db_selected

                    logging.debug(f"repeating view ....")
                    stdscr.nodelay(True)  # Non-blocking input
                    time_restrict = dt.datetime.now().isoformat() + "Z"  # ISO 8601 format with Zulu time
                    #
                    local = dt.datetime.now().astimezone()  # local time with timezone info
                    utc_dt = local.astimezone(dt.timezone.utc)
                    time_restrict = utc_dt.isoformat().replace("+00:00", "Z")
                    #time_restrict = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")#isoformat() + "Z"  # ISO 8601 format with Zulu time
                    time1 = dt.datetime.now().strftime("%H:%M:%S")
                    logging.debug(f"repeating view ....{time_restrict}")

                    while True:
                        time2 = dt.datetime.now().strftime("%H:%M:%S") # interesting. when time1 inside strftime, overrided
                        res = maninf.show_measurement_newest_sample(name, dbase, silent=True, prepend=f"measurement from {time1}  ==>>>  {time2}", time_restrict=time_restrict)
                        show_message_box(stdscr, f"{res}", wait_key=False)
                        time.sleep(2)
                        newkey = -1
                        ####newkey = stdscr.getch()
                        try:
                            newkey = stdscr.getch()
                        except curses.error:
                            newkey = -1
                        if newkey != -1:  # Any key pressed
                            break
                        refresh_panels()
                        draw_panel(left_win, left_items, left_idx, active_panel == 'left', left_offset, disk_mode=left_disk_mode)
                        draw_panel(right_win, right_items, right_idx, active_panel == 'right', right_offset, disk_mode=right_disk_mode)
                        #
                        draw_bottom_bar(stdscr)

                    stdscr.nodelay(False)  # Non-blocking input
                # --- "#"
                refresh_panels()

            elif key == ord('4'):# --------------------------------- INSERT measurement
                if (active_panel == 'left' and left_disk_mode) or (active_panel == 'right' and right_disk_mode):
                    show_message_box(stdscr, "FEATURE NOT IMPLEMENTED")
                    pass
                else:
                    name = None
                    dbase = None
                    if active_panel == 'left':
                        name = left_items[left_idx]
                        dbase = left_db_selected
                        other_dbase = right_db_selected
                    else:
                        name = right_items[right_idx]
                        dbase = right_db_selected
                        other_dbase = left_db_selected

                    aaa = ''.join(chr(random.randint(97, 122)) for _ in range(3))
                    res = maninf.insert_new_measurement(f"z_test_{aaa}", dbase, silent=True)
                    logging.debug(f"{res}")
                    #show_message_box(stdscr, f"{res}")
                refresh_panels()



            elif key == ord('5'):# --------------------------------- COPY measurement
                name = None
                dbase = None
                if not left_disk_mode and not right_disk_mode:
                    # -----------------------------------  all influx
                    if active_panel == 'left':
                        name = left_items[left_idx]
                        dbase = left_db_selected
                        other_dbase = right_db_selected
                    else:
                        name = right_items[right_idx]
                        dbase = right_db_selected
                        other_dbase = left_db_selected
                    logging.debug(f"copy no disk {name} from {dbase} to {other_dbase} ")
                    on_copy(name, dbase, other_dbase, stdscr)
                    refresh_panels()
                else:# ------------------- one panel is disk
                    if active_panel == 'left' and right_disk_mode:
                        name = left_items[left_idx]
                        dbase = left_db_selected
                        if name and dbase: # copy measurement
                            #filename = input_dialog(stdscr, f"Export measurement '{name}' from {dbase} to file (in mirror folder): ")
                            filename = f"{name}.csv"
                            logging.debug(f"copy to disk: {name} from {dbase} to {filename} ")
                            if filename:
                                filepath = os.path.join(DISK_MIRROR_PATH, filename)
                                res = maninf.export_measurement(name, dbase, filepath=filepath) # csv export
                                #show_message_box(stdscr, res)
                        elif name and dbase is None: # BACKUP
                            filename = f"{name}.exported"
                            filepath = os.path.join(DISK_MIRROR_PATH, filename)
                            if os.path.exists(filepath):
                                show_message_box(stdscr, f"NO BACKUP TO EXISTING BACKUP \n{filepath}")
                            else:
                                logging.debug(f"copy DB to disk: {name}  to {filepath} ")
                                maninf.backup_portable(filepath, name ) # ONE  DB BACKUP
                    elif  active_panel == 'right' and left_disk_mode:
                        name = right_items[right_idx]
                        dbase = right_db_selected
                        if name and dbase: # copy measurement
                            #filename = input_dialog(stdscr, f"Export measurement '{name}' from {dbase} to file (in mirror folder): ")
                            filename = f"{name}.csv"
                            if filename:
                                filepath = os.path.join(DISK_MIRROR_PATH, filename)
                                res = maninf.export_measurement(name, dbase, filepath=filepath) # csv export
                                #show_message_box(stdscr, res)
                        elif name and dbase is None: # BACKUP
                            filename = f"{name}.exported"
                            filepath = os.path.join(DISK_MIRROR_PATH, filename)
                            if os.path.exists(filepath):
                                show_message_box(stdscr, f"NO BACKUP TO EXISTING BACKUP {filepath}")
                            else:
                                logging.debug(f"copy DB to disk: {name}  to {filepath} ")
                                maninf.backup_portable(filepath, name ) # ONE  DB BACKUP
                    elif active_panel == "right" and right_disk_mode:
                        #show_message_box(stdscr, "FEATURE NOT IMPLEMENTED\n copying disk to DB right side")
                        name = right_items[right_idx]
                        if name.find(".exported") > 0:
                            basename = name.split(".exported")[0]
                            filepath = os.path.join(DISK_MIRROR_PATH, name)
                            oldname = maninf.restore_portable_get_oldname(filepath, database=basename)
                            confirm = confirm_dialog(stdscr, f"RESTORE DATABASE:\n {basename} \n Original name: \n {oldname}")
                            if confirm: maninf.restore_portable(filepath, database=basename)
                        else:
                            show_message_box(stdscr, "FEATURE NOT IMPLEMENTED\n copying disk to infl right side")
                        pass
                    elif active_panel == "left" and left_disk_mode:
                        name = left_items[left_idx]
                        if name.find(".exported") > 0:
                            basename = name.split(".exported")[0]
                            filepath = os.path.join(DISK_MIRROR_PATH, name)
                            oldname = maninf.restore_portable_get_oldname(filepath, database=basename)
                            confirm = confirm_dialog(stdscr, f"RESTORE DATABASE:\n {basename} \n Original name: \n {oldname}")
                            if confirm: maninf.restore_portable(filepath, database=basename)
                        else:
                            show_message_box(stdscr, "FEATURE NOT IMPLEMENTED\n copying disk to infl left side")
                        pass
                    else:
                        show_message_box(stdscr, "FEATURE NOT IMPLEMENTED")
                        pass
                refresh_panels() # refresh after copy




            elif key == ord('6'):# --------------------------------- MOVE measurement
                if (active_panel == 'left' and left_disk_mode) or (active_panel == 'right' and right_disk_mode):
                    show_message_box(stdscr, "FEATURE NOT IMPLEMENTED")
                    pass
                else:
                    name = None
                    dbase = None
                    if active_panel == 'left':
                        name = left_items[left_idx]
                        dbase = left_db_selected
                        other_dbase = right_db_selected
                    else:
                        name = right_items[right_idx]
                        dbase = right_db_selected
                        other_dbase = left_db_selected
                    if dbase is None or other_dbase is None:
                        logging.debug(f"I am in db view and F6 db=={name} this time. TO RENAME")
                        newname = input_dialog(stdscr, f"Rename {name} to : ")
                        if len(newname) > 0:
                            maninf.create_database(newname)
                            # now copy  all measurements in
                            res = maninf.show_measurements(name)
                            logging.debug(f"About to copy this to {newname}: {res}")
                            for i in res:
                                logging.debug(f" - copying {i} from {name} to {newname}")
                                on_copy(i, name, newname, stdscr, asking=False)
                                logging.debug(f" - not dropping {i} in {name}; ")
                            name = input_dialog(stdscr, f"You drop {name} database yourself ")
                        else:logging.debug("empty string for newname")
                    else:
                        logging.debug(f"I am in measurement view and F6 mea=={name}")
                        on_copy(name, dbase, other_dbase, stdscr, wordcopy="MOVE")
                        on_delete_measurement(name, dbase, stdscr, asking=False) # in move
                refresh_panels()
                #on_move()
                #refresh_panels()


            elif key == ord('7'):# --------------------------------- CREATE database
                if (active_panel == 'left' and left_disk_mode) or (active_panel == 'right' and right_disk_mode):
                    show_message_box(stdscr, "FEATURE NOT IMPLEMENTED")
                    pass
                else:
                    name = input_dialog(stdscr, "Create name: ")
                    on_create_database(name)
                refresh_panels()


            elif key == ord('8'): # --------------------------------- DELETE database/measurement
                if (active_panel == 'left' and left_disk_mode) or (active_panel == 'right' and right_disk_mode):
                    show_message_box(stdscr, "FEATURE NOT IMPLEMENTED")
                    pass
                else:
                    logging.debug("8... in delete mode...")
                    if active_panel == 'left':
                        if left_items:
                            #logging.debug("8... deleting...left...")
                            #logging.debug(f"8... deleting...left...{left_idx}")
                            selected_item = left_items[left_idx]
                            logging.debug(f"8. deleting...selected: {selected_item}, db={left_db_selected}")
                            if (selected_item != '..') and (left_db_selected is None): #  view ??? meas?
                                logging.debug(f"*in delete DB and db_sel {selected_item}")
                                #name = left_items[left_idx]
                                on_delete_database(selected_item, stdscr)
                                #on_delete_measurement(name, left_db_selected, stdscr)
                            elif (left_db_selected is not None): #  view datab ???
                                name = left_items[left_idx]
                                # name== selected_item
                                logging.debug(f"*in delete MEAS and Me={name} sel=={selected_item} DB={left_db_selected}")
                                on_delete_measurement(selected_item, left_db_selected, stdscr)
                    if active_panel == 'right':
                        if right_items:# right panel  ***********************
                            logging.debug("8... deleting...right ... TO DO !!!")
                            selected_item = right_items[right_idx]
                            logging.debug(f"8. deleting...selected: {selected_item}, db={right_db_selected}")
                            if (selected_item != '..') and (right_db_selected is None): #  view ??? meas?
                                logging.debug(f"*in delete DB and db_sel {selected_item}")
                                on_delete_database(selected_item, stdscr)
                            elif (right_db_selected is not None): #  view datab ???
                                name = right_items[right_idx]
                                logging.debug(f"*in delete MEAS and Me={name} sel=={selected_item} DB={right_db_selected}")
                                on_delete_measurement(selected_item, right_db_selected, stdscr)
                    # -----------------------------------------------------
                refresh_panels()




            elif key == ord('^'):  # SHIFT-6 rename measurement or disk file
                if active_panel == 'left':
                    if left_disk_mode:
                        # Rename file in disk mirror folder
                        selected_item = left_items[left_idx]
                        if selected_item == '..':
                            show_message_box(stdscr, "Cannot rename parent directory entry")
                        else:
                            old_path = os.path.join(DISK_MIRROR_PATH, selected_item.rstrip('/'))
                            new_name = input_dialog(stdscr, f"Rename file '{selected_item}' to: ")
                            if new_name:
                                logging.debug(f"  rename left new=   {new_name} ")

                                new_name = rename_with_extension_preserved(selected_item, new_name)
                                new_path = os.path.join(DISK_MIRROR_PATH, new_name)
                                logging.debug(f"  rename left new pa=   {new_path} ")
                                try:
                                    os.rename(old_path, new_path)
                                    #show_message_box(stdscr, f"Renamed '{selected_item}' to '{new_name}'")
                                except Exception as e:
                                    show_message_box(stdscr, f"Rename failed: {e}")
                                refresh_panels()
                    else:
                        # Rename measurement in influxdb
                        name = left_items[left_idx]
                        dbase = left_db_selected
                        if name and dbase:
                            new_name = input_dialog(stdscr, f"Rename measurement '{name}' to: ")
                            if new_name and new_name != name:
                                # Copy measurement to new_name then delete old
                                res_copy = maninf.copy_measurement(name, dbase, dbase, silent=True, new_measurement_name=new_name)
                                if "error" not in res_copy.lower():
                                    maninf.delete_measurement(name, dbase)
                                    #show_message_box(stdscr, f"Renamed measurement '{name}' to '{new_name}'")
                                else:
                                    show_message_box(stdscr, f"Rename failed: {res_copy}")
                                refresh_panels()
                else:# right panel is active ------------------------------------------
                    if right_disk_mode:
                        selected_item = right_items[right_idx]
                        if selected_item == '..':
                            show_message_box(stdscr, "Cannot rename parent directory entry")
                        else:
                            old_path = os.path.join(DISK_MIRROR_PATH, selected_item.rstrip('/'))
                            new_name = input_dialog(stdscr, f"Rename file '{selected_item}' to: ")
                            logging.debug(f"  rename right new=   {new_name} ")
                            if new_name:
                                new_name = rename_with_extension_preserved(selected_item, new_name)
                                new_path = os.path.join(DISK_MIRROR_PATH, new_name)
                                logging.debug(f"  rename right new pa=   {new_path} ")
                                try:
                                    os.rename(old_path, new_path)
                                    #show_message_box(stdscr, f"Renamed '{selected_item}' to '{new_name}'")
                                except Exception as e:
                                    show_message_box(stdscr, f"Rename failed: {e}")
                                refresh_panels()
                    else:# ---- influxdb mode ---------------
                        name = right_items[right_idx]
                        dbase = right_db_selected
                        if name and dbase:
                            new_name = input_dialog(stdscr, f"Rename measurement '{name}' to: ")
                            if new_name and new_name != name:
                                res_copy = maninf.copy_measurement(name, dbase, dbase, silent=True, new_measurement_name=new_name)
                                if "error" not in res_copy.lower():
                                    maninf.delete_measurement(name, dbase)
                                    #show_message_box(stdscr, f"Renamed measurement '{name}' to '{new_name}'")
                                else:
                                    show_message_box(stdscr, f"Rename failed: {res_copy}")
                                refresh_panels()


            elif key == ord('r'): # --------------------------------- refresh panels
                refresh_panels()



            elif key == ord('d'):  # ----------------------------------- CHANGE  DISK MODE --------------
                if active_panel == 'left':
                    left_disk_mode = not left_disk_mode
                    if left_disk_mode:
                        # Reset selection and offset for disk mode
                        left_idx = 0
                        left_offset = 0
                    else:
                        # Reset selection and offset for influxdb mode
                        left_idx = 0
                        left_offset = 0
                else:
                    right_disk_mode = not right_disk_mode
                    if right_disk_mode:
                        right_idx = 0
                        right_offset = 0
                    else:
                        right_idx = 0
                        right_offset = 0
                refresh_panels()



            elif key == ord('b'): # --------------------------------- backup ALL  ... to the hardcoded path
                on_backup(stdscr)
                refresh_panels()

            elif key in (curses.KEY_ENTER, 10, 13): # movements throug influxdb or view basics info on measurement
                if active_panel == 'left':
                    logging.debug(f"Left ENTER db-selected=={left_db_selected}")
                    if left_items:
                        selected_item = left_items[left_idx]
                        logging.debug(f"Left ENTER item-selected=={selected_item}")
                        if selected_item == '..': # going up
                            left_db_selected = None
                            left_items = get_left_panel_status()
                            left_idx = left_idx_prev # not 0
                        elif left_db_selected is None:
                            left_db_selected = selected_item
                            left_idx_prev = left_idx # store  previous index
                            left_items = ['..'] + maninf.show_measurements(left_db_selected)
                            left_idx = 0
                        else:
                            logging.debug(f"enter on measurement: see newest; m1={selected_item} db1={left_db_selected}")
                            res = maninf.show_measurement_newest_oldest(selected_item, left_db_selected, silent=True)

                            logging.debug(f"{res}")
                            show_message_box(stdscr, res)
                            pass
                else: # the active panel is right ---------
                    logging.debug(f"Right ENTER db-selected=={right_db_selected}")
                    # ----
                    if right_disk_mode: # NEW DISK HANDLING
                        selected_item = right_items[right_idx]
                        path = os.path.join(DISK_MIRROR_PATH, selected_item.rstrip('/'))
                        if selected_item == '..':
                            # Go up one directory if inside subdir, else stay
                            parent = os.path.dirname(DISK_MIRROR_PATH)
                            # For simplicity, stay in root mirror folder (no going above)
                            pass
                        elif os.path.isdir(path):
                            # Optional: implement subdir navigation if desired
                            text = ""
                            if selected_item.find(".exported") > 0:
                                nm1 = selected_item.split(".exported")[0]
                                text = f"... exported database: \n {nm1}"
                            show_message_box(stdscr, f"Directory: \n {selected_item} \n {text}")
                        elif os.path.isfile(path):
                            try:
                                with open(path, 'r') as f:
                                    content = f.read(1024)
                                show_message_box(stdscr, f"File: {selected_item}\n\n{content}")
                            except Exception as e:
                                show_message_box(stdscr, f"Error reading file: {e}")
                        refresh_panels()

                    elif right_items: #   PREVIOUS HANDLING influxdb
                        selected_item = right_items[right_idx]
                        if selected_item == '..':
                            right_db_selected = None
                            right_items = get_right_panel_status()
                            right_idx = right_idx_prev # 0
                        elif right_db_selected is None:
                            right_db_selected = selected_item
                            right_idx_prev = right_idx # store
                            right_items = ['..'] + maninf.show_measurements(right_db_selected)
                            right_idx = 0
                        else:
                            logging.debug(f"enter on measurement: see newest; m1={selected_item} db1={right_db_selected}")
                            res = maninf.show_measurement_newest_oldest(selected_item, right_db_selected, silent=True)

                            logging.debug(f"{res}")
                            show_message_box(stdscr, res)
                            pass

            # elif key in (curses.KEY_ENTER, 10, 13):
            #     if active_panel == 'left':
            #         if left_items:
            #             left_db_selected = left_items[left_idx]
            #             left_items = maninf.show_measurements(left_db_selected)
            #             left_idx = 0
            #     else:
            #         if right_items:
            #             right_db_selected = right_items[right_idx]
            #             right_items = maninf.show_measurements(right_db_selected)
            #             right_idx = 0

            elif key in (ord('q'), 27):  # q or ESC to quit
                break

            #  newer with scrolling
            draw_panel(left_win, left_items, left_idx, active_panel == 'left', left_offset, disk_mode=left_disk_mode)
            draw_panel(right_win, right_items, right_idx, active_panel == 'right', right_offset, disk_mode=right_disk_mode)
            #
            draw_bottom_bar(stdscr)

    curses.wrapper(curses_main)

if __name__ == "__main__":
    main()
