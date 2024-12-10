"""Launches a graphing calculator as a windowed application.
Designed and coded by Matthew Tien Wells, 2024.
"""

import tkinter, equations
import tkinter.colorchooser
from tkinter import ttk, Tk
from math import floor, ceil
from functools import partial

class canvasView:
    """Class representing the view of the coordinate plane shown on
    the canvas widget.
    """
    def __init__(self, width=500, height=500, zoom=10):
        self.width = width
        self.height = height
        self.zoom = zoom
        self.x_center = 0
        self.y_center = 0
        self.dragStartX = 0
        self.dragStartY = 0

    def drag(self, event):
        """Accept a motion event with x and y attributes and shift the
        view accordingly.
        """
        x = event.x
        y = event.y
        x -= self.dragStartX
        y -= self.dragStartY
        y = -y
        x /= self.zoom
        y /= self.zoom
        self.x_center = round(x + self.dragStartCenterX)
        self.y_center = round(y + self.dragStartCenterY)

    def dragStart(self, event):
        """Record where the mouse and view are when the user begins
        dragging to be used to calculate the proper placement of the
        view while dragging.
        """
        self.dragStartX = event.x
        self.dragStartY = event.y
        self.dragStartCenterX = self.x_center
        self.dragStartCenterY = self.y_center

    
view = canvasView()

def toCanvas(x, y):
    """Convert x and y coordinates to fit the tkinter canvas system."""
    x += view.x_center
    y += view.y_center
    x *= view.zoom
    y *= view.zoom
    x += view.width/2
    y = view.height/2 - y
    return (x,y)

def fromCanvas(x, y):
    """Convert x any y coordinates from the tkinter canvas system to
    a value on the 2 dimensional plane represented by view.
    """
    x -= view.width/2
    y = view.height/2 - y
    x /= view.zoom
    y /= view.zoom
    x -= view.x_center
    y -= view.y_center
    return (x,y)

root = Tk()
root.title("Graphing Calculator")
frm = ttk.Frame(root, padding=10)
frm.grid()
canvas = tkinter.Canvas(frm, width=view.width, height=view.height)
canvas.grid(column=0,row=0)

formulaInput = tkinter.Text(frm,height=2)
formulaInput.grid(column=0,row=1)
formulas = [] #type: list[equations.equation]

formulaDisplay = ttk.Frame(frm,padding=5)
formulaDisplay.grid(column=1,row=0)

solutionsDisplay = tkinter.Frame(root)
solutionsDisplay.grid(row=0,column=3)

def chooseFormulaColor():
    """Select a color to draw a new formula with."""
    # High contrast color palette to ensure accessibility per WCAG
    # standards. 
    palette = [
        '#C44601','#054FB9','#0073E6','#B51963','#5928ED'
    ]
    if len(formulas) == 0:
        return palette[0]
    try:
        colorIndex = palette.index(formulas[-1].color)
    except ValueError:
        colorIndex = 0
    return palette[(colorIndex + 1) % len(palette)]

def drawFormula(formula:equations.equation|None=None, input=formulaInput):
    """Draw the provided formula on the canvas. Requires the only
    variable in the equation to be x.
    """
    if formula == None:
        formula = equations.equation(color=chooseFormulaColor())
        formulas.append(formula)
    if input != None:
        formulaStr = input.get(1.0, "end-1c")
        formula.parse(formulaStr)
    elif formula.symbols == []:
        return None

    x = round(view.zoom*fromCanvas(view.width/2,view.height/2)[0])
    linePoints = []
    bounds = round(0.5*view.width)+1
    for num in range(x-bounds, x+bounds):
        zNum = num/view.zoom
        linePoints.append(toCanvas(zNum, formula.calculate(x=zNum)))

    canvas.create_line(linePoints, fill=formula.color)

def removeFormula(formula:equations.equation):
    """Delete a formula from the formula list and redraw the canvas
    without it.
    """
    formulas.remove(formula)
    canvas.delete("all")
    drawAxes()
    for formula in formulas:
        drawFormula(formula, input=None)
    listFormulas()


