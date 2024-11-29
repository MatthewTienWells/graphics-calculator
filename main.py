"""Launches a graphing calculator as a windowed application.
Designed and coded by Matthew Tien Wells, 2024.
"""

import tkinter, equations
from tkinter import ttk, Tk

canvasWidth = 500
canvasHeight = 500


def toCanvas(x, y, zoom, width=canvasWidth, height=canvasHeight):
    """Convert x and y coordinates to fit the tkinter canvas system."""
    x *= zoom
    y *= zoom
    x += width/2
    y = height/2 - y
    return (x,y)



root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
canvas = tkinter.Canvas(frm, width=canvasWidth, height=canvasHeight)
canvas.grid(column=0,row=0)

formulaInput = tkinter.Text(frm,height=2)
formulaInput.grid(column=0,row=1)

def drawFormula(input=formulaInput):
    """Draw the provided formula on the canvas. Requires the only
    variable in the equation to be x.
    """
    formulaStr = input.get(1.0, "end-1c")
    formula = equations.equation()
    formula.parse(formulaStr)

    linePoints = []
    for num in range(-50, 50):
        linePoints.append(toCanvas(num, formula.calculate(x=num),10))

    canvas.create_line(linePoints)


canvas.create_line([0,canvasWidth/2],[canvasHeight,canvasWidth/2])
canvas.create_line([canvasHeight/2, 0],[canvasHeight/2,canvasWidth])

tkinter.Button(frm, text="Draw", command=drawFormula).grid(column=1,row=1)


root.mainloop()