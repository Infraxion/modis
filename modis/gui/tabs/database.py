import logging
import json
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox

from modis.tools import config, data

logger = logging.getLogger(__name__)


class Frame(ttk.Frame):
    """A tab containing controls for the data.json"""

    def __init__(self, parent):
        """Create the frame.

        Args:
            parent: A tk or ttk object.
        """

        super(Frame, self).__init__(parent, padding=8)

        # Add elements
        tree = self.DataTree(self)

        # Grid elements
        tree.grid(column=0, row=0, padx=8, pady=8, sticky="W E N S")

        # Configure stretch ratios
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    class DataTree(ttk.LabelFrame):
        """The database display"""

        def __init__(self, parent):
            """Create the tree.

            Args:
                parent: A tk or ttk object.
            """

            super(Frame.DataTree, self).__init__(parent, padding=8, text="Database tree")

            # Define variables
            self.datapath = tk.StringVar(value=config.DATAFILE)
            self.selected_key_var = tk.StringVar(value="Select a variable to edit")
            self.selected_val_var = tk.StringVar(value="")
            self.all_items = []
            self.selected_path = []

            # Add elements
            frame_path = ttk.Frame(self)
            datapath_label = ttk.Label(frame_path, text="Data file path:")
            datapath_entry = ttk.Entry(frame_path, textvariable=self.datapath, state="readonly")
            datapath_button = ttk.Button(frame_path, command=self.set_data_location, text="Change")

            frame_control = ttk.Frame(self)
            button_refresh = ttk.Button(frame_control, text="Refresh", command=self.tree_update)
            button_expand = ttk.Button(frame_control, text="Expand all", command=self.tree_expand)
            button_collapse = ttk.Button(frame_control, text="Collapse all", command=self.tree_collapse)

            frame_tree = ttk.Frame(self)
            self.tree = ttk.Treeview(frame_tree, columns="val")
            self.tree.bind("<<TreeviewSelect>>", self.tree_select)
            self.tree.column("#0", width=50)
            self.tree.heading("#0", text="Key")
            self.tree.heading("val", text="Value")
            self.tree_update()
            yscrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
            xscrollbar = ttk.Scrollbar(frame_tree, orient="horizontal", command=self.tree.xview)
            self.tree['yscrollcommand'] = yscrollbar.set
            self.tree['xscrollcommand'] = xscrollbar.set

            frame_edit = ttk.Frame(self)
            label_key = ttk.Label(frame_edit, text="Selected key:")
            label_val = ttk.Label(frame_edit, text="Change to:")
            selected_key = ttk.Entry(frame_edit, textvariable=self.selected_key_var, state="readonly")
            selected_val = ttk.Entry(frame_edit, textvariable=self.selected_val_var)
            self.selected_enter = ttk.Button(frame_edit, text="Enter", command=self.tree_edit, state="disabled")

            # Grid elements
            datapath_label.grid(column=0, row=0, padx=4, pady=4, stick="E")
            datapath_entry.grid(column=1, row=0, padx=4, pady=4, sticky="W E")
            datapath_button.grid(column=2, row=0, padx=4, pady=4, sticky="E")

            button_refresh.grid(column=0, row=0, padx=4, pady=4, sticky="W")
            button_expand.grid(column=1, row=0, padx=4, pady=4, sticky="W")
            button_collapse.grid(column=2, row=0, padx=4, pady=4, sticky="W")

            self.tree.grid(column=0, row=0, sticky="W E N S")
            yscrollbar.grid(column=1, row=0, sticky="N S")
            xscrollbar.grid(column=0, row=1, sticky="W E")

            label_key.grid(column=0, row=0, padx=4, pady=4, sticky="E")
            selected_key.grid(column=1, columnspan=2, row=0, padx=4, pady=4, sticky="W E")
            label_val.grid(column=0, row=1, padx=4, pady=4, sticky="E")
            selected_val.grid(column=1, row=1, padx=4, pady=4, sticky="W E")
            self.selected_enter.grid(column=2, row=1, padx=4, pady=4, sticky="E")

            frame_path.grid(column=0, row=0, sticky="W E N S")
            frame_control.grid(column=0, row=1, sticky="W E N S")
            frame_tree.grid(column=0, row=2, sticky="W E N S")
            frame_edit.grid(column=0, row=3, sticky="W E N S")

            # Configure stretch ratios
            self.columnconfigure(0, weight=1)
            self.rowconfigure(0, weight=0)
            self.rowconfigure(1, weight=0)
            self.rowconfigure(2, weight=1)
            self.rowconfigure(3, weight=0)

            frame_path.columnconfigure(0, weight=0)
            frame_path.columnconfigure(1, weight=1)
            frame_path.columnconfigure(2, weight=0)
            frame_path.rowconfigure(0, weight=0)

            frame_control.columnconfigure(0, weight=0)
            frame_control.rowconfigure(0, weight=0)
            frame_control.rowconfigure(1, weight=0)
            frame_control.rowconfigure(2, weight=0)

            frame_tree.columnconfigure(0, weight=1)
            frame_tree.columnconfigure(1, weight=0)
            frame_tree.rowconfigure(0, weight=1)
            frame_tree.rowconfigure(1, weight=0)

            frame_edit.columnconfigure(0, weight=0)
            frame_edit.columnconfigure(1, weight=1)
            frame_edit.columnconfigure(2, weight=0)
            frame_edit.rowconfigure(0, weight=0)
            frame_edit.rowconfigure(0, weight=0)

        def tree_update(self):
            for item in self.all_items:
                try:
                    self.tree.delete(item)
                except tk.TclError:
                    pass
            self.all_items = []

            from modis.tools import data

            def recursive_add(entry, parent=""):
                for key in entry:
                    if type(entry[key]) is dict:
                        new_item = self.tree.insert(parent, "end", text=key)
                        self.all_items.append(new_item)
                        recursive_add(entry[key], new_item)
                    else:
                        new_item = self.tree.insert(parent, "end", text=key, values=str(entry[key]))
                        self.all_items.append(new_item)

            recursive_add(data.cache)

        def tree_expand(self):
            for item in self.all_items:
                self.tree.item(item, open=True)

        def tree_collapse(self):
            for item in self.all_items:
                self.tree.item(item, open=False)

        def tree_select(self, event):
            selected = self.tree.focus()
            self.selected_key_var.set(self.tree.item(selected)["text"])

            if self.tree.item(selected)["values"]:
                self.selected_val_var.set(self.tree.item(selected)["values"][0])
                self.selected_enter.config(state="enabled")
            elif not self.tree.get_children(selected):
                self.selected_val_var.set("")
                self.selected_enter.config(state="enabled")
            else:
                self.selected_val_var.set("")
                self.selected_enter.config(state="disabled")

            self.selected_path = []

            def recursive_get(item):
                parent_item = self.tree.parent(item)
                parent_name = self.tree.item(parent_item)["text"]
                self.selected_path.insert(0, self.tree.item(item)["text"])
                if parent_name:
                    recursive_get(parent_item)

            recursive_get(selected)
            self.selected_key_var.set(".".join(self.selected_path))

        def tree_edit(self):
            if not messagebox.askokcancel(title="Edit value", message="Set {} to:\n{}".format(self.selected_key_var.get(), self.selected_val_var.get())):
                # User cancelled value edit
                messagebox.showinfo(title="Edit value", message="Value not changed.")
                return

            from modis.tools import data

            pathstr = ""
            for item in self.selected_path:
                pathstr += """["{}"]""".format(item)

            logger.warning("Updating {} to {}".format(self.selected_key_var.get(), self.selected_val_var.get()))
            exec("data.cache{} = self.selected_val_var.get()".format(pathstr))

            data.push()
            self.tree_update()
            messagebox.showinfo(title="Edit value", message="Edit successful.")

        def set_data_location(self):
            newpath = filedialog.askopenfile()
            oldpath = config.DATAFILE

            try:
                newpath = newpath.name
            except AttributeError:
                # Window was closed
                logger.warning("Data file not changed")
                return

            if not messagebox.askokcancel(title="Change data file path", message="Change data file to:\n{}".format(newpath)):
                # User cancelled path change
                messagebox.showinfo(title="Change data file path", message="Data file not changed.")
                return

            # Change the path
            config.DATAFILE = newpath

            try:
                data.pull()
            except json.decoder.JSONDecodeError:
                # Chosen file invalid
                logger.error("Chosen file is not a valid json; reverting changes")
                messagebox.showerror(title="Change data file path", message="Chosen file is not a valid json.")

                # Try again
                config.DATAFILE = oldpath
                data.pull()
                self.set_data_location()
                return

            # Successful change
            self.datapath.set(newpath)
            self.tree_update()
            logger.warning("data file changed to " + config.DATAFILE)
            messagebox.showinfo(title="Change data file path", message="Data file change successful.")
