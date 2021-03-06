"""
Text Editor
"""
import os
from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
import sys
import enchant

PROGRAM_NAME = "P-PAD"
file_name = None

FILETYPES = [
    ("All Files", "*.*"), ("Text Documents", "*.txt"), ("Flash ActionScript file", ("*.as", "*.mx")),
    ("Ada file", ("*.ada", "*.ads", "*.adb")), ("Assembly Language source file", "*.asm"),
    ("Abstract Server Pages script file", "*.asp"), ("Autolt", '*.au3'), ("AviSynth script file", ("*.avs", "*.avsi")),
    ("BaanC file", ("*.bc", "*.cln")), ("Unix Script file", ("*.bash", "*.sh", "*.bsh", "*.csh", "*.bash_profile", "...")),
    ("Batch file", ("*.bat", "*.cmd", "*.nt")), ("BlitzBasic file", "*.bb"), ("C source file", ("*.c", "*.lex")),
    ("Categorical Abstract Machine Language", ("*.ml", "*.mli", "*.sml", "*.thy")), ("CMake file", "*.cmake"),
    ("COBOL", ("*.cbl", "*.cbd", "*.cdb", "*.cdc", "*.cob", "*.cpy", "*.copy", "*.lst")),
    ("CSound file", ("*.orc", "*.sco", "*.csd")), ("CoffeeScript file", ("*.coffee", "*.litcoffee")),
    ("C++ Source file", ("*.h", "*.hh", "*.hpp", "*.hxx", "*.cpp", "*.cxx", "*.cc", "*.ino")),
    ("C# source file", "*.cs"), ("Cascade Style Sheets file", "*.css"), ("D programming language", "*.d"),
    ("Diff file", ("*.diff", "*.patch")), ("Erlang file", ("*.erl", "*.hrl")), ("ESCRIPT file", ("*.src", "*.em")),
    ("Forth file", "*.forth"), ("Fortran free form source file", ("*.f", "*.for", "*.f90", "*.f95", "*.f2k", "*.f23")),
    ("Fortran fixed form source file", "*.f77"), ("FreeBasic file", ("*.bas", "*.bi")),
    ("Haskell", ("*.hs", "*.lhs", "*.las")), ("HTML file", ("*.html", "*.shtml", "*.xhtml", "*.htm", "*.shtm", "*.xht", "*.hta")),
    ("MS ini file", ("*.ini", "*.inf", "*.url", "*.wer")), ("InnoSetup script", "*.iss"), ("Intel HEX Binary Data", "*.hex"),
    ("Java Soruce file", "*.java"), ("JavaScript file", ("*.js", "*.jsm", "*.jsx", "*.ts", "*.tsx")), ("JSON file", "*.json"),
    ("Java Server Pages Script file", "*.jsp"), ("KixTart file", "*.kix"), ("List Processing Language", ("*.lsp", "*.lisp")),
    ("LaTex file", ("*.tex", "*.sty")), ("Lua source file", "*.lua"), ("Makefile", ("*.mak", "*.mk")), ("MATLAB", "*.m"),
    ("MMIXAL file", "*.mms"), ("Nimrod file", "*.nim"), ("Extended crontab file", ("*.tab", "*.spf")),
    ("MSDOS style/ASCII Art", "*.nfo"), ("Nullsoft Scriptable Install System script file", ("*.nsi", "*.nsh")),
    ("OScript Source file", "*.osx"), ("Objective-C source file", "*.mm"), ("Pascal Source file", ("*.pas", "*.pp", "*.p", "*.inc", "*.lpr")),
    ("Perl Source file", ("*.pl", "*.pm", "*.plx")), ("Post Script file", "*.ps"),
    ("PHP Hypertext Preprocessor file", ("*.php", "*.php3", "*.php4", "*.php5", "*.phps", "*.phpt", "*.phtml")),
    ("Windows PowerShell", ("*.ps1", "*.psm1")), ("Properties file", "*.properties"), ("PureBasic file", "*.pb"),
    ("Python file", ("*.py", "*.pyw", "*.pyz")), ("R programming file", ("*.r", "*.s", "*.splus")), ("REBOL file", ("*.r2", "*.r3", "*.reb")),
    ("registry file", "*.reg"), ("Windows Resource file", "*.rc"), ("Ruby file", ("*.rb", "*.rbw")), ("Rust file", "*.rs"),
    ("Scheme file", ("*.scm", "*.smd", "*.ss")), ("Smalltalk file", "*.st"), ("spice file", ("*.scp", "*.out")),
    ("Structured Query Language", "*.sql"), ("Motorola S-Record Binary data", ("*.mot", "*.srec")), ("Swift file", "*.swift"),
    ("Tool Command Language", "*.tcl"), ("Tektronix Extended HEX Binary data", "*.tek"), ("TeX file", "*.tex"),
    ("Visual Basic file", ("*.vb", "*.vbs")), ("txt2tags file", "*.t2t"), ("Verilog file", ("*.v", "*.sv", "*.vh", "*.svh")),
    ("VHSIC Hardware Description Language file", ("*.vhd", "*.vhdl")), ("Visual Prolog file", ("*.pro", "*.cl", "*.i", "*.pack", "*.ph")),
    ("eXtensible Markup Language", ("*.xml", "*.xaml", "*.xsl", "*.xslt", "*.xsd", "*.xul", "*.kml", "*.svg", "*.mxml", "*.xsml", "...")),
    ("YAML Ain't Markup Language", ("*.yml", "*.yaml"))
]


class LineNumberCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.text_widget = None
        self.breakpoints = []

    def connect(self, text_widget):
        self.text_widget = text_widget

    def re_render(self):
        """Re-render the line canvas"""
        self.delete('all') # To prevent drawing over the previous canvas

        temp = self.text_widget.index("@0, 0")
        while True :
            dline= self.text_widget.dlineinfo(temp)
            if dline is None: 
                break
            y = dline[1]
            x = dline[0]
            linenum = str(temp).split(".")[0]

            id = self.create_text(2, y, anchor="nw", text=linenum, font='Consolas 13')

            if int(linenum) in self.breakpoints:                
                x1, y1, x2, y2 = self.bbox(id)
                self.create_oval(x1, y1, x2, y2, fill='red')
                self.tag_raise(id)

            temp = self.text_widget.index("%s+1line" % temp)

    def get_breakpoint_number(self,event):
         if self.find_withtag('current'):
            i = self.find_withtag('current')[0]
            linenum = int(self.itemcget(i,'text'))

            if linenum in self.breakpoints:
                self.breakpoints.remove(linenum)
            else:
                self.breakpoints.append(linenum)
            self.re_render()


def mechanise():
    content_text.tk.eval('''
        proc widget_interceptor {widget command args} {

            set orig_call [uplevel [linsert $args 0 $command]]

          if {
                ([lindex $args 0] == "insert") ||
                ([lindex $args 0] == "delete") ||
                ([lindex $args 0] == "replace") ||
                ([lrange $args 0 2] == {mark set insert}) || 
                ([lrange $args 0 1] == {xview moveto}) ||
                ([lrange $args 0 1] == {xview scroll}) ||
                ([lrange $args 0 1] == {yview moveto}) ||
                ([lrange $args 0 1] == {yview scroll})} {

                event generate  $widget <<Changed>>
            }

            #return original command
            return $orig_call
        }
        ''')
    content_text.tk.eval('''
        rename {widget} new
        interp alias {{}} ::{widget} {{}} widget_interceptor {widget} new
    '''.format(widget=str(content_text)))
    return


def binding_keys():
    for key in ['<Down>', '<Up>', "<<Changed>>", "<Configure>"]:
        content_text.bind(key, changed)
    linenumbers.bind('<Button-1>', linenumbers.get_breakpoint_number)
    return


def changed(event):
    linenumbers.re_render()
    return


root = Tk()
text_frame = Frame(root, highlightthickness=1, highlightbackground='black')
content_text = Text(text_frame, wrap='word', undo=1, font='Consolas 13')

