import tkinter as tk
from tkinter import messagebox, ttk
import requests

ADMIN_KEY = 'random_key'
BASE_URL = 'URL_TO_SERVER'  # Update this if your server runs on a different URL or port

class TorrentAdminApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Torrent Admin Panel")
        self.geometry("900x600")
        
        self.create_widgets()
        self.load_torrents()

    def create_widgets(self):
        # Create treeview to display torrents
        self.tree = ttk.Treeview(self, columns=("Name", "Info Hash", "Description", "Category", "Delete Key"), show='headings')
        self.tree.heading("Name", text="Name")
        self.tree.heading("Info Hash", text="Info Hash")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Delete Key", text="Delete Key")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Add buttons
        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X)

        self.start_button = tk.Button(button_frame, text="Start Opentracker", command=self.start_opentracker)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_button = tk.Button(button_frame, text="Stop Opentracker", command=self.stop_opentracker)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.reload_button = tk.Button(button_frame, text="Reload Opentracker", command=self.reload_opentracker)
        self.reload_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.remove_button = tk.Button(button_frame, text="Remove Selected Torrent", command=self.remove_selected_torrent)
        self.remove_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.update_button = tk.Button(button_frame, text="Update Selected Torrent", command=self.update_selected_torrent)
        self.update_button.pack(side=tk.LEFT, padx=5, pady=5)

    def load_torrents(self):
        self.tree.delete(*self.tree.get_children())
        response = requests.get(f"{BASE_URL}/admin-torrents", headers={'Admin-Key': ADMIN_KEY})
        if response.status_code == 200:
            torrents = response.json()
            for torrent in torrents:
                self.tree.insert("", tk.END, values=(torrent['name'], torrent['info_hash'], torrent['description'], ', '.join(torrent['category']), torrent['delete_key']))
        else:
            messagebox.showerror("Error", response.json().get('message', 'Failed to load torrents'))

    def start_opentracker(self):
        response = requests.post(f"{BASE_URL}/start", headers={'Admin-Key': ADMIN_KEY})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Opentracker started successfully.")
        else:
            messagebox.showerror("Error", response.json().get('message', 'Failed to start opentracker'))

    def stop_opentracker(self):
        response = requests.post(f"{BASE_URL}/stop", headers={'Admin-Key': ADMIN_KEY})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Opentracker stopped successfully.")
        else:
            messagebox.showerror("Error", response.json().get('message', 'Failed to stop opentracker'))

    def reload_opentracker(self):
        response = requests.post(f"{BASE_URL}/reload", headers={'Admin-Key': ADMIN_KEY})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Opentracker reloaded successfully.")
        else:
            messagebox.showerror("Error", response.json().get('message', 'Failed to reload opentracker'))

    def remove_selected_torrent(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No torrent selected")
            return

        info_hash = self.tree.item(selected_item, 'values')[1]
        delete_key = self.tree.item(selected_item, 'values')[4]

        response = requests.delete(f"{BASE_URL}/remove_torrent", json={'info_hash': info_hash, 'delete_key': delete_key})
        if response.status_code == 200:
            messagebox.showinfo("Success", response.json().get('message'))
            self.tree.delete(selected_item)
        else:
            messagebox.showerror("Error", response.json().get('message', 'Failed to remove torrent'))

    def update_selected_torrent(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No torrent selected")
            return

        info_hash = self.tree.item(selected_item, 'values')[1]
        name = self.tree.item(selected_item, 'values')[0]
        description = self.tree.item(selected_item, 'values')[2]
        category = self.tree.item(selected_item, 'values')[3]

        update_window = UpdateTorrentWindow(self, info_hash, name, description, category)
        self.wait_window(update_window)
        self.load_torrents()

class UpdateTorrentWindow(tk.Toplevel):
    def __init__(self, parent, info_hash, name, description, category):
        super().__init__(parent)
        self.info_hash = info_hash
        self.title("Update Torrent")
        self.geometry("400x300")

        self.create_widgets(name, description, category)

    def create_widgets(self, name, description, category):
        tk.Label(self, text="Name:").pack(pady=5)
        self.name_entry = tk.Entry(self)
        self.name_entry.insert(0, name)
        self.name_entry.pack(fill=tk.X, pady=5)

        tk.Label(self, text="Description:").pack(pady=5)
        self.description_entry = tk.Entry(self)
        self.description_entry.insert(0, description)
        self.description_entry.pack(fill=tk.X, pady=5)

        tk.Label(self, text="Category (comma separated):").pack(pady=5)
        self.category_entry = tk.Entry(self)
        self.category_entry.insert(0, category)
        self.category_entry.pack(fill=tk.X, pady=5)

        tk.Button(self, text="Update", command=self.update_torrent).pack(pady=10)

    def update_torrent(self):
        name = self.name_entry.get()
        description = self.description_entry.get()
        category = self.category_entry.get().split(',')

        data = {
            'info_hash': self.info_hash,
            'name': name,
            'description': description,
            'category': category
        }

        response = requests.post(f"{BASE_URL}/update_torrent", headers={'Admin-Key': ADMIN_KEY}, json=data)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Torrent updated successfully.")
            self.destroy()
        else:
            messagebox.showerror("Error", response.json().get('message', 'Failed to update torrent'))

if __name__ == '__main__':
    app = TorrentAdminApp()
    app.mainloop()
