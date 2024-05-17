import tkinter as tk
from tkinter import messagebox
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import webbrowser
 
 
# Global variables to store form details and session
form_list = []
current_url = ""
web_session = requests.Session()
 
 
def setup_interface(root):
   global entry_url, listbox_forms, frame_form_fields
 
 
   # Interface for URL input
   label_url = tk.Label(root, text="Enter URL:")
   label_url.pack(pady=(10, 0))
   entry_url = tk.Entry(root, width=60)
   entry_url.pack(pady=5)
 
 
   # Button to retrieve forms
   button_load_forms = tk.Button(root, text="Load Forms", command=load_forms)
   button_load_forms.pack(pady=10)
 
 
   # Listbox for showing forms
   listbox_forms = tk.Listbox(root, height=6)
   listbox_forms.pack(pady=15, fill=tk.X)
 
 
   # Button to choose a form
   button_select_form = tk.Button(root, text="Edit & Submit Selected Form", command=edit_form)
   button_select_form.pack(pady=5)
 
 
   # Frame for displaying form fields
   frame_form_fields = tk.Frame(root)
   frame_form_fields.pack(fill=tk.BOTH, expand=True)
 
 
def load_forms():
   global form_list, current_url, entry_url, listbox_forms, web_session
 
 
   current_url = entry_url.get().strip()
   if not current_url:
       messagebox.showerror("Error", "Please provide a URL.")
       return
 
 
   try:
       response = web_session.get(current_url)
       parsed_html = BeautifulSoup(response.text, "html.parser")
       form_list = parsed_html.find_all("form")
       listbox_forms.delete(0, tk.END)
       for idx, form in enumerate(form_list):
           form_action = form.attrs.get('action', 'No specified action')
           listbox_forms.insert(tk.END, f"Form {idx + 1}: {form_action}")
   except Exception as e:
       messagebox.showerror("Error", f"Could not load forms: {str(e)}")
 
 
def edit_form():
   global listbox_forms, frame_form_fields
 
 
   selected_index = listbox_forms.curselection()
   if not selected_index:
       messagebox.showerror("Error", "Select a form first.")
       return
   selected_form = form_list[selected_index[0]]
   form_details = extract_form_details(selected_form)
 
 
   # Clear old form fields
   for widget in frame_form_fields.winfo_children():
       widget.destroy()
 
 
   for field in form_details['fields']:
       label = tk.Label(frame_form_fields, text=f"{field['label']}:")
       label.pack()
       entry = tk.Entry(frame_form_fields, width=50)
       entry.insert(0, field['default'])
       entry.pack()
 
 
   submit_button = tk.Button(frame_form_fields, text="Submit Form", command=lambda: submit_selected_form(form_details))
   submit_button.pack(pady=10)
 
 
def submit_selected_form(form_details):
   global frame_form_fields, current_url, web_session
 
 
   input_widgets = frame_form_fields.winfo_children()[1::2]
   form_data = {field['name']: widget.get() for field, widget in zip(form_details['fields'], input_widgets)}
 
 
   form_action_url = urljoin(current_url, form_details['action'])
 
 
   if form_details['method'] == 'get':
       params = '&'.join([f"{key}={value}" for key, value in form_data.items()])
       full_url = f"{form_action_url}?{params}"
       webbrowser.open(full_url)  # Open the URL in the default web browser
   else:
       response = web_session.post(form_action_url, data=form_data)
       temp_html = 'temp_result.html'
       with open(temp_html, 'w', encoding='utf-8') as file:
           file.write(response.text)
       webbrowser.open(f'file://{temp_html}')  # Open the temporary file in the default web browser
 
 
def extract_form_details(form):
   details = {
       'action': form.attrs.get('action', '').strip(),
       'method': form.attrs.get('method', 'get').strip().lower(),
       'fields': []
   }
   for input_element in form.find_all('input'):
       input_name = input_element.attrs.get('name', None)
       if input_name:  # Only add inputs that have a name attribute
           details['fields'].append({
               'name': input_name,
               'type': input_element.attrs.get('type', 'text'),
               'default': input_element.attrs.get('value', ''),
               'label': input_name.capitalize()  # Use name for label, capitalized
           })
   return details
 
 
if __name__ == "__main__":
   root = tk.Tk()
   root.title("Web Form Explorer - The Pycodes")
   root.geometry("650x500")
 
 
   setup_interface(root)
   root.mainloop()