linenumbers = LineNumberCanvas(text_frame, width=30)
linenumbers.connect(content_text)
linenumbers.pack(side=LEFT, fill=Y)

# show pop-up menu

def show_popup_menu(event):
    popup_menu.tk_popup(event.x_root, event.y_root)


def show_cursor_info_bar():
    show_cursor_info_checked = show_cursor_info.get()
    if show_cursor_info_checked:
        cursor_info_bar.pack(expand='no', fill=None, side='right', anchor='se')
    else:
        cursor_info_bar.pack_forget()


def update_cursor_info_bar(event=None):
    row, col = content_text.index(INSERT).split('.')
    line_num, col_num = str(int(row)), str(int(col) + 1)  # col starts at 0
    infotext = "Line: {0} | Column: {1}".format(line_num, col_num)
    cursor_info_bar.config(text=infotext)


def update_sel_info_bar(event=None):
    sel_length = len(content_text.get(SEL_FIRST, SEL_LAST))
    sel_info_bar.config(text='Sel: {0} chars'.format(sel_length))


def change_theme(event=None):
    selected_theme = theme_choice.get()
    fg_bg_colors = color_schemes.get(selected_theme)
    foreground_color, background_color = fg_bg_colors.split('.')
    content_text.config(
        background=background_color, fg=foreground_color)


def highlight_line(interval=100):
    content_text.tag_remove("active_line", 1.0, "end")
    content_text.tag_add(
        "active_line", "insert linestart", "insert lineend+1c")
    content_text.after(interval, toggle_highlight)


def undo_highlight():
    content_text.tag_remove("active_line", 1.0, "end")


def toggle_highlight(event=None):
    if to_highlight_line.get():
        highlight_line()
    else:
        undo_highlight()


def on_content_changed(event=None):
    if event:
        update_cursor_info_bar(event)
    else:
        update_cursor_info_bar()


def display_about_messagebox(event=None):
    tkinter.messagebox.showinfo(
        "About", "{}{}".format(PROGRAM_NAME, "\nText Editor\prerakl123\pratapslodhaa@gmail.com"))


def display_help_messagebox(event=None):
    tkinter.messagebox.showinfo(
        "Help", "Help Book: \nText Editor\nprerakl123\npratapslodhaa@gmail.com",
        icon='question')


def exit_editor(event=None):
    leaving = tkinter.messagebox.askyesnocancel("P-Pad", "Do you want to save your current work before quitting?")
    if leaving is True:
        root.destroy()
    elif leaving is False:
        root.destroy()
    elif leaving is None:
        return


def new_file(event=None):
    root.title("Untitled")
    global file_name
    file_name = None
    content_text.delete(1.0, END)
    on_content_changed()


def open_file(event=None):
    input_file_name = tkinter.filedialog.askopenfilename(defaultextension=".txt", filetypes=FILETYPES)
    if input_file_name:
        global file_name
        file_name = input_file_name
        root.title('{} - {}'.format(os.path.basename(file_name), PROGRAM_NAME))
        content_text.delete(1.0, END)
        with open(file_name) as _file:
            content_text.insert(1.0, _file.read())
        on_content_changed()


def write_to_file(file_name):
    try:
        content = content_text.get(1.0, 'end')
        with open(file_name, 'w') as the_file:
            the_file.write(content)
    except IOError:
        tkinter.messagebox.showwarning("Save", "Could not save the file.")


def save_as(event=None):
    input_file_name = tkinter.filedialog.asksaveasfilename(defaultextension=".txt", filetypes=FILETYPES)
    if input_file_name:
        global file_name
        file_name = input_file_name
        write_to_file(file_name)
        root.title('{} - {}'.format(os.path.basename(file_name), PROGRAM_NAME))
    return "break"


def save(event=None):
    global file_name
    if not file_name:
        save_as()
    else:
        write_to_file(file_name)
    return "break"


def select_all(event=None):
    content_text.tag_add('sel', '1.0', 'end')
    return "break"


