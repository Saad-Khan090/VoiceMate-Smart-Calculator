def run_gui():

    import customtkinter as ctk
    import speech_recognition as sr
    from .parser import calculate
    import re
    from gtts import gTTS
    from playsound import playsound
    import os
    import threading


    words_to_math = {
        # Numbers
        "zero":"0","one":"1","two":"2","three":"3","four":"4","five":"5",
        "six":"6","seven":"7","eight":"8","nine":"9",
        # Operator
        "plus":"+", "minus":"-", "multiply":"*", "multiply by": "*", "times":"*", "into":"*", "x":"*",
        "divide":"/", "divide by": "/", "by":"/","over":"/","sin":"sin(","cos":"cos(",'tan':'tan(','log':"log(",
        #New logic words
        "add": "",
        "sum": "",
        "of": "",
        "and": "",
        # Bractet and power 
        "open bracket":"(", "bracket open":"(", "close bracket":")", "bracket close":")","open":"(", "close":")",
        "power": "**", "raised to": "**",
        # filter word to ignore because we handle these in if else
        "calculate": "", "what is": "", "how much is": "", "the": "","What's the answer of":"","Hey calculate":"",
        "add": "", "sum": "", "of": "", "subtract": "", "multiply": "", "divide": "", "Canyou": "","Tell me":"",
        "Solve this:":""

    }

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("VoiceMate Modern Calculator")
    app.geometry("520x720")

    # Global varaibles
    expression = ""
    voice_enabled = True
    history_window = None
    history_data = []
    scroll_frame = None


    # Scientific Frame Setup
    sci_frame = ctk.CTkFrame(app)

  
    #Display box
    display = ctk.CTkEntry(app, font=("Arial", 24),height=80, width=300)
    display.grid(row=0, column=0, columnspan=4, padx=10, pady=(20, 10), sticky="ew") 
    
    
    #Functions

    def button_click(value):
        nonlocal expression
        expression += value
        display.delete(0, "end")
        display.insert(0, expression)

    # Clear function
    def clear():
        nonlocal expression
        expression = ""
        display.delete(0, "end")

    #update display
    def update_display(message):
        display.delete(0, "end")
        display.insert(0, message)

    # Speak Result
    def speak(text):
        if not voice_enabled:
            return
        def _speak():
            try:
                tts = gTTS(text=text, lang='en')
                file = "voice_output.mp3"
                tts.save(file)
                playsound(file)
                os.remove(file)
            except:
                pass
        threading.Thread(target=_speak).start()

    # refresh history
    def refresh_history_window():
        if scroll_frame is not None and scroll_frame.winfo_exists():
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            if not history_data:
                 ctk.CTkLabel(scroll_frame, text="No History Yet", font=("Arial", 14)).pack(pady=5)
            else:
                 for item in history_data:
                    ctk.CTkLabel(scroll_frame, text=item, font=("Arial",14), anchor="w").pack(fill="x", pady=2)
    def show_history():

        nonlocal history_window, scroll_frame

        if history_window is None or not history_window.winfo_exists():
            history_window = ctk.CTkToplevel(app)
            history_window.title("Calculation History")
            history_window.geometry("300x400")
            history_window.attributes("-topmost", True)

            # Heading
            ctk.CTkLabel(history_window, text="History", font=("Arial", 20, "bold")).pack(pady=10)

            def clear_all_history():
                history_data.clear()
                refresh_history_window()
    
            ctk.CTkButton(history_window, text="Clear All History", fg_color="#b30000", hover_color="#800000",
                  height=30, command=clear_all_history).pack(pady=5)
            # Scroll Frame
            scroll_frame = ctk.CTkScrollableFrame(history_window)
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # first time loads
            refresh_history_window()
        else:
            history_window.focus()
            refresh_history_window()

    def clear_history():
        history_data.clear()
        refresh_history_window()

    # evaluate function
    def equal_press():
        nonlocal expression
        try:
            expression = auto_fix_expression(expression)
            result = calculate(expression)
            history_entry = f"{expression} = {result}"
            history_data.insert(0, history_entry)
            display.delete(0, "end")
            display.insert(0, result)
            speak(f"The Answer is {result}")
            refresh_history_window()  #update window if open
            expression = str(result)
        except ZeroDivisionError:
            display.delete(0, "end")
            display.insert(0, "Division by Zero")
            expression = ""
            speak("Error: Division by zero")
        except Exception as e:
            display.delete(0, "end")
            display.insert(0, f"Error: {e}")
            expression = ""
            speak("Calculation Error")
        except:
            display.delete(0, "end")
            display.insert(0, "Error")
            expression = ""

    def voice_input():
        nonlocal expression

        r = sr.Recognizer()
        with sr.Microphone() as source:
            update_display("listening...")
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                text = r.recognize_google(audio).lower()
                print(f'You said: {text}')

                # Addition 
                if "addition of" in text and "and" in text:
                    text = text.replace("addition of","").replace("and", "+")
                if "add" in text and "and" in text:
                    text = text.replace("add", "").replace("and", "+")
                elif "sum of" in text and "and" in text:
                    text = text.replace("sum of", "").replace("and","+")
                # Subtraction
                elif "subtraction of" in text and "and" in text:
                    text = text.replace("subtraction of","").replace("and", "-")
                elif "subtract" in text and "and" in text:
                    text = text.replace('subtract','').replace('and', '-')
                elif "difference between" in text and "and" in text:
                    text = text.replace('difference between', '').replace('and','-')
                elif 'take away' in text:
                    text = text.replace('take away', '-')
                elif "less" in text:
                    text = text.replace("less", '-')   
                #Multiplication
                elif "multiply" in text and "by" in text:
                    text = text.replace("multiply","").replace("by", "*")
                elif "multiplication of" in text and "and" in text:
                    text = text.replace("multiplication of", "").replace("and", "*")
                elif "multiply" in text and "and" in text:
                    text = text.replace("multiply", "").replace("and", "*")
                elif "product of" in text and "and" in text:
                    text = text.replace("product of", "").replace("and", "*")          
                # Division
                elif "division of" in text and "and" in text:
                    text = text.replace("division of", "").replace("and", "/")
                elif "divide" in text and "by" in text:
                    text = text.replace("divide", "").replace("by","/")
                elif "ratio of" in text and "and" in text:
                    text = text.replace("ratio of", "").replace("and", "/")
                elif "clear all history" in text or "clear history" in text or  "clearall" in text or "clearallhistory" in text:
                    clear_history()
                    speak("History cleared")
                    update_display("History Cleared")
                    return
                elif "showhistory" in text or "history" in text or "show history" in text:
                    show_history()
                    update_display("History tab opened")
                    speak("History tab opened")
                    return
                elif "clear display" in text or "cleardisplay" in text or "clear" in text:
                    speak("display cleared")
                    display.delete(0, "end")
                    return

                recognized_text = text
                for word, symbol in words_to_math.items():
                    recognized_text = recognized_text.replace(word, symbol)
                expression = recognized_text
                expression = auto_fix_expression(expression)            
                result = calculate(expression)
                history_addition = f"{expression} = {result}"
                history_data.insert(0, history_addition)
                refresh_history_window()
                display.delete(0, "end")
                display.insert(0, expression + " = " + str(result))
                speak(f"The Answer is {result}")
                expression = str(result)
            except sr.UnknownValueError:
                speak("Could not understand your input.")
                update_display(expression)
            except sr.RequestError:
                speak("Check your internet connection")

            except Exception as e:
                print(e)
                update_display("Error")

    
    ctk.CTkButton(app, text="🎤 Voice", height=40, font=("Arial", 16), command=voice_input).grid(
    row=1, column=0, columnspan=2, padx=(10, 5), pady=5, sticky="ew")
    
    btn_history = ctk.CTkButton(app, text="🕒", width=40, command=show_history)
    btn_history.place(x=10, y=10)
    
    def toggle_voice():
        nonlocal voice_enabled
        voice_enabled = not voice_enabled
        if voice_enabled:
            switch_voice.configure(text="Mute")
        else:
            switch_voice.configure(text="Unmute")
    switch_voice = ctk.CTkSwitch(app,text="Mute",command=toggle_voice,onvalue=True,offvalue=False,
    switch_width=60,switch_height=28,font=("Arial", 15))
    switch_voice.grid(row=1, column=2, columnspan=2, padx=(5, 10), pady=5, sticky="ew")    

    #auto fix keyboard expression
    def auto_fix_expression(expr):
        expr = expr.replace(" ","")
        expr = expr.replace("x", "*").replace("X","*")
        expr = re.sub(r"(\d)\(", r"\1*(", expr)
        expr = re.sub(r"\)(\d)", r")*\1", expr)
        expr = re.sub(r"\)\(", r")*(", expr)
        return expr
    
    # Keyboard Input
    def keyboard_input(event):
        nonlocal expression
        expression = display.get()
        equal_press()
    display.bind("<Return>", keyboard_input)

    
    
    
    # Butten Frame
    frame = ctk.CTkFrame(app)
    frame.grid(row=2, column=0, columnspan=4, padx=10, pady=(10, 20), sticky="nsew")

    for i in range(4):
        app.grid_columnconfigure(i, weight=1)
        frame.grid_columnconfigure(i, weight=1)

    buttons = [
        ("7",0,0), ("8",0,1), ("9",0,2), ("/",0,3),
        ("4",1,0), ("5",1,1), ("6",1,2), ("*",1,3),
        ("1",2,0), ("2",2,1), ("3",2,2), ("-",2,3),
        ("0",3,0), (".",3,1), ("=",3,2), ("+",3,3),
        ("(",4,0), (")",4,1)
    ]

    for text, r, c in buttons:
        cmd = lambda x=text: button_click(x) if x != "=" else equal_press()
        # Operator and spacial button color
        if text in ("/","*", "-", "+", "="):
            color = "red"
            hover_color = "#990000"
        elif text in ("(", ")", "."):
            color = "#404040"
            hover_color = "#505050"
        else:
            color = "#1F6AA5"
            hover_color = "#144870"

        ctk.CTkButton(frame, text=text, font=("Arial", 20, "bold"), height=60,command=cmd,fg_color=color,hover_color=hover_color
                      ).grid(row=r, column=c, padx=5, pady=5, sticky="nsew") 


    ctk.CTkButton(frame, text="Clear", height=60,font=("Arial", 16),command=clear,fg_color="darkred", # Clear button ka alag colour
    hover_color="red").grid(row=4, column=2, columnspan=2, padx=5, pady=5, sticky="nsew")    
    


    # list of scienfific buttons
    sci_buttons = [
        ("sin", 0, 0), ("cos", 0, 1), ("tan", 0, 2),
        ("log", 1, 0), ("ln", 1, 1), ("sqrt", 1, 2),
        ("^", 2, 0), ("fact", 2, 1), ("(", 2, 2),
        (")", 3, 0)
    ]
    for text, r, c in sci_buttons:
        if text in ["sin", "cos", "tan", "log", "ln", "sqrt", "fact"]:
            insert_text = text +"("
        else:
            insert_text = text
        cmd = lambda x = insert_text: button_click(x)
        ctk.CTkButton(sci_frame, text=text, width=60, height=60,font=("Arial", 18),fg_color="#2B2B2B",command=cmd
                      ).grid(row=r, column=c, padx=5, pady=5)

    is_scientific = False

    def toggle_mode():
        nonlocal is_scientific
        is_scientific = not is_scientific

        if is_scientific:
            app.geometry("850x720")
            sci_frame.grid(row=2, column=4, rowspan=5, padx=10, pady=10, sticky="n")
            mode_btn.configure(text="Standard Mode")
        else:
            app.geometry("520x720")
            
            sci_frame.grid_forget()
            mode_btn.configure(text="Scientific Mode")

    mode_btn = ctk.CTkButton(app, text="Scientific Mode", command=toggle_mode, fg_color="green")
    mode_btn.grid(row=3, column=0, columnspan=4,pady=5)
    app.mainloop()