def listFormulas():
    """Render the formulas provided as a list in the frame provided."""
    count = 0
    for child in formulaDisplay.winfo_children():
        child.destroy()
    for formula in formulas:
        tkinter.Label(
            formulaDisplay,text="y="+str(formula)[1:-1],
            foreground=formula.color
        ).grid(row=count,column=0, sticky='W')
        tkinter.Button(
            formulaDisplay,text='X',background='red',foreground='white',
            command=partial(removeFormula, formula=formula)
        ).grid(row=count, column=1, padx=5, pady=3)
        count += 1


def drawAxes():
    """Draw the origin axes with labels on the canvas. If the origin
    axes are out of view, place the labels on the side of the canvas
    closest to the respective axis.
    """
    coords = toCanvas(0,0)
    x = coords[0]
    y = coords[1]
    offset_x = floor(x) % view.zoom
    offset_y = floor(y) % view.zoom
    for num in range(0+offset_y, view.height, view.zoom):
        if view.zoom > 3:
            canvas.create_line([0, num], [view.height, num], fill='thistle2')
            canvas.create_line([(x-5, num),(x+5, num)])
        labelY = round(fromCanvas(x,num)[1])
        if labelY % ceil(50/view.zoom) == 0 and labelY != 0:
            canvas.create_text(
                min(max(10,x-12),view.width-10), num, text=labelY
                )
    for num in range(0+offset_x, view.width, view.zoom):
        if view.zoom > 3:
            canvas.create_line([num, 0], [num, view.width], fill='thistle2')
            canvas.create_line([(num, y-5),(num, y+5)])
        labelX = round(fromCanvas(num,y)[0])
        if labelX % ceil(50/view.zoom) == 0 and labelX != 0:
            canvas.create_text(
                num, min(max(10,y-12),view.height-10), text=labelX
                )
    canvas.create_line([x, 0],[x, view.height])
    canvas.create_line([0, y],[view.width, y])

def constructSolutionFrame(event):
    hideSolutionFrame(event)
    x = fromCanvas(event.x, event.y)[0]
    ttk.Label(
        solutionsDisplay,text="x="+str(round(x,7))
    ).grid(row=0,column=0,sticky='NW')
    count = 1
    for formula in formulas:
        solution = formula.getSolution(x=x)
        if solution:
            text = str(formula)[1:-1] + "="
            text += str(round(solution,7))
            solution = ttk.Label(
                solutionsDisplay, text=text, foreground=formula.color
            )
            solution.grid(row=count,column=0,sticky='NW')
            count += 1
    

def hideSolutionFrame(event):
    for child in solutionsDisplay.winfo_children():
        child.destroy()

def dragCanvas(event):
    """Handle the view of the coordinare plane being shifted by a
    click and drag.
    """
    view.drag(event)
    canvas.delete("all")
    drawAxes()
    for formula in formulas:
        drawFormula(formula, input=None)
    listFormulas()

def beginDrag(event):
    """Pass on the beginning of a drag event to the canvas view."""
    view.dragStart(event)

def zoomChange(event):
    """Reduce or increase the zoom level of the canvas."""
    view.zoom += int(event.delta/abs(event.delta))
    if view.zoom < 1:
        view.zoom = 1
    canvas.delete("all")
    drawAxes()
    for formula in formulas:
        drawFormula(formula, input=None)

def addFormula():
    """Add a new formula to the formula list, draw it, and clear the
    input box.
    """
    drawFormula()
    listFormulas()
    formulaInput.delete('1.0',tkinter.END)


tkinter.Button(frm, text="Draw", command=addFormula).grid(column=1,row=1)

drawAxes()

canvas.bind("<B1-Motion>", dragCanvas)
canvas.bind("<Button-1>", beginDrag)
canvas.bind("<MouseWheel>", zoomChange)
canvas.bind("<Enter>", constructSolutionFrame)
canvas.bind("<Motion>", constructSolutionFrame)
canvas.bind("<Leave>", hideSolutionFrame)

root.mainloop()