def find_text(event=None):
    search_toplevel = Toplevel(root)
    search_toplevel.title('Find Text')
    search_toplevel.transient(root)

    Label(search_toplevel, text="Find All:").grid(row=0, column=0, sticky='e')

    search_entry_widget = Entry(
        search_toplevel, width=25)
    search_entry_widget.grid(row=0, column=1, padx=2, pady=2, sticky='we')
    search_entry_widget.focus_set()
    ignore_case_value = IntVar()
    Checkbutton(search_toplevel, text='Ignore Case', variable=ignore_case_value).grid(
        row=1, column=1, sticky='e', padx=2, pady=2)
    Button(search_toplevel, text="Find All", underline=0,
           command=lambda: search_output(
               search_entry_widget.get(), ignore_case_value.get(),
               content_text, search_toplevel, search_entry_widget)
           ).grid(row=0, column=2, sticky='e' + 'w', padx=2, pady=2)

    def close_search_window():
        content_text.tag_remove('match', '1.0', END)
        search_toplevel.destroy()
    search_toplevel.protocol('WM_DELETE_WINDOW', close_search_window)
    return "break"


def search_output(needle, if_ignore_case, content_text,
                  search_toplevel, search_box):
    content_text.tag_remove('match', '1.0', END)
    matches_found = 0
    if needle:
        start_pos = '1.0'
        while True:
            start_pos = content_text.search(needle, start_pos,
                                            nocase=if_ignore_case, stopindex=END)
            if not start_pos:
                break
            end_pos = '{}+{}c'.format(start_pos, len(needle))
            content_text.tag_add('match', start_pos, end_pos)
            matches_found += 1
            start_pos = end_pos
        content_text.tag_config(
            'match', foreground='red', background='yellow')
    search_box.focus_set()
    search_toplevel.title('{} matches found'.format(matches_found))


def cut():
    content_text.event_generate("<<Cut>>")
    on_content_changed()
    return "break"


def copy():
    content_text.event_generate("<<Copy>>")
    return "break"


def paste():
    content_text.event_generate("<<Paste>>")
    on_content_changed()
    return "break"


def undo():
    content_text.event_generate("<<Undo>>")
    on_content_changed()
    return "break"


def redo(event=None):
    content_text.event_generate("<<Redo>>")
    on_content_changed()
    return 'break'

    
us_dict = enchant.Dict('EN_US')
in_dict = enchant.Dict('EN_IN')


def Spellcheck(event):
    '''Spellcheck the word preceeding the insertion point'''
    index = content_text.search(r'\s', "insert", backwards=True, regexp=True)
    if index == "":
        index ="1.0"
    else:
        index = content_text.index("%s+1c" % index)
    word = content_text.get(index, "insert")
    if us_dict.check(word) is True or in_dict.check(word) is True:
        content_text.tag_remove("misspelled", index, "%s+%dc" % (index, len(word)))
    else:
        content_text.tag_add("misspelled", index, "%s+%dc" % (index, len(word)))


def highlight_pattern(pattern, tag, start="1.0", end="end", regexp=False):
    '''Apply the given tag to all text that matches the given pattern

    If 'regexp' is set to True, pattern will be treated as a regular
    expression according to Tcl's regular expression syntax.
    '''
    
    start = self.index(start)
    end = self.index(end)
    self.mark_set("matchStart", start)
    self.mark_set("matchEnd", start)
    self.mark_set("searchLimit", end)

    count = IntVar()
    while True:
        index = self.search(pattern, "matchEnd","searchLimit", count=count, regexp=regexp)
        if index == "": break
        if count.get() == 0: break # degenerate pattern which matches zero-length strings
        self.mark_set("matchStart", index)
        self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
        self.tag_add(tag, "matchStart", "matchEnd")


content_text.tag_configure("misspelled", foreground="red", underline=True)


