"""
PassGuard - A Password Security Toolkit (GUI)
Lab 1 - PYTHON FOR ENGINEERS - Bsc COMPUTER ENGINEERING (Level 200)
Author: <YAKUBU SHARHABIL ANAMZOYA > | Index No: <2526400394>
"""

import string
import secrets
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

LOG_FILE = "passguard_log.txt"

Commonly_used = [
    "abc123", "letmein", "welcome", "123456789", "111111",
    "12345678", "12345", "123123", "admin", "password1",
    "000000", "iloveyou", "ghana123", "monkey", "accra123",
    "football", "god123"
]


COLOURS = {
    "VERY WEAK": "#dc2626",
    "WEAK": "#ea580c",
    "MEDIUM": "#ca8a04",
    "STRONG": "#16a34a"
}


def verify_password(password):
    secure = 0
    tip = []

    if password.lower() in Commonly_used:
        return 0, "VERY WEAK", ["THIS IS A COMMON PASSWORD AND CAN EASILY BE GUESSED. NEVER USE IT AGAIN."]

    if len(password) >= 12:
        secure += 2
    elif len(password) >= 8:
        secure += 1
        tip.append("Too short; can be easily guessed.")
    else:
        tip.append("Password is too weak. Add unique characters and lengthen it to 12+ characters.")

    if any(ch.isupper() for ch in password):
        secure += 1
    else:
        tip.append("Add uppercase letters to make your password more secure.")

    if any(ch.islower() for ch in password):
        secure += 1
    else:
        tip.append("Add lowercase letters to make your password more secure.")

    if any(ch.isdigit() for ch in password):
        secure += 1
    else:
        tip.append("Add numbers (0-9) to make your password more secure.")

    if any(ch in string.punctuation for ch in password):
        secure += 1
    else:
        tip.append("Add unique characters (@, #, !, etc.) to make your password more secure.")

    if secure >= 5:
        label = "STRONG"
    elif secure >= 3:
        label = "MEDIUM"
    elif secure >= 2:
        label = "WEAK"
    else:
        label = "VERY WEAK"

    return secure, label, tip


def generator(length=16):
    all_chars = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(all_chars) for _ in range(length))
        secure, label, tip = verify_password(password)
        if label == "STRONG":
            return password


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def save_to_log(password, score, label):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    short_hash = hash_password(password)[:10]
    record = f"{time_now} | {short_hash}... | {score}/6 | {label}"
    with open(LOG_FILE, "a") as file:
        file.write(record + "\n")
    return record


def load_log():
    try:
        with open(LOG_FILE, "r") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []


def live_check(event=None):
    password = password_entry.get()
    if password == "":
        strength_bar["value"] = 0
        result_label.config(text="Start typing a password...", fg="#64748b")
        tips_label.config(text="")
        return

    secure, label, tip = verify_password(password)
    strength_bar["value"] = secure
    result_label.config(text=f"{label} ({secure}/6)", fg=COLOURS.get(label, "#0f172a"))
    tips_label.config(text="\n".join("• " + t for t in tip))


def on_check():
    password = password_entry.get()
    if password == "":
        messagebox.showwarning("PassGuard", "Please type a password first.")
        return
    secure, label, tip = verify_password(password)
    record = save_to_log(password, secure, label)
    history_list.insert(tk.END, record)
    messagebox.showinfo("PassGuard", f"Result: {label} ({secure}/6)\nSaved to history.")


def toggle_show():
    if show_var.get():
        password_entry.config(show="")
    else:
        password_entry.config(show="*")


def on_generate():
    new_password = generator(length_var.get())
    generated_var.set(new_password)


def on_copy():
    root.clipboard_clear()
    root.clipboard_append(generated_var.get())
    messagebox.showinfo("PassGuard", "Password copied to clipboard.")


def on_hash():
    password = password_entry.get()
    if password == "":
        messagebox.showwarning("PassGuard", "Please type a password first.")
        return
    hash_var.set(hash_password(password))



root = tk.Tk()
root.title("PassGuard - Password Manager")
root.geometry("950x650")
root.config(bg="#f1f5f9")
root.resizable(False, False)

header_frame = tk.Frame(root, bg="#f1f5f9")
header_frame.pack(fill="x", padx=20, pady=(20, 10))

title_label = tk.Label(header_frame, text="🔒 PassGuard", font=("Segoe UI", 22, "bold"), fg="#0f172a", bg="#f1f5f9")
title_label.pack(anchor="w")

subtitle_label = tk.Label(header_frame, text="Securely check, generate, and hash your passwords.",
                          font=("Segoe UI", 11), fg="#64748b", bg="#f1f5f9")
subtitle_label.pack(anchor="w", pady=(2, 0))

