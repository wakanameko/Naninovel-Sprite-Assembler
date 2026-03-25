import platform

def canvas_on_mousewheel(instance, event):
    amount=0
    # Linux (idk this is works)
    if platform.system() == "Linux" and (event.num == 4 or event.delta > 0):   # up
        amount = -1
    elif platform.system() == "Linux" and (event.num == 5 or event.delta < 0): # down
        amount = 1
    else:
        # Win, Mac
        if platform.system() == "Windows":
            amount = -event.delta // 120
        else:
            amount = -event.delta

    if event.state & 1:
        instance.canvas_preview.xview_scroll(amount, "units")
    else:
        instance.canvas_preview.yview_scroll(amount, "units")