new_file_icon = PhotoImage(file='icons/new_file.png')
open_file_icon = PhotoImage(file='icons/open_file.png')
save_file_icon = PhotoImage(file='icons/save.png')
cut_icon = PhotoImage(file='icons/cut.png')
copy_icon = PhotoImage(file='icons/copy.png')
paste_icon = PhotoImage(file='icons/paste.png')
undo_icon = PhotoImage(file='icons/undo.png')
redo_icon = PhotoImage(file='icons/redo.png')


menu_bar = Menu(root, tearoff=0)

file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label='New', accelerator='Ctrl+N', compound='left',
                      image=new_file_icon, underline=0, command=new_file)
file_menu.add_command(label='Open', accelerator='Ctrl+O', compound='left',
                      image=open_file_icon, underline=0, command=open_file)
file_menu.add_command(label='Save', accelerator='Ctrl+S',
                      compound='left', image=save_file_icon, underline=0, command=save)
file_menu.add_command(
    label='Save as', accelerator='Shift+Ctrl+S', command=save_as)
file_menu.add_separator()
file_menu.add_command(label='Exit', accelerator='Alt+F4', command=exit_editor)
menu_bar.add_cascade(label='File', menu=file_menu)


edit_menu = Menu(menu_bar, tearoff=0)
edit_menu.add_command(label='Undo', accelerator='Ctrl+Z',
                      compound='left', image=undo_icon, command=undo)
edit_menu.add_command(label='Redo', accelerator='Ctrl+Y',
                      compound='left', image=redo_icon, command=redo)
edit_menu.add_separator()
edit_menu.add_command(label='Cut', accelerator='Ctrl+X',
                      compound='left', image=cut_icon, command=cut)
edit_menu.add_command(label='Copy', accelerator='Ctrl+C',
                      compound='left', image=copy_icon, command=copy)
edit_menu.add_command(label='Paste', accelerator='Ctrl+V',
                      compound='left', image=paste_icon, command=paste)
edit_menu.add_separator()
edit_menu.add_command(label='Find', underline=0,
                      accelerator='Ctrl+F', command=find_text)
edit_menu.add_separator()
edit_menu.add_command(label='Select All', underline=7,
                      accelerator='Ctrl+A', command=select_all)
menu_bar.add_cascade(label='Edit', menu=edit_menu)


view_menu = Menu(menu_bar, tearoff=0)
show_cursor_info = IntVar()
show_cursor_info.set(1)
view_menu.add_checkbutton(
    label='Show Cursor Location at Bottom', variable=show_cursor_info, command=show_cursor_info_bar)
to_highlight_line = BooleanVar()
view_menu.add_checkbutton(label='Highlight Current Line', onvalue=1,
                          offvalue=0, variable=to_highlight_line, command=toggle_highlight)
themes_menu = Menu(menu_bar, tearoff=0)
view_menu.add_cascade(label='Themes', menu=themes_menu)

color_schemes = {
    'Default': '#000000.#FFFFFF',
    'Greygarious': '#83406A.#D1D4D1',
    'Aquamarine': '#5B8340.#D1E7E0',
    'Bold Beige': '#4B4620.#FFF0E1',
    'Cobalt Blue': '#ffffBB.#3333aa',
    'Olive Green': '#D1E7E0.#5B8340',
    'Night Mode': '#FFFFFF.#000000',
}

theme_choice = StringVar()
theme_choice.set('Default')
for k in sorted(color_schemes):
    themes_menu.add_radiobutton(label=k, variable=theme_choice, command=change_theme)
menu_bar.add_cascade(label='View', menu=view_menu)


about_menu = Menu(menu_bar, tearoff=0)
about_menu.add_command(label='About', command=display_about_messagebox)
about_menu.add_command(label='Help', command=display_help_messagebox)
menu_bar.add_cascade(label='About',  menu=about_menu)
root.config(menu=menu_bar)

shortcut_bar = Frame(root, height=25, background='DeepSkyBlue2')
shortcut_bar.pack(expand='no', fill='x')

icons = ('new_file', 'open_file', 'save', 'cut', 'copy', 'paste',
         'undo', 'redo', 'find_text')
for i, icon in enumerate(icons):
    tool_bar_icon = PhotoImage(file='icons/{}.png'.format(icon))
    cmd = eval(icon)
    tool_bar = Button(shortcut_bar, image=tool_bar_icon, command=cmd)
    tool_bar.image = tool_bar_icon
    tool_bar.pack(side='left')


scroll_bar = Scrollbar(text_frame, command=content_text.yview, cursor='')
cursor_info_bar = Label(content_text, text='Line: 1 | Column: 1', highlightthickness=1, highlightbackground='black')
sel_info_bar = Label(content_text, text='From: 0 | To: 0', highlightthickness=1, highlightbackground='black')
scroll_bar.pack(side='right', fill='y')
text_frame.pack(expand='yes', fill='both')
content_text.pack(expand='yes', fill='both')
content_text.config(yscrollcommand=scroll_bar.set)
cursor_info_bar.pack(expand='no', fill=None, side='right', anchor='se')
sel_info_bar.pack(expand='no', fill=None, side='right', anchor='se', padx=5)

content_text.bind('<KeyPress-F1>', display_help_messagebox)
content_text.bind('<Control-N>', new_file)
content_text.bind('<Control-n>', new_file)
content_text.bind('<Control-O>', open_file)
content_text.bind('<Control-o>', open_file)
content_text.bind('<Control-S>', save)
content_text.bind('<Control-s>', save)
content_text.bind('<Control-f>', find_text)
content_text.bind('<Control-F>', find_text)
content_text.bind('<Control-A>', select_all)
content_text.bind('<Control-a>', select_all)
content_text.bind('<Control-y>', redo)
content_text.bind('<Control-Y>', redo)
content_text.bind('<Any-Key>', on_content_changed)
content_text.bind('<Any-KeyPress>', Spellcheck)


def sel():
    result = content_text.selection_get()
    sel_info_bar.config(text='Sel: {0} chars'.format(len(result)))
##    if result:
##        content_text.tag_remove("sel", "sel.first", "sel.last-1c")
##        content_text.tag_add("sel", "sel.first", "sel.last-1c")
##        content_text.bind(SEL, update_sel_info_bar)
    root.after(100, sel)


content_text.bind('<Button-1>', lambda x: content_text.after(50, sel))
for key in ['<Up>', '<Down>', '<Left>', '<Right>', '<Any-Key>', '<Button-1>', '<Button-2>', '<Button-3>']:
    content_text.bind(key, update_cursor_info_bar)

content_text.tag_configure('active_line', background='grey75')

# set up the pop-up menu
popup_menu = Menu(content_text, tearoff=0)
for i in ('cut', 'copy', 'paste', 'undo', 'redo'):
    cmd = eval(i)
    popup_menu.add_command(label=i, compound='left', command=cmd)
popup_menu.add_separator()
popup_menu.add_command(label='Select All', underline=7, command=select_all)
content_text.bind('<Button-3>', show_popup_menu)


# bind right mouse click to show pop up and set focus to text widget on launch
content_text.bind('<Button-3>', show_popup_menu)
content_text.focus_set()


def fullscreen_toggle(event):
    root.focus_set()
    root.overrideredirect(True)
    root.overrideredirect(False)
    root.attributes('-fullscreen', True)
    root.wm_attributes('-topmost', 1)


def fullscreen_cancel(event):
    root.overrideredirect(False)
    root.attributes('-fullscreen', False)
    root.wm_attributes('-topmost', 0)


if __name__ == '__main__':
    root.geometry('1200x620')
    root.title(PROGRAM_NAME)
    mechanise()
    binding_keys()
    root.bind('<F11>', fullscreen_toggle)
    root.bind('<Escape>', fullscreen_cancel)
    root.wm_state('zoomed')
    root.protocol('WM_DELETE_WINDOW', exit_editor)
    try:
        if sys.argv[1]:
            with open(sys.argv[1], 'r') as f:
                content_text.insert(END, f.read())
    except Exception:
        pass
    root.mainloop()


# MAYBE ADD A DICTIONARY MENU OPTION