check_frame = tk.LabelFrame(root, text=" 1. Check Password Strength ", font=("Segoe UI", 11, "bold"), fg="#0f172a",
                            bg="#ffffff", bd=1, relief="solid", padx=15, pady=15)
check_frame.pack(fill="x", padx=20, pady=10)

password_entry = tk.Entry(check_frame, show="*", font=("Segoe UI", 12), bg="#ffffff", fg="#0f172a",
                          insertbackground="#0f172a", relief="solid", bd=1, width=40)
password_entry.pack(fill="x", ipady=6, ipadx=5)
password_entry.bind("<KeyRelease>", live_check)

show_var = tk.BooleanVar()
show_chk = tk.Checkbutton(check_frame, text="Show password", variable=show_var, command=toggle_show,
                          font=("Segoe UI", 10), fg="#334155", bg="#ffffff", selectcolor="#ffffff",
                          activebackground="#ffffff", activeforeground="#0f172a")
show_chk.pack(anchor="w", pady=(8, 5))

strength_bar = ttk.Progressbar(check_frame, maximum=6, length=400)
strength_bar.pack(fill="x", pady=5)

result_label = tk.Label(check_frame, text="Start typing a password...", font=("Segoe UI", 11, "bold"), fg="#64748b",
                        bg="#ffffff")
result_label.pack(anchor="w", pady=(3, 0))

tips_label = tk.Label(check_frame, text="", justify="left", font=("Segoe UI", 9), fg="#334155", bg="#ffffff")
tips_label.pack(anchor="w", pady=(3, 5))

button_row = tk.Frame(check_frame, bg="#ffffff")
button_row.pack(anchor="w", pady=(8, 5))

btn_save = tk.Button(button_row, text="Save Check", font=("Segoe UI", 10, "bold"), bg="#3b82f6", fg="black",
                     relief="raised", bd=1, padx=12, pady=5, command=on_check, cursor="hand2")
btn_save.pack(side="left")

btn_hash = tk.Button(button_row, text="Hash It", font=("Segoe UI", 10, "bold"), bg="#e2e8f0", fg="#0f172a", relief="raised",
                     bd=1, padx=12, pady=5, command=on_hash, cursor="hand2")
btn_hash.pack(side="left", padx=8)

hash_var = tk.StringVar()
hash_entry = tk.Entry(check_frame, textvariable=hash_var, state="readonly", font=("Consolas", 10), bg="#ffffff",
                      fg="white", relief="solid", bd=1)
hash_entry.pack(fill="x", ipady=4, pady=(8, 0))

gen_frame = tk.LabelFrame(root, text=" 2. Generate Strong Password ", font=("Segoe UI", 11, "bold"), fg="#0f172a",
                          bg="#ffffff", bd=1, relief="solid", padx=15, pady=15)
gen_frame.pack(fill="x", padx=20, pady=10)

gen_sub_frame = tk.Frame(gen_frame, bg="#ffffff")
gen_sub_frame.pack(fill="x")

tk.Label(gen_sub_frame, text="Length:", font=("Segoe UI", 10), fg="#334155", bg="#ffffff").pack(side="left")

length_var = tk.IntVar(value=16)
length_spin = tk.Spinbox(gen_sub_frame, from_=8, to=32, width=4, textvariable=length_var, state="readonly",
                         font=("Segoe UI", 10), bg="#ffffff", fg="#0f172a")
length_spin.pack(side="left", padx=(8, 15))

btn_gen = tk.Button(gen_sub_frame, text="Generate", font=("Segoe UI", 10, "bold"), bg="#10b981", fg="black",
                    relief="raised", bd=1, padx=12, pady=4, command=on_generate, cursor="hand2")
btn_gen.pack(side="left")

generated_var = tk.StringVar()
gen_entry = tk.Entry(gen_sub_frame, textvariable=generated_var, state="readonly", font=("Consolas", 11), bg="#ffffff",
                     fg="white", relief="solid", bd=1, width=22)
gen_entry.pack(side="left", padx=15, ipady=3)

btn_copy = tk.Button(gen_sub_frame, text="Copy", font=("Segoe UI", 10, "bold"), bg="#e2e8f0", fg="#0f172a", relief="raised",
                     bd=1, padx=12, pady=4, command=on_copy, cursor="hand2")
btn_copy.pack(side="left")

hist_frame = tk.LabelFrame(root, text=" 3. Activity History (Hashes Only) ", font=("Segoe UI", 11, "bold"),
                           fg="#0f172a", bg="#ffffff", bd=1, relief="solid", padx=15, pady=15)
hist_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

history_list = tk.Listbox(hist_frame, font=("Consolas", 9), bg="#ffffff", fg="#0f172a", selectbackground="#cbd5e1",
                          relief="solid", bd=1, highlightthickness=0, height=9)
history_list.pack(fill="both", expand=True)

for saved_record in load_log():
    history_list.insert(tk.END, saved_record)

root.mainloop()
