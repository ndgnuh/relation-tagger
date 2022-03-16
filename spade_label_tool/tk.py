import pygame as pg
import custom_events as ce
import threading
from tkinter import Menu, Tk, Listbox
from tkinter.ttk import Frame, Button, Label

references: dict = {}


def import_menu(menubar):
    m = Menu(menubar)
    m.add_command(label="Import Data (CSV)")
    m.add_command(label="Import Data (JSON)")
    m.add_command(label="Import Label (TXT)",
                  command=ce.emit_func(ce.ACTION_IMPORT_LABELS))
    m.add_command(label="Import Session")
    return m


def export_menu(menubar):
    m = Menu(menubar)
    m.add_command(label="Export Data (JSON)")
    m.add_command(label="Export Label (TXT)")
    m.add_command(label="Export Session")
    return m


def file_menu(menubar):
    m = Menu(menubar)
    m.add_command(label="Settings")
    m.add_command(label="Exit", command=ce.emit_func(pg.QUIT))
    return m


def label_list(frame):
    lb = Listbox(frame)
    lb.pack()
    return lb


def tk_gui():
    root = Tk()

    menubar = Menu(root)
    menubar.add_cascade(menu=file_menu(menubar), label="File")
    menubar.add_cascade(menu=import_menu(menubar), label="Import")
    menubar.add_cascade(menu=export_menu(menubar), label="Export")

    def quit():
        ce.emit(pg.QUIT, now=True)
        root.destroy()
    menubar.add_command(label="Exit", command=quit)
    root.config(menu=menubar)

    label_list(root).grid(row=0, column=0)
    Button(text="Add label").grid(row=1, column=0)
    Button(text="Delete selected label").grid(row=2, column=0)
    root.mainloop()


def main():
    pg.init()
    pg_root = pg.display.set_mode((300, 300))
    threading.Thread(target=tk_gui).run()
    pg.event.pump()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()


main()
