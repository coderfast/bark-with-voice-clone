import tkinter as tk
from tkinter import ttk
from config.colors import COLORS
from widgets.mixer_fader import MixerFader


def create_slider(gui, parent: ttk.Frame, row: int, label: str,
                  variable: tk.DoubleVar, from_: float, to: float,
                  unit: str = "", color: str = None) -> MixerFader:
    """Create a mixer-style fader with value display."""
    fader = MixerFader(
        parent,
        variable=variable,
        from_=from_,
        to=to,
        width=65,
        height=125,
        orientation='vertical',
        color=color,
        on_press=lambda: gui._stop_audio(),
        on_release=lambda: gui._on_slider_release()
    )
    fader.pack(pady=(0, 5))

    gui.faders.append(fader)

    value_label = ttk.Label(parent, text=f"{variable.get():.1f}{unit}", width=8)
    value_label.pack()

    variable.trace_add('write', lambda *args, lbl=value_label, v=variable, u=unit:
                      lbl.configure(text=f"{v.get():.1f}{u}"))

    return fader


def create_basic_tab(gui, parent: ttk.Frame) -> None:
    """Create basic parameters tab with mixer-style faders."""
    inner = tk.Frame(parent, bg=COLORS['channel_bg'])
    inner.pack(fill=tk.BOTH, expand=True)

    ttk.Label(inner, text="BASIC", font=('', 10, 'bold'),
              foreground=COLORS['basic'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

    content_frame = tk.Frame(inner, bg=COLORS['channel_bg'])
    content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    for i in range(3):
        content_frame.columnconfigure(i, weight=1, uniform='basic')

    # Faders
    faders = [
        ("VOL", gui.volume_var, 0, 2, "%"),
        ("PITCH", gui.pitch_var, -12, 12, " st"),
        ("SPEED", gui.speed_var, 0.5, 2, "x"),
    ]

    for col, (label_text, var, from_, to, unit) in enumerate(faders):
        channel = tk.Frame(content_frame, bg=COLORS['channel_bg'],
                         highlightbackground=COLORS['channel_border'],
                         highlightthickness=1)
        channel.grid(row=0, column=col, padx=4, pady=5, sticky='nsew')

        tk.Label(channel, text=label_text, font=('', 9, 'bold'),
                fg=COLORS['basic'], bg=COLORS['channel_bg']).pack(pady=(5, 2))

        fader_container = tk.Frame(channel, bg=COLORS['channel_bg'])
        fader_container.pack(fill=tk.X, padx=5, pady=2)
        fader = MixerFader(
            fader_container,
            variable=var,
            from_=from_,
            to=to,
            width=65,
            height=125,
            orientation='vertical',
            color=COLORS['basic'],
            on_press=lambda: gui._stop_audio(),
            on_release=lambda: gui._on_slider_release()
        )
        fader.pack(expand=True)
        gui.faders.append(fader)

        val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
        val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
        val_frame.pack_propagate(False)
        tk.Label(val_frame, text=f"{var.get():.1f}{unit}",
                font=('', 8), fg=COLORS['led_green'], bg=COLORS['meter_bg']).pack(expand=True)

        def update_val(v=var, lbl=None, u=unit):
            if lbl and lbl.winfo_exists():
                lbl.configure(text=f"{v.get():.1f}{u}")
        var.trace_add('write', lambda *args, v=var, u=unit: gui.root.after(10, update_val, v, None, u))


def create_eq_tab(gui, parent: ttk.Frame) -> None:
    """Create EQ parameters tab."""
    inner = tk.Frame(parent, bg=COLORS['channel_bg'])
    inner.pack(fill=tk.BOTH, expand=True)

    ttk.Label(inner, text="EQUALIZER", font=('', 10, 'bold'),
              foreground=COLORS['eq'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

    fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
    fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    eq_faders = [
        ("BASS\n100Hz", gui.eq_bass_var),
        ("LOW\n400Hz", gui.eq_low_mid_var),
        ("MID\n1kHz", gui.eq_mid_var),
        ("HIGH\n2.5kHz", gui.eq_high_mid_var),
        ("TREBLE\n6kHz", gui.eq_treble_var),
    ]

    for col, (label_text, var) in enumerate(eq_faders):
        channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                         highlightbackground=COLORS['channel_border'],
                         highlightthickness=1)
        channel.grid(row=0, column=col, padx=3, pady=5, sticky='nsew')

        tk.Label(channel, text=label_text, font=('', 8, 'bold'),
                fg=COLORS['eq'], bg=COLORS['channel_bg'], justify=tk.CENTER).pack(pady=(8, 2))

        create_slider(gui, channel, 0, "", var, -12, 12, " dB", COLORS['eq'])

        val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
        val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
        val_frame.pack_propagate(False)
        tk.Label(val_frame, text=f"{var.get():.1f} dB",
                font=('', 8), fg=COLORS['eq'], bg=COLORS['meter_bg']).pack(expand=True)

    for i in range(5):
        fader_grid.columnconfigure(i, weight=1)


def create_filters_tab(gui, parent: ttk.Frame) -> None:
    """Create filters parameters tab."""
    inner = tk.Frame(parent, bg=COLORS['channel_bg'])
    inner.pack(fill=tk.BOTH, expand=True)

    ttk.Label(inner, text="FILTERS", font=('', 10, 'bold'),
              foreground=COLORS['eq'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

    fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
    fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    filter_faders = [
        ("LOW\nPASS", gui.low_pass_var, 100, 20000, " Hz"),
        ("HIGH\nPASS", gui.high_pass_var, 20, 5000, " Hz"),
    ]

    for col, (label_text, var, from_, to, unit) in enumerate(filter_faders):
        channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                         highlightbackground=COLORS['channel_border'],
                         highlightthickness=1)
        channel.grid(row=0, column=col, padx=15, pady=5, sticky='nsew')

        tk.Label(channel, text=label_text, font=('', 9, 'bold'),
                fg=COLORS['eq'], bg=COLORS['channel_bg'], justify=tk.CENTER).pack(pady=(8, 2))

        create_slider(gui, channel, 0, "", var, from_, to, unit, COLORS['eq'])

        val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
        val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
        val_frame.pack_propagate(False)
        tk.Label(val_frame, text=f"{var.get():.0f}{unit}",
                font=('', 8), fg=COLORS['eq'], bg=COLORS['meter_bg']).pack(expand=True)

    fader_grid.columnconfigure(0, weight=1)
    fader_grid.columnconfigure(1, weight=1)


def create_modulation_tab(gui, parent: ttk.Frame) -> None:
    """Create modulation parameters tab."""
    inner = tk.Frame(parent, bg=COLORS['channel_bg'])
    inner.pack(fill=tk.BOTH, expand=True)

    ttk.Label(inner, text="MODULATION", font=('', 10, 'bold'),
              foreground=COLORS['modulation'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

    fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
    fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    mod_faders = [
        ("CHORUS", gui.chorus_var),
        ("FLANGER", gui.flanger_var),
        ("PHASER", gui.phaser_var),
        ("TREMOLO", gui.tremolo_var),
        ("VIBRATO", gui.vibrato_var),
    ]

    for col, (label_text, var) in enumerate(mod_faders):
        channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                         highlightbackground=COLORS['channel_border'],
                         highlightthickness=1)
        channel.grid(row=0, column=col, padx=3, pady=5, sticky='nsew')

        tk.Label(channel, text=label_text, font=('', 9, 'bold'),
                fg=COLORS['modulation'], bg=COLORS['channel_bg']).pack(pady=(8, 2))

        create_slider(gui, channel, 0, "", var, 0, 1, "", COLORS['modulation'])

        val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
        val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
        val_frame.pack_propagate(False)
        tk.Label(val_frame, text=f"{var.get():.0%}",
                font=('', 8), fg=COLORS['modulation'], bg=COLORS['meter_bg']).pack(expand=True)

    for i in range(5):
        fader_grid.columnconfigure(i, weight=1)


def create_distortion_tab(gui, parent: ttk.Frame) -> None:
    """Create distortion parameters tab."""
    inner = tk.Frame(parent, bg=COLORS['channel_bg'])
    inner.pack(fill=tk.BOTH, expand=True)

    ttk.Label(inner, text="DISTORTION", font=('', 10, 'bold'),
              foreground=COLORS['distortion'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

    fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
    fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    dist_faders = [
        ("DIST", gui.distortion_var, 0, 1, ""),
        ("BITS", gui.bitcrusher_var, 4, 32, " bit"),
        ("DRIVE", gui.overdrive_var, 1, 10, "x"),
    ]

    for col, (label_text, var, from_, to, unit) in enumerate(dist_faders):
        channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                         highlightbackground=COLORS['channel_border'],
                         highlightthickness=1)
        channel.grid(row=0, column=col, padx=15, pady=5, sticky='nsew')

        tk.Label(channel, text=label_text, font=('', 9, 'bold'),
                fg=COLORS['distortion'], bg=COLORS['channel_bg']).pack(pady=(8, 2))

        create_slider(gui, channel, 0, "", var, from_, to, unit, COLORS['distortion'])

        val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
        val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
        val_frame.pack_propagate(False)
        tk.Label(val_frame, text=f"{var.get():.1f}{unit}",
                font=('', 8), fg=COLORS['distortion'], bg=COLORS['meter_bg']).pack(expand=True)

    fader_grid.columnconfigure(0, weight=1)
    fader_grid.columnconfigure(1, weight=1)
    fader_grid.columnconfigure(2, weight=1)


def create_time_tab(gui, parent: ttk.Frame) -> None:
    """Create time-based parameters tab."""
    inner = tk.Frame(parent, bg=COLORS['channel_bg'])
    inner.pack(fill=tk.BOTH, expand=True)

    ttk.Label(inner, text="TIME EFFECTS", font=('', 10, 'bold'),
              foreground=COLORS['time'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

    fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
    fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    time_faders = [
        ("REVERB", gui.reverb_var, 0, 1, ""),
        ("DELAY", gui.delay_var, 0, 500, " ms"),
    ]

    for col, (label_text, var, from_, to, unit) in enumerate(time_faders):
        channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                         highlightbackground=COLORS['channel_border'],
                         highlightthickness=1)
        channel.grid(row=0, column=col, padx=15, pady=5, sticky='nsew')

        tk.Label(channel, text=label_text, font=('', 9, 'bold'),
                fg=COLORS['time'], bg=COLORS['channel_bg']).pack(pady=(8, 2))

        create_slider(gui, channel, 0, "", var, from_, to, unit, COLORS['time'])

        val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
        val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
        val_frame.pack_propagate(False)
        tk.Label(val_frame, text=f"{var.get():.1f}{unit}",
                font=('', 8), fg=COLORS['time'], bg=COLORS['meter_bg']).pack(expand=True)

    fader_grid.columnconfigure(0, weight=1)
    fader_grid.columnconfigure(1, weight=1)


def create_dynamics_tab(gui, parent: ttk.Frame) -> None:
    """Create dynamics parameters tab."""
    inner = tk.Frame(parent, bg=COLORS['channel_bg'])
    inner.pack(fill=tk.BOTH, expand=True)

    ttk.Label(inner, text="DYNAMICS", font=('', 10, 'bold'),
              foreground=COLORS['dynamics'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

    fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
    fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    dyn_faders = [
        ("THRESH", gui.comp_threshold_var, -40, 0, " dB"),
        ("RATIO", gui.comp_ratio_var, 1, 20, ":1"),
        ("GATE", gui.gate_var, -60, 0, " dB"),
    ]

    for col, (label_text, var, from_, to, unit) in enumerate(dyn_faders):
        channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                         highlightbackground=COLORS['channel_border'],
                         highlightthickness=1)
        channel.grid(row=0, column=col, padx=15, pady=5, sticky='nsew')

        tk.Label(channel, text=label_text, font=('', 9, 'bold'),
                fg=COLORS['dynamics'], bg=COLORS['channel_bg']).pack(pady=(8, 2))

        create_slider(gui, channel, 0, "", var, from_, to, unit, COLORS['dynamics'])

        val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
        val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
        val_frame.pack_propagate(False)
        tk.Label(val_frame, text=f"{var.get():.1f}{unit}",
                font=('', 8), fg=COLORS['dynamics'], bg=COLORS['meter_bg']).pack(expand=True)

    fader_grid.columnconfigure(0, weight=1)
    fader_grid.columnconfigure(1, weight=1)
    fader_grid.columnconfigure(2, weight=1)


def create_utility_tab(gui, parent: ttk.Frame) -> None:
    """Create utility parameters tab."""
    inner = tk.Frame(parent, bg=COLORS['channel_bg'])
    inner.pack(fill=tk.BOTH, expand=True)

    ttk.Label(inner, text="UTILITY", font=('', 10, 'bold'),
              foreground=COLORS['utility'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

    fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
    fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    util_faders = [
        ("FADE\nIN", gui.fade_in_var, 0, 5000, " ms"),
        ("FADE\nOUT", gui.fade_out_var, 0, 5000, " ms"),
        ("NORM", gui.normalize_var, -24, 0, " dB"),
        ("TRIM\nSTART", gui.trim_start_var, 0, 100, " s"),
        ("TRIM\nEND", gui.trim_end_var, 0, 100, " s"),
    ]

    for col, (label_text, var, from_, to, unit) in enumerate(util_faders):
        channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                         highlightbackground=COLORS['channel_border'],
                         highlightthickness=1)
        channel.grid(row=0, column=col, padx=3, pady=5, sticky='nsew')

        tk.Label(channel, text=label_text, font=('', 8, 'bold'),
                fg=COLORS['utility'], bg=COLORS['channel_bg'], justify=tk.CENTER).pack(pady=(8, 2))

        create_slider(gui, channel, 0, "", var, from_, to, unit, COLORS['utility'])

        val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
        val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
        val_frame.pack_propagate(False)
        tk.Label(val_frame, text=f"{var.get():.1f}{unit}",
                font=('', 8), fg=COLORS['utility'], bg=COLORS['meter_bg']).pack(expand=True)

    for i in range(5):
        fader_grid.columnconfigure(i, weight=1)

    # Reverse checkbox
    reverse_frame = tk.Frame(inner, bg=COLORS['channel_bg'])
    reverse_frame.pack(fill=tk.X, pady=10, padx=10)
    reverse_cb = tk.Checkbutton(reverse_frame, text="REVERSE",
                               variable=gui.reverse_var,
                               command=gui._on_reverse_change,
                               bg=COLORS['channel_bg'], fg=COLORS['utility'],
                               selectcolor=COLORS['meter_bg'],
                               activebackground=COLORS['channel_bg'],
                               activeforeground=COLORS['utility'])
    reverse_cb.pack(side=tk.LEFT)
    reverse_cb.bind('<ButtonPress-1>', lambda e: gui._stop_audio())
    inner.columnconfigure(1, weight=1)
