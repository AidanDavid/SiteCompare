import tkinter as tk
from tkinter import ttk
from FileChecker import FileChecker

def show_ingredients():
    selected_recipe = recipe_var.get()
    ingredients_text.set(ingredients_dict[selected_recipe])

fc = FileChecker("C:/Users/aidan/OneDrive/Desktop/Wget/websites/bravenlyglobal.com","C:/Users/aidan/OneDrive/Desktop/Wget/websites/bravenlyglobal.d-solmedia.com")
fc.makeTable()

# Dictionary to store recipe names and their corresponding ingredients
recipes = {'Cookies': 'Flour, Sugar, Eggs, Butter',
           'Muffins': 'Flour, Baking Powder, Sugar, Milk, Eggs',
           'Waffles': 'Flour, Baking Powder, Sugar, Milk, Eggs, Butter'}

# Create a Tkinter window
window = tk.Tk()
window.title('Recipe Application')

# Dropdown for recipe selection
recipe_var = tk.StringVar()
recipe_dropdown = ttk.Combobox(window, textvariable=recipe_var, values=list(recipes.keys()))
recipe_dropdown.grid(row=0, column=0, padx=10, pady=10)

# Button to show ingredients
show_button = tk.Button(window, text='Show Ingredients', command=show_ingredients)
show_button.grid(row=0, column=1, padx=10, pady=10)

# Label to display ingredients
ingredients_text = tk.StringVar()
ingredients_label = tk.Label(window, textvariable=ingredients_text, wraplength=300)
ingredients_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Dictionary to map selected recipe to ingredients
ingredients_dict = {recipe: ingredients for recipe, ingredients in recipes.items()}

# Start the Tkinter event loop
window.mainloop()