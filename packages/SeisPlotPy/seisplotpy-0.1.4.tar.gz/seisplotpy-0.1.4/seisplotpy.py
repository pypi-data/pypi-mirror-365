# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 12:09:24 2025

@author: Admin
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import segyio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import threading
import time
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SeismicViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SeisPlotPy")
        self.root.geometry("1200x800")
        try:
            self.root.iconbitmap(resource_path('seisplotpy.ico'))
        except:
            pass  # If icon not found, use default

        self.segy_data = None
        self.cdp_all = None
        self.twt_all = None
        self.header_data = {}
        self.file_path = None
        self.horizon_widgets = []
        self.horizon_data = []
        self.fig = None
        self.ax = None
        self.canvas = None
        
        # Loading status variables
        self.loading_active = False
        self.loading_thread = None
        self.status_timer = None
        self.dot_count = 0

        # --- Top Control Panel ---
        self.control_frame = ttk.Frame(self.root, padding=10)
        self.control_frame.pack(fill=tk.X)

        # Select SEG-Y button
        self.select_button = ttk.Button(self.control_frame, text="Select SEG-Y File", command=self.load_segy_file)
        self.select_button.grid(row=0, column=0, padx=5)

        # CDP min/max display
        ttk.Label(self.control_frame, text="X Range:").grid(row=0, column=1, padx=5)
        self.cdp_min_var = tk.StringVar()
        self.cdp_max_var = tk.StringVar()
        self.cdp_min_entry = ttk.Entry(self.control_frame, width=10, textvariable=self.cdp_min_var, state='disabled')
        self.cdp_max_entry = ttk.Entry(self.control_frame, width=10, textvariable=self.cdp_max_var, state='disabled')
        self.cdp_min_entry.grid(row=0, column=2)
        self.cdp_max_entry.grid(row=0, column=3)

        # TWT/Depth min/max display
        ttk.Label(self.control_frame, text="TWT/Depth Range:").grid(row=0, column=4, padx=5)
        self.twt_min_var = tk.StringVar()
        self.twt_max_var = tk.StringVar()
        self.twt_min_entry = ttk.Entry(self.control_frame, width=10, textvariable=self.twt_min_var, state='disabled')
        self.twt_max_entry = ttk.Entry(self.control_frame, width=10, textvariable=self.twt_max_var, state='disabled')
        self.twt_min_entry.grid(row=0, column=5)
        self.twt_max_entry.grid(row=0, column=6)

        # CDP Header Dropdown
        ttk.Label(self.control_frame, text="Select X-axis Header:").grid(row=0, column=7, padx=5)
        self.cdp_header_var = tk.StringVar()
        self.cdp_header_dropdown = ttk.Combobox(self.control_frame, textvariable=self.cdp_header_var, state='readonly', width=20)
        self.cdp_header_dropdown.grid(row=0, column=8)
        self.cdp_header_dropdown.bind("<<ComboboxSelected>>", self.update_cdp_range)

        # Colormap selection
        self.cmap_var = tk.StringVar(value="seismic")  # Default cmap
        ttk.Label(self.control_frame, text="Colormap:").grid(row=0, column=9, padx=5, pady=5)
        self.cmap_dropdown = ttk.Combobox(self.control_frame, textvariable=self.cmap_var, state='readonly', width=15, 
                                         values=["gray", "gray_r", "Grays", "Grays_r", "seismic", "seismic_r", 
                                                 "bwr", "bwr_r", "binary", "binary_r", "RdBu", "RdBu_r", 
                                                 "RdGy", "RdGy_r", "coolwarm", "coolwarm_r", "PuOr", "PuOr_r", 
                                                 "PiYG", "PiYG_r", "PRGn", "PRGn_r", "BrBG", "BrBG_r"])
        self.cmap_dropdown.grid(row=0, column=10, padx=5, pady=5)

        # --- Second Row for Additional Controls ---
        # Time/Depth Domain Dropdown
        ttk.Label(self.control_frame, text="Domain:").grid(row=1, column=0, padx=5, pady=5)
        self.domain_var = tk.StringVar(value="Time")
        self.domain_dropdown = ttk.Combobox(self.control_frame, textvariable=self.domain_var, state='readonly', width=10, values=["Time", "Depth"])
        self.domain_dropdown.grid(row=1, column=1)

        # vmin/vmax Entry
        ttk.Label(self.control_frame, text="Amplitude (min, max):").grid(row=1, column=2, padx=5)
        self.vmin_var = tk.StringVar(value="-0.3")
        self.vmax_var = tk.StringVar(value="0.3")
        self.vmin_entry = ttk.Entry(self.control_frame, width=10, textvariable=self.vmin_var)
        self.vmin_entry.grid(row=1, column=3)
        self.vmax_entry = ttk.Entry(self.control_frame, width=10, textvariable=self.vmax_var)
        self.vmax_entry.grid(row=1, column=4)

        # X-axis Position Dropdown
        ttk.Label(self.control_frame, text="X Axis Position:").grid(row=1, column=5, padx=5)
        self.axis_pos_var = tk.StringVar(value="Top")
        self.axis_pos_dropdown = ttk.Combobox(self.control_frame, textvariable=self.axis_pos_var, state='readonly', width=10, values=["Top", "Bottom"])
        self.axis_pos_dropdown.grid(row=1, column=6)

        # Grid Toggle Checkbox
        self.grid_var = tk.BooleanVar(value=True)
        self.grid_check = ttk.Checkbutton(self.control_frame, text="Show Grid", variable=self.grid_var)
        self.grid_check.grid(row=1, column=7, padx=5)

        # X-axis Flip Checkbox
        self.flip_x_var = tk.BooleanVar(value=False)
        self.flip_x_check = ttk.Checkbutton(self.control_frame, text="Flip X-Axis", variable=self.flip_x_var)
        self.flip_x_check.grid(row=1, column=8, padx=5)

        # --- Third Row for Figure Size Controls ---
        # Figure size (width, height) Entry for aspect ratio
        ttk.Label(self.control_frame, text="Figure Aspect Ratio (width, height):").grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        self.fig_width_var = tk.StringVar(value="20")
        self.fig_height_var = tk.StringVar(value="9")
        self.fig_width_entry = ttk.Entry(self.control_frame, width=10, textvariable=self.fig_width_var)
        self.fig_height_entry = ttk.Entry(self.control_frame, width=10, textvariable=self.fig_height_var)
        self.fig_width_entry.grid(row=2, column=2)
        self.fig_height_entry.grid(row=2, column=3)

        # Apply Button
        self.apply_button = ttk.Button(self.control_frame, text="Apply", command=self.apply_changes)
        self.apply_button.grid(row=2, column=10, padx=5)

        # --- Fourth Row for Export Controls ---
        # Export Format Dropdown
        ttk.Label(self.control_frame, text="Export Format:").grid(row=3, column=0, padx=5)
        self.format_var = tk.StringVar(value="PNG")
        self.format_dropdown = ttk.Combobox(self.control_frame, textvariable=self.format_var, state='readonly', width=10, values=["PNG", "JPEG", "TIFF", "PDF"])
        self.format_dropdown.grid(row=3, column=1)

        # DPI Entry
        ttk.Label(self.control_frame, text="DPI:").grid(row=3, column=2, padx=5)
        self.dpi_var = tk.StringVar(value="300")
        self.dpi_entry = ttk.Entry(self.control_frame, width=10, textvariable=self.dpi_var)
        self.dpi_entry.grid(row=3, column=3)

        # Export Button
        self.export_button = ttk.Button(self.control_frame, text="Export", command=self.export_figure, state='disabled')
        self.export_button.grid(row=3, column=4, padx=5)

        # --- Horizon Controls Frame ---
        self.horizon_frame = ttk.Frame(self.root, padding=10)
        self.horizon_frame.pack(fill=tk.X)

        # Number of Horizons Entry
        ttk.Label(self.horizon_frame, text="Number of Horizons:").grid(row=0, column=0, padx=5, pady=5)
        self.num_horizons_var = tk.StringVar(value="0")
        self.num_horizons_entry = ttk.Entry(self.horizon_frame, width=5, textvariable=self.num_horizons_var)
        self.num_horizons_entry.grid(row=0, column=1)
        self.num_horizons_entry.bind("<Return>", self.update_horizon_controls_wrapper)
        self.num_horizons_entry.bind("<FocusOut>", self.update_horizon_controls_wrapper)

        # Frame for dynamic horizon controls
        self.horizon_controls_frame = ttk.Frame(self.horizon_frame)
        self.horizon_controls_frame.grid(row=1, column=0, columnspan=10, sticky='w')

        # --- Scrollable Matplotlib Canvas for Seismic Display ---
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas_widget = tk.Canvas(self.canvas_frame, bg='white')
        self.scrollable_frame = ttk.Frame(self.canvas_widget)
        self.scrollbar_v = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas_widget.yview)
        self.scrollbar_h = ttk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas_widget.xview)
        self.canvas_widget.configure(yscrollcommand=self.scrollbar_v.set, xscrollcommand=self.scrollbar_h.set)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas_widget.configure(scrollregion=self.canvas_widget.bbox("all")))
        self.canvas_widget.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Status Bar ---
        self.status_label = ttk.Label(self.root, text="Welcome!", relief=tk.SUNKEN, anchor='w')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Available colors and line styles for horizons
        self.color_options = ['red', 'blue', 'green', 'black', 'purple', 'orange', 'brown', 'cyan', 'magenta']
        self.line_style_options = ['solid', 'dashed', 'dotted', 'dashdot']

    def start_loading_animation(self, base_message, show_patience_after=30):
        """Start the loading animation with blinking dots."""
        self.loading_active = True
        self.dot_count = 0
        self.loading_start_time = time.time()
        self.base_message = base_message
        self.show_patience_after = show_patience_after
        self.update_loading_message()

    def stop_loading_animation(self):
        """Stop the loading animation."""
        self.loading_active = False
        if self.status_timer:
            self.root.after_cancel(self.status_timer)
            self.status_timer = None

    def update_loading_message(self):
        """Update the loading message with animated dots."""
        if not self.loading_active:
            return

        # Check if we need to show patience message
        elapsed_time = time.time() - self.loading_start_time
        if elapsed_time >= self.show_patience_after:
            current_message = "This may take some time, please be patient"
        else:
            current_message = self.base_message

        # Add dots
        dots = "." * (self.dot_count + 1)
        self.status_label.config(text=f"{current_message}{dots}")
        
        # Update dot count (cycle through 0, 1, 2, 3)
        self.dot_count = (self.dot_count + 1) % 4
        
        # Schedule next update (change 500 to your desired milliseconds)
        if self.loading_active:
            self.status_timer = self.root.after(500, self.update_loading_message)

    def load_segy_file(self):
        """Load SEG-Y file with loading animation."""
        # Start loading animation immediately
        self.start_loading_animation("Loading data, please wait", show_patience_after=30)
        
        # Disable the button during loading
        self.select_button.config(state='disabled')
        
        file_path = filedialog.askopenfilename(title="Select SEG-Y File", filetypes=[("SEG-Y files", "*.sgy *.segy")])
        if not file_path:
            # Stop animation and re-enable button if user cancels
            self.stop_loading_animation()
            self.select_button.config(state='normal')
            self.status_label.config(text="File selection cancelled.")
            return
        
        self.file_path = file_path
        
        # Start loading in a separate thread
        self.loading_thread = threading.Thread(target=self._load_segy_worker, args=(file_path,))
        self.loading_thread.daemon = True
        self.loading_thread.start()

    def _load_segy_worker(self, file_path):
        """Worker thread for loading SEG-Y file."""
        try:
            with segyio.open(file_path, ignore_geometry=True) as f:
                self.twt_all = f.samples
                self.segy_data = f.trace.raw[:]
                self.header_data = {}
                self.trace_count = f.tracecount

                for key, val in segyio.tracefield.keys.items():
                    try:
                        self.header_data[key] = f.attributes(val)[:]
                    except Exception:
                        continue

            # Update UI in main thread
            self.root.after(0, self._load_segy_complete, file_path)
            
        except Exception as e:
            # Handle error in main thread
            self.root.after(0, self._load_segy_error, str(e))

    def _load_segy_complete(self, file_path):
        """Complete the SEG-Y loading process in the main thread."""
        try:
            # Stop loading animation
            self.stop_loading_animation()
            
            self.populate_trace_headers()
            self.status_label.config(text=f"Loaded SEG-Y file: {os.path.basename(file_path)} — Select CDP header")

            # Set TWT range (fixed)
            self.twt_min_var.set(str(np.min(self.twt_all)))
            self.twt_max_var.set(str(np.max(self.twt_all)))

            # Enable range entries for editing
            self.cdp_min_entry.config(state='normal')
            self.cdp_max_entry.config(state='normal')
            self.twt_min_entry.config(state='normal')
            self.twt_max_entry.config(state='normal')

            # Initialize figure and canvas with aspect ratio
            try:
                fig_width = float(self.fig_width_var.get())
                fig_height = float(self.fig_height_var.get())
                if fig_width <= 0 or fig_height <= 0:
                    raise ValueError("Figure size must be positive.")
                aspect_ratio = fig_width / fig_height
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid positive numbers for figure aspect ratio.")
                return

            self.fig = plt.Figure(figsize=(10, 10 / aspect_ratio))
            self.ax = self.fig.add_subplot(111)
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.scrollable_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Bind resize event to maintain aspect ratio
            self.root.bind('<Configure>', self.on_resize)

            # Enable export button
            self.export_button.config(state='normal')

            # Plot the seismic data
            self.plot_seismic()

        except Exception as e:
            self._load_segy_error(str(e))
        finally:
            # Re-enable the button
            self.select_button.config(state='normal')

    def _load_segy_error(self, error_message):
        """Handle SEG-Y loading error in the main thread."""
        # Stop loading animation
        self.stop_loading_animation()
        
        # Re-enable the button
        self.select_button.config(state='normal')
        
        # Show error
        messagebox.showerror("Error", f"Failed to load SEG-Y: {error_message}")
        self.status_label.config(text="Error loading SEG-Y file.")

    def apply_changes(self):
        """Apply changes with loading animation."""
        if self.segy_data is None:
            messagebox.showwarning("Warning", "Please load a SEG-Y file first.")
            return
        
        # Start loading animation
        self.start_loading_animation("Applying changes", show_patience_after=999999)  # No patience message for apply
        
        # Disable the button during processing
        self.apply_button.config(state='disabled')
        
        # Start processing in a separate thread
        self.loading_thread = threading.Thread(target=self._apply_changes_worker)
        self.loading_thread.daemon = True
        self.loading_thread.start()

    def _apply_changes_worker(self):
        """Worker thread for applying changes."""
        try:
            # Simulate the plotting work (this runs in background)
            time.sleep(0.1)  # Small delay to show the animation
            
            # Update UI in main thread
            self.root.after(0, self._apply_changes_complete)
            
        except Exception as e:
            # Handle error in main thread
            self.root.after(0, self._apply_changes_error, str(e))

    def _apply_changes_complete(self):
        """Complete the apply changes process in the main thread."""
        try:
            # Stop loading animation
            self.stop_loading_animation()
            
            # Actually plot the seismic data
            self.plot_seismic()
            
            # Update status
            filename = os.path.basename(self.file_path) if self.file_path else "data"
            self.status_label.config(text=f"Applied changes to: {filename}")
            
        except Exception as e:
            self._apply_changes_error(str(e))
        finally:
            # Re-enable the button
            self.apply_button.config(state='normal')

    def _apply_changes_error(self, error_message):
        """Handle apply changes error in the main thread."""
        # Stop loading animation
        self.stop_loading_animation()
        
        # Re-enable the button
        self.apply_button.config(state='normal')
        
        # Show error
        messagebox.showerror("Error", f"Failed to apply changes: {error_message}")
        self.status_label.config(text="Error applying changes.")

    def update_horizon_controls_wrapper(self, event=None):
        """Wrapper for horizon controls update with loading animation."""
        # Start loading animation
        self.start_loading_animation("Applying changes", show_patience_after=999999)  # No patience message
        
        # Start processing in a separate thread
        self.loading_thread = threading.Thread(target=self._update_horizon_controls_worker)
        self.loading_thread.daemon = True
        self.loading_thread.start()

    def _update_horizon_controls_worker(self):
        """Worker thread for updating horizon controls."""
        try:
            # Longer delay to show "Applying changes..." message
            time.sleep(0.5)
            
            # Update UI in main thread
            self.root.after(0, self._update_horizon_controls_complete)
            
        except Exception as e:
            # Handle error in main thread
            self.root.after(0, self._update_horizon_controls_error, str(e))

    def _update_horizon_controls_complete(self):
        """Complete the horizon controls update in the main thread."""
        try:
            # Actually update the horizon controls first
            self.update_horizon_controls()
            
            # Stop loading animation
            self.stop_loading_animation()
            
            # Show completion message after a brief delay to see the controls appear
            self.root.after(500, lambda: self.status_label.config(text="Horizon controls updated."))
            
        except Exception as e:
            self._update_horizon_controls_error(str(e))

    def _update_horizon_controls_error(self, error_message):
        """Handle horizon controls update error in the main thread."""
        # Stop loading animation
        self.stop_loading_animation()
        
        # Show error
        messagebox.showerror("Error", f"Failed to update horizon controls: {error_message}")
        self.status_label.config(text="Error updating horizon controls.")

    def update_horizon_controls(self, event=None):
        """Update the horizon control widgets based on the number of horizons."""
        try:
            num_horizons = int(self.num_horizons_var.get())
            if num_horizons < 0:
                raise ValueError("Number of horizons cannot be negative.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid non-negative integer for number of horizons.")
            return

        # Clear existing horizon widgets and data
        for widget_tuple in self.horizon_widgets:
            for widget in widget_tuple:
                try:
                    widget.destroy()
                except:
                    pass  # Ignore errors if widget is already destroyed
        self.horizon_widgets = []
        self.horizon_data = []

        # Create controls for each horizon
        for i in range(num_horizons):
            # Horizon file selection
            ttk.Label(self.horizon_controls_frame, text=f"Horizon {i+1} File:").grid(row=i, column=0, padx=5, pady=2)
            file_var = tk.StringVar()
            file_button = ttk.Button(self.horizon_controls_frame, text="Select", command=lambda var=file_var: self.select_horizon_file(var))
            file_button.grid(row=i, column=1)
            file_entry = ttk.Entry(self.horizon_controls_frame, width=20, textvariable=file_var, state='readonly')
            file_entry.grid(row=i, column=2)

            # Color selection
            ttk.Label(self.horizon_controls_frame, text="Color:").grid(row=i, column=3, padx=5)
            color_var = tk.StringVar(value=self.color_options[0])
            color_dropdown = ttk.Combobox(self.horizon_controls_frame, textvariable=color_var, state='readonly', width=10, values=self.color_options)
            color_dropdown.grid(row=i, column=4)
            color_canvas = tk.Canvas(self.horizon_controls_frame, width=20, height=20, bg=self.color_options[0])
            color_canvas.grid(row=i, column=5)
            color_dropdown.bind("<<ComboboxSelected>>", lambda e, cv=color_canvas, var=color_var: self.update_color_swatch(cv, var))

            # Line style selection
            ttk.Label(self.horizon_controls_frame, text="Style:").grid(row=i, column=6, padx=5)
            style_var = tk.StringVar(value=self.line_style_options[0])
            style_dropdown = ttk.Combobox(self.horizon_controls_frame, textvariable=style_var, state='readonly', width=10, values=self.line_style_options)
            style_dropdown.grid(row=i, column=7)

            # Line thickness entry
            ttk.Label(self.horizon_controls_frame, text="Thickness:").grid(row=i, column=8, padx=5)
            thickness_var = tk.StringVar(value="1.0")
            thickness_entry = ttk.Entry(self.horizon_controls_frame, width=5, textvariable=thickness_var)
            thickness_entry.grid(row=i, column=9)

            # Store widget references and initial data
            self.horizon_widgets.append((file_button, file_entry, color_dropdown, color_canvas, style_dropdown, thickness_entry))
            self.horizon_data.append({'file': file_var, 'color': color_var, 'style': style_var, 'thickness': thickness_var})

    def select_horizon_file(self, file_var):
        """Open a file dialog to select a horizon CSV file."""
        file_path = filedialog.askopenfilename(title="Select Horizon File", filetypes=[("CSV files", "*.csv")])
        if file_path:
            file_var.set(os.path.basename(file_path))
            file_var.path = file_path

    def update_color_swatch(self, canvas, color_var):
        """Update the color swatch canvas when a color is selected."""
        canvas.config(bg=color_var.get())

    def populate_trace_headers(self):
        header_list = list(self.header_data.keys())
        self.cdp_header_dropdown['values'] = header_list
        if 'CDP' in header_list:
            self.cdp_header_var.set('CDP')
            self.update_cdp_range()
        else:
            self.cdp_header_var.set('')

    def update_cdp_range(self, event=None):
        selected_key = self.cdp_header_var.get()
        if not selected_key:
            return

        try:
            self.cdp_all = np.array(self.header_data[selected_key])
            self.cdp_min_var.set(str(np.min(self.cdp_all)))
            self.cdp_max_var.set(str(np.max(self.cdp_all)))
        except Exception as e:
            messagebox.showerror("Header Error", f"Failed to extract CDP values from '{selected_key}': {e}")

    def on_resize(self, event):
        """Handle window resize to maintain aspect ratio."""
        if self.fig and self.canvas:
            try:
                fig_width = float(self.fig_width_var.get())
                fig_height = float(self.fig_height_var.get())
                aspect_ratio = fig_width / fig_height
                self.fig.set_size_inches(10, 10 / aspect_ratio)
                self.canvas.draw()
                self.canvas_widget.configure(scrollregion=self.canvas_widget.bbox("all"))
            except ValueError:
                pass  # Ignore invalid values during resize

    def plot_seismic(self):
        """Plot the loaded SEG-Y data and horizons in the matplotlib canvas."""
        if self.segy_data is None or self.cdp_all is None or self.twt_all is None or self.fig is None or self.ax is None:
            return

        # Get figure size for aspect ratio
        try:
            fig_width = float(self.fig_width_var.get())
            fig_height = float(self.fig_height_var.get())
            if fig_width <= 0 or fig_height <= 0:
                raise ValueError("Figure size must be positive.")
            aspect_ratio = fig_width / fig_height
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid positive numbers for figure aspect ratio.")
            return

        # Recreate figure and canvas with new aspect ratio
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.fig = plt.Figure(figsize=(10, 10 / aspect_ratio))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.scrollable_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Get user-defined ranges
        try:
            cdp_min = float(self.cdp_min_var.get())
            cdp_max = float(self.cdp_max_var.get())
            twt_min = float(self.twt_min_var.get())
            twt_max = float(self.twt_max_var.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for CDP and TWT/Depth ranges.")
            return

        # Filter data based on ranges
        cdp_mask = (self.cdp_all >= cdp_min) & (self.cdp_all <= cdp_max)
        twt_mask = (self.twt_all >= twt_min) & (self.twt_all <= twt_max)
        data_filtered = self.segy_data[cdp_mask, :][:, twt_mask]
        cdp_filtered = self.cdp_all[cdp_mask]
        twt_filtered = self.twt_all[twt_mask]

        # Get vmin/vmax for amplitude clipping
        try:
            vmin = float(self.vmin_var.get()) * np.percentile(data_filtered, 99.9)
            vmax = float(self.vmax_var.get()) * np.percentile(data_filtered, 99.9)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for vmin and vmax.")
            return

        # Plot seismic data with interpolation
        im = self.ax.imshow(
            data_filtered.T,
            cmap=self.cmap_var.get(),  # Use selected cmap
            aspect="auto",
            extent=[cdp_filtered[0], cdp_filtered[-1], twt_filtered[-1], twt_filtered[0]],
            vmin=vmin,
            vmax=vmax,
            interpolation='bilinear'
        )

        # Plot horizons
        for horizon in self.horizon_data:
            if hasattr(horizon['file'], 'path'):
                try:
                    df = pd.read_csv(horizon['file'].path, header=None, skiprows=1, usecols=[0, 1])
                    cdp = df[0].values
                    y_val = df[1].values
                    mask = (cdp >= cdp_min) & (cdp <= cdp_max) & (y_val >= twt_min) & (y_val <= twt_max)
                    if np.any(mask):
                        thickness = float(horizon['thickness'].get())
                        self.ax.plot(cdp[mask], y_val[mask], color=horizon['color'].get(), linestyle=horizon['style'].get(), linewidth=thickness)
                except Exception as e:
                    messagebox.showerror("Horizon Error", f"Failed to load or plot horizon: {str(e)}")

        # Set y-axis label based on domain
        domain = self.domain_var.get()
        self.ax.set_ylabel("TWT (ms)" if domain == "Time" else "Depth (m)", fontsize=12)

        # Set x-axis position (top or bottom)
        axis_pos = self.axis_pos_var.get()
        if axis_pos == "Top":
            self.ax.set_xticklabels([])
            self.ax.set_xlabel("")
            ax_top = self.ax.twiny()
            ax_top.set_xlim(self.ax.get_xlim())
            ax_top.set_xlabel("CDP", fontsize=12)
        else:
            self.ax.set_xlabel("CDP", fontsize=12)

        # Flip x-axis if requested
        if self.flip_x_var.get():
            self.ax.invert_xaxis()
            if axis_pos == "Top":
                ax_top.invert_xaxis()

        # Toggle grid
        if self.grid_var.get():
            self.ax.grid(True, linestyle='--', linewidth=0.3)
        else:
            self.ax.grid(False)

        # Redraw the canvas and update scroll region
        self.canvas.draw()
        self.canvas_widget.configure(scrollregion=self.canvas_widget.bbox("all"))

    def export_figure(self):
        """Export the current figure with the specified format and DPI."""
        if self.fig is None:
            messagebox.showerror("Error", "No figure to export. Please load a SEG-Y file first.")
            return

        # Get figure size in inches
        try:
            fig_width = float(self.fig_width_var.get())
            fig_height = float(self.fig_height_var.get())
            if fig_width <= 0 or fig_height <= 0:
                raise ValueError("Figure size must be positive.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid positive numbers for figure aspect ratio.")
            return

        # Get DPI
        try:
            dpi = int(self.dpi_var.get())
            if dpi <= 0:
                raise ValueError("DPI must be positive.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid positive number for DPI.")
            return

        # Determine file extension and format
        format_map = {"PNG": ".png", "JPEG": ".jpg", "TIFF": ".tif", "PDF": ".pdf"}
        export_format = self.format_var.get()
        if export_format not in format_map:
            messagebox.showerror("Error", "Invalid export format.")
            return

        # Set default file name and directory
        default_dir = os.path.dirname(self.file_path) if self.file_path else ""
        default_name = os.path.splitext(os.path.basename(self.file_path or "seismic_plot"))[0] + format_map[export_format]
        file_path = filedialog.asksaveasfilename(
            title="Save Figure",
            defaultextension=format_map[export_format],
            filetypes=[(f"{export_format} files", f"*{format_map[export_format]}")],
            initialdir=default_dir,
            initialfile=default_name
        )
        if not file_path:
            return  # User cancelled

        # Create a new figure with the specified size in inches for export
        export_fig = plt.Figure(figsize=(fig_width, fig_height))
        export_ax = export_fig.add_subplot(111)

        # Replot data for export
        cdp_min = float(self.cdp_min_var.get())
        cdp_max = float(self.cdp_max_var.get())
        twt_min = float(self.twt_min_var.get())
        twt_max = float(self.twt_max_var.get())
        cdp_mask = (self.cdp_all >= cdp_min) & (self.cdp_all <= cdp_max)
        twt_mask = (self.twt_all >= twt_min) & (self.twt_all <= twt_max)
        data_filtered = self.segy_data[cdp_mask, :][:, twt_mask]
        cdp_filtered = self.cdp_all[cdp_mask]
        twt_filtered = self.twt_all[twt_mask]
        vmin = float(self.vmin_var.get()) * np.percentile(data_filtered, 99.9)
        vmax = float(self.vmax_var.get()) * np.percentile(data_filtered, 99.9)

        im = export_ax.imshow(
            data_filtered.T,
            cmap=self.cmap_var.get(),  # Use selected cmap
            aspect="auto",
            extent=[cdp_filtered[0], cdp_filtered[-1], twt_filtered[-1], twt_filtered[0]],
            vmin=vmin,
            vmax=vmax,
            interpolation='bilinear'
        )

        # Replot horizons
        for horizon in self.horizon_data:
            if hasattr(horizon['file'], 'path'):
                try:
                    df = pd.read_csv(horizon['file'].path, header=None, skiprows=1, usecols=[0, 1])
                    cdp = df[0].values
                    y_val = df[1].values
                    mask = (cdp >= cdp_min) & (cdp <= cdp_max) & (y_val >= twt_min) & (y_val <= twt_max)
                    if np.any(mask):
                        thickness = float(horizon['thickness'].get())
                        export_ax.plot(cdp[mask], y_val[mask], color=horizon['color'].get(), linestyle=horizon['style'].get(), linewidth=thickness)
                except Exception as e:
                    messagebox.showerror("Horizon Error", f"Failed to load or plot horizon for export: {str(e)}")

        # Set labels and styles
        domain = self.domain_var.get()
        export_ax.set_ylabel("TWT (ms)" if domain == "Time" else "Depth (m)", fontsize=12)
        axis_pos = self.axis_pos_var.get()
        if axis_pos == "Top":
            export_ax.set_xticklabels([])
            export_ax.set_xlabel("")
            ax_top = export_ax.twiny()
            ax_top.set_xlim(export_ax.get_xlim())
            ax_top.set_xlabel("CDP", fontsize=12)
        else:
            export_ax.set_xlabel("CDP", fontsize=12)
        if self.flip_x_var.get():
            export_ax.invert_xaxis()
            if axis_pos == "Top":
                ax_top.invert_xaxis()
        if self.grid_var.get():
            export_ax.grid(True, linestyle='--', linewidth=0.3)
        else:
            export_ax.grid(False)

        # Save the figure
        export_fig.savefig(file_path, dpi=dpi, bbox_inches='tight')
        plt.close(export_fig)
        self.status_label.config(text=f"Exported to {file_path}")

    @staticmethod
    def main():
        root = tk.Tk()
        app = SeismicViewerApp(root)
        app.root.mainloop()

if __name__ == "__main__":
    SeismicViewerApp.